#!/usr/bin/env python3

#import serial
import asyncio, json, copy
import datetime
import sys
from collections import Callable
import os



@asyncio.coroutine
def simulator(reader, writer):
	while True:
		data = yield from reader.read(100)
		print('data: ',data.decode())
		ack_received = 'ok\r\n'.encode()
		ack_ready = '{"stat":0}\r\n'.encode()
		writer.write(ack_received)
		yield from writer.drain()
		writer.write(ack_ready)
		yield from writer.drain()




class Output(asyncio.Protocol):


	def __init__(self, outer):
		self.outer = outer
		self._delimiter = "\n"
		self.data_buffer = ""
		self.transport = None
		self.data_last = ""
		self.datum_last = ""


	def connection_made(self, transport):
		print(datetime.datetime.now(),' - Output.connection_made:')
		print('\ttransport: ',transport)
		self.transport = transport
		self.outer.smoothie_transport = transport
		transport.write("M114\r\n".encode())
		loop = asyncio.get_event_loop()
		self.outer._on_connection_made()


	def data_received(self, data):
		#print(datetime.datetime.now(),' - Output.data_received:')
		#print('\tdata: '+str(data))
		self.data_buffer = self.data_buffer + data.decode()
		delimiter_index = self.data_buffer.rfind("\n")
		if delimiter_index >= 0:
			current_data = self.data_buffer[:delimiter_index]
			self.data_buffer = self.data_buffer[delimiter_index+1:]
			data_list = [e+self._delimiter for e in current_data.split(self._delimiter)]
			for datum in data_list:
				if datum != self.datum_last:
					self.datum_last = datum
					self.outer._smoothie_data_handler(datum)
		if data != self.data_last:
			self.data_last = data
			self.outer._on_raw_data(data)


	def connection_lost(self, exc):
		print(datetime.datetime.now(),' - Output.connection_lost:')
		#print('\texc: ',exc)
		self.transport = None
		self.outer.smoothie_transport = None
		self.data_buffer = ""
		loop = asyncio.get_event_loop()
		self.outer._on_connection_lost()
 



class SmoothieDriver(object):
	"""

	How data flows to and from Smoothieboard:

	To:




	From:

	1. Data coming in is split up by delimiter ('\n') and then
	each section is sent to a callback (SmoothieDriver._smoothie_data_handler)
	The raw data is then sent to another callback (SmoothieDriver._raw_data_handler)

	Function: Output.data_received()
	-> _smoothie_data_handler - callback for raw data
	-> _raw_data_handler - callback for chunks of data separated by delimiter

	2. In SmoothieDriver._smoothie_data_handler data is divided between text data and
	JSON data, serial text data formatted for JSON. Either way, the data is then 
	reformatted into a list of standardized dictionary objects with the following format:

	[
		{
		  [MESSAGE]:
			{ 
			  [PARAMETER]:[VALUE],
			  ...
			}
		},
		...
	]

	3. The standard dictionary object is checked for specific flow control data and 
	flow control logic is updated accordingly.

	4. The standard dictionary object is then routed to the appropriate callback based
	on the message


	"""




	def __init__(self, simulate=True):
		"""
		"""
		print(datetime.datetime.now(),' - driver.__init__:')
		#print('\n\targs: ',locals(),'\n')
		self.simulation = simulate
		self.the_loop = asyncio.get_event_loop()
		self.command_queue = []
		self.simulation_queue = []
	
		self.smoothie_transport = None
		self.the_loop = None

		self.current_info = {'session_id':"",'from':""}
		self.connected_info = {'session_id':"",'from':""}
		self.disconnected_info = {'session_id':"",'from':""}

		self.state_dict = {
			'name':'smoothie',
			'simulation':False,
			'connected':False,
			'transport':False,
			'locked':False,
			'ack_received':True,
			'ack_ready':True,
			'queue_size':0,
			'direction':{'X':0,'Y':0,'Z':0,'A':0,'B':0,'C':0},	# 0 = positive, 1 = negative
			'smoothie_pos':{'X':0,'Y':0,'Z':0,'A':0,'B':0,'C':0},
			'adjusted_pos':{'X':0,'Y':0,'Z':0,'A':0,'B':0,'C':0},
			'absolute_mode':True,
			'feedback_on':False
		}

		self.state_dict['simulation'] = simulate

		self.config_dict = {
			'delimiter':"\n",
			'message_ender':"\r\n",
			'ack_received_message':"ok",
			'ack_received_parameter':None,
			'ack_received_value':None,
			'ack_ready_message':"None",
			'ack_ready_parameter':"stat",
			'ack_ready_value':"0",
			'slack':{'X':0.5,'Y':0.5,'Z':0.0,'A':0.1,'B':0.1,'C':0.0}
		}

		self.callbacks_dict = {}
		#  {
		#    <callback_name>:
		#    {
		#      callback: <CALLBACK OBJECT>,
		#      messages: [ <messages>... ]
		#    },
		#    ...
		#  }

		self.meta_callbacks_dict = {
			'on_connect' : None,
			'on_disconnect' : None,
			'on_empty_queue' : None,
			'on_raw_data' : None
		}

		self.commands_dict = {
			"move":{
				"code":"G91 G0",
				"parameters":["","X","Y","Z","A","B"]
			},
			"move_to":{
				"code":"G90 G0",
				"parameters":["","X","Y","Z","A","B"]
			},
			"rapid_linear_move":{
				"code":"G0",
				"parameters":["","X","Y","Z","A","B"]
			},
			"linear_move":{
				"code":"G1",
				"parameters":["","X","Y","Z","A","B"]
			},
			"home":{
				"code":"G28",
				"parameters":["","X","Y","Z","A","B"]
			},
			"absolute":{
				"code":"G90",
				"parameters":[]
			},
			"relative":{
				"code":"G91",
				"parameters":[]
			},
			"speed":{
				"code":"F",
				"parameters":[]
			},
			"speed_a":{
				"code":"a",
				"parameters":[]
			},
			"speed_b":{
				"code":"b",
				"parameters":[]
			},
			"speed_c":{
				"code":"c",
				"parameters":[]
			},
			"enable_motors":{
				"code":"M17",
				"parameters":[]
			},
			"disable_motors":{
				"code":"M18",
				"parameters":[]
			},
			"feedback_on":{
				"code":"M62",
				"parameters":[]
			},
			"feedback_off":{
				"code":"M63",
				"parameters":[]
			},
			"halt":{
				"code":"M112",
				"parameters":[]
			},
			"positions":{
				"code":"M114",
				"parameters":[]
			},
			"limit_switches":{
				"code":"M119",
				"parameters":[]
			},
			"feed_rate":{
				"code":"M198",
				"parameters":["","S","A","B"]
			},
			"seek_rate":{
				"code":"M199",
				"parameters":["","S","A","B"]
			},
			"max_rates":{
				"code":"M203",
				"parameters":["","X","Y","Z","A","B"]
			},
			"acceleration":{
				"code":"M204",
				"parameters":["","S","Z","A","B"]
			},
			"junction":{
				"code":"M205",
				"parameters":["","X","Z","S"]
			},
			"reset":{
				"code":"reset",
				"parameters":[]
			},
			"reset_from_halt":{
				"code":"M999",
				"parameters":[]
			},
			"nothing":{
				"code":"",
				"parameters":["X","Y","Z","A","B","a","b"]
			}
		}


	def callbacks(self):
		"""
		"""
		print(datetime.datetime.now(),' - driver.callbacks')
		return_dict = {}
		for name, value in self.callbacks_dict.items():
			return_dict[name] = value['messages']
		return return_dict
		#return copy.deepcopy(self.callbacks_dict)


	def configs(self):
		"""
		"""
		print(datetime.datetime.now(),' - driver.configs')
		return copy.deepcopy(self.config_dict)


	def set_config(self, config, setting):
		"""
		"""
		print(datetime.datetime.now(),' - driver.set_config:')
		#print('\n\targs: ',locals(),'\n')
		if config in self.config_dict:
			self.config_dict[config] = setting
		return self.configs()


	def meta_callbacks(self):
		"""
		"""
		print(datetime.datetime.now(),' - driver.meta_callbacks')
		return_dict = dict()
		for name, value in self.meta_callbacks_dict.items():
			if value is not None and isinstance(value, Callable):
				return_dict[name] = value.__name__
			else:
				return_dict[name] = 'None'
		# cannot just send back copy becuase NoneObject causes problem
		#return copy.deepcopy(self.meta_callbacks_dict)
		return return_dict


	def set_meta_callback(self, name, callback):
		"""
		name should correspond 
		"""
		print(datetime.datetime.now(),' - driver.set_meta_callback:')
		#print('\n\targs: ',locals(),'\n')
		if name in self.meta_callbacks_dict and isinstance(callback, Callable):
			self.meta_callbacks_dict[name] = callback
		else:
			return '{error:name not in meta_callbacks or callback is not Callable}'
		return self.meta_callbacks()


	def add_callback(self, callback, messages):
		"""
		"""
		print(datetime.datetime.now(),' - driver.add_callback:')
		#print('\n\targs: ',locals(),'\n')
		if callback.__name__ not in list(self.callbacks_dict):
			if isinstance(messages, list):
				self.callbacks_dict[callback.__name__] = {'callback':callback, 'messages':messages}
			else:
				self.callbacks_dict[callback.__name__] = {'callback':callback, 'messages':[messages]}
		elif message not in self.callbacks_dict[callback.__name__]['messages']:
			if isinstance(messages, list):
				self.callbacks_dict[callback.__name__]['messages'].extend(messages)
			else:
				self.callbacks_dict[callback.__name__]['messages'].append(messages)
		return self.callbacks()


	def remove_callback(self, callback_name):
		"""
		"""
		print(datetime.datetime.now(),' - driver.remove_callback')
		#print('\n\targs: ',locals(),'\n')
		del self.callbacks_dict[callback_name]
		return self.callbacks()


	def flow(self):
		"""
		"""
		print(datetime.datetime.now(),' - driver.flow')
		return copy.deepcopy(self.state_dict)


	def clear_queue(self):
		"""
		"""
		print(datetime.datetime.now(),' - driver.clear_queue')
		self.command_queue = []
		self.state_dict['queue_size'] = len(self.command_queue)
		self.state_dict['ack_received'] = True
		self.state_dict['ack_ready'] = True
		return self.flow()

	
	def connect(self, from_, session_id, device=None, port=None):
		"""
		"""
		print(datetime.datetime.now(),' - driver.connect called:')
		#print('\n\targs: ',locals(),'\n')
		self.connected_info = {'from':from_,'session_id':session_id}
		self.the_loop = asyncio.get_event_loop()
		#asyncio.async(serial.aio.create_serial_connection(self.the_loop, Output, '/dev/ttyUSB0', baudrate=115200))
		callbacker = Output(self)
		try:
			if self.the_loop.is_running():
				self.the_loop.stop()
			print(self.simulation)
			if self.simulation:
				print(simulator)
				server = self.the_loop.run_until_complete(asyncio.start_server(simulator,'0.0.0.0',3334))
				self.the_loop.run_until_complete(self.the_loop.create_connection(lambda: callbacker, host='0.0.0.0', port=3334))
				
				#yield from server.wait_closed()
			else:
				smoothie_host=os.environ.get('SMOOTHIE_HOST', '0.0.0.0')
				smoothie_port=int(os.environ.get('SMOOTHIE_PORT', '3333'))
				asyncio.async(self.the_loop.create_connection(
					lambda: callbacker,
					host=smoothie_host,
					port=smoothie_port))
		except:
			print(datetime.datetime.now(),' - error:driver.connects\n\r',sys.exc_info())
			

	def disconnect(self, from_, session_id):
		"""
		"""
		print(datetime.datetime.now(),' - driver.disconnect')
		#print('\n\targs: ',locals(),'\n')
		self.disconnected_info = {'from':from_,'session_id':session_id}
		self.smoothie_transport.close()


	def commands(self):
		"""
		"""
		print(datetime.datetime.now(),' - driver.commands')
		return copy.deepcopy(self.commands_dict)


	def unlock(self):
		"""
		"""
		print(datetime.datetime.now(),' - driver.unlock')
		self.state_dict['ack_received'] = True
		self.state_dict['ack_ready'] = True
		self.lock_check()


	def send(self, message):
		print(datetime.datetime.now(),' - driver.send:')
		#print('\n\targs: ',locals(),'\n')
		self.state_dict['queue_size'] = len(self.command_queue)
		command = message['command'] + self.config_dict['message_ender']

		if self.simulation:
			self.simulation_queue.append(message)
		
		if self.smoothie_transport is not None:
			print(datetime.datetime.now(),' - smoothie_transport not None')
			#if self.lock_check() == False:
			# should have already been checked
			self.state_dict['ack_received'] = False
			self.state_dict['ack_ready'] = False  # needs to be set here because not ready message from device takes too long, ack_received already received
			if command.startswith('M62'):
				self.state_dict['feedback_on'] = True
			elif command.startswith('M63'):
				self.state_dict['feedback_on'] = False
		    
			if command.startswith('G90'):
		    	self.state_dict['absolute_mode'] = True
			if command.startswith('G91'):
				self.state_dict['absolute_mode'] = False
			self.lock_check()
			self.current_info = {'session_id':message['session_id'],'from':message['from']}
			self.smoothie_transport.write(command.encode())
			#self.smoothie_streamwriter.drain()
		else:
			print(datetime.datetime.now(),' - smoothie_transport is None????')



# flow control 

	def lock_check(self):
		print(datetime.datetime.now(),' - driver.lock_check')
		#print("SmoothieDriver.lock check called")
		print('\tack_received: ',self.state_dict['ack_received'])
		print('\tack_ready: ',self.state_dict['ack_ready'])
		print('\tfeedback_on: ',self.state_dict['feedback_on'])
		if self.state_dict['ack_received'] == True:
			if self.state_dict['feedback_on'] == True:
				if self.state_dict['ack_ready'] == True:
					self.state_dict['locked'] = False
					print('\tunlocked - 1')
					return False
				else:
					self.state_dict['locked'] = True
					print('\tlocked - 1')
					return True
			else:
				self.state_dict['locked'] = False
				print('\tunlocked - 2')
			return False
		else:
			self.state_dict['locked'] = True
			print('\tlocked - 2')
			return True


	def _add_to_command_queue(self, from_, session_id, command):
		print(datetime.datetime.now(),' - driver._add_to_command_queue:')
		#print('\n\targs: ',locals(),'\n')
		cmd = {'session_id':session_id,'from':from_,'command':command}
		self.command_queue.append(cmd)
		self.state_dict['queue_size'] = len(self.command_queue)
		self._step_command_queue()


	def _step_command_queue(self):
		print(datetime.datetime.now(),' - driver._step_command_queue')
		self.lock_check()
		if self.state_dict['locked'] == False:
			if len(self.command_queue) == 0:
				if isinstance(self.meta_callbacks_dict['on_empty_queue'],Callable):
					self.meta_callbacks_dict['on_empty_queue'](self.current_info['from'],self.current_info['session_id'])
			else:
				self.send(self.command_queue.pop(0))



	def _format_text_data(self, text_data):
		print(datetime.datetime.now(),' - driver._format_text_data:')
		#print('\n\targs: ',locals(),'\n')
		return_list = []
		remainder_data = text_data
		while remainder_data.find(',')>=0:
			stupid_dict = self._format_group( remainder_data[:remainder_data.find(',')] ) 
			return_list.append(stupid_dict)
			remainder_data = remainder_data[remainder_data.find(',')+1:]
		stupid_dict = self._format_group( remainder_data )
		return_list.append(stupid_dict)
		return return_list


	def _format_group(self, group_data):
		print(datetime.datetime.now(),' - driver._format_group:')
		#print('\n\targs: ',locals(),'\n')
		return_dict = dict()
		remainder_data = group_data
		if remainder_data.find(':')>=0:
			while remainder_data.find(':')>=0:
				message = remainder_data[:remainder_data.find(':')].replace('\n','').replace('\r','')
				remainder_data = remainder_data[remainder_data.find(':')+1:]
				if remainder_data.find(' ')>=0:
					parameter = remainder_data[:remainder_data.find(' ')].replace('\n','').replace('\r','')
					remainder_data = remainder_data[remainder_data.find(' ')+1:]
				else:
					parameter = remainder_data.replace('\r','').replace('\n','')
					return_dict[message] = parameter
		else:
			return_dict[group_data.strip()] = ''
		return return_dict


	def _format_json_data(self, json_data):

		#
		#	{ 
		#		name : value,
		#		... ,
		#		name : { ... }???
		#	}
		#
		#
		print(datetime.datetime.now(),' - driver._format_json_data:')
		#print('\n\targs: ',locals(),'\n')
		return_list = []
		for name, value in json_data.items():
			if isinstance(value, dict):
				message = name
				for value_name, value_value in value.items():
					parameter = value_name
					this_dict = {}
					this_dict[message] = {}
					this_dict[message][parameter] = value_value
					return_list.append(this_dict)
			else:
				message = 'None'
				parameter = name
				this_dict = {}
				this_dict[message] = {}
				this_dict[message][parameter] = value
				return_list.append(this_dict)
		#
		#	so, if json_data looks like:
		#	{ X:<f>, Y:<f>, Z:<f>, A:<f>, B:<f> }
		#
		#	it gets turned into:
		#	[ 
		#	  {  'None':
		#			{ X:<f>, Y:<f>, Z:<f>, A:<f>, B:<f> } 
		#	  } 
		#	]
		#
		return return_list


	def _process_message_dict(self, message_dict):
		print(datetime.datetime.now(),' - driver._process_message_dict:')
		#print('\n\targs: ',locals(),'\n')

		# First, pass messages to their respective callbacks based on callbacks and messages they're registered to receive
		#
		# this is done first to keep _step_command_queue() being called elsewhere from screwing up from_ and 
		# session_id before being done with them
		# eg:
		#
		#	message dict:
		#	{ 'None':
		#		{ X:<f>, Y:<f>, Z:<f>, A:<f>, B:<f> } 
		#	}
		#
		#	---->  name_message = 'None'
		#	---->  value = { X:<f>, Y:<f>, Z:<f>, A:<f>, B:<f> } 
		#
		#
		for name_message, value in message_dict.items():
			if name_message == 'None':
				axis_found = False
				for axis in list(self.state_dict['smoothie_pos']):
					if axis in value:
						axis_found = True
						self.state_dict['smoothie_pos'][axis] = value[axis]
						if self.state_dict['direction'][axis] == 1:
							self.state_dict['adjusted_pos'][axis] = value[axis]
						else:
							self.state_dict['adjusted_pos'][axis] = value[axis] + self.config_dict['slack'][axis]

				if axis_found == True:
					pos_dict = {'pos':copy.deepcopy(self.state_dict['smoothie_pos'])}
					adj_pos_dict = {'adj_pos':copy.deepcopy(self.state_dict['adjusted_pos'])}
					for callback_name, callback in self.callbacks_dict.items():
						if 'smoothie_pos' in callback['messages']:
							callback['callback'](self.state_dict['name'], self.current_info['from'], self.current_info['session_id'], pos_dict)
						if 'adjusted_pos' in callback['messages']:
							callback['callback'](self.state_dict['name'], self.current_info['from'], self.current_info['session_id'], adj_pos_dict)
				

			for callback_name, callback in self.callbacks_dict.items():
				if name_message in callback['messages']:
					callback['callback'](self.state_dict['name'], self.current_info['from'], self.current_info['session_id'], value)
				





		# second, check if ack_received confirmation
		if self.config_dict['ack_received_message'] in list(message_dict) or self.config_dict['ack_received_message'] is None:
			value = message_dict.get(self.config_dict['ack_received_message'])
			if isinstance(value, dict):
				if self.config_dict['ack_receieved_parameter'] is None:
					self.state_dict['ack_received'] = True
				else:
					for value_name, value_value in value.items():
						if value_name == self.config_dict['ack_received_parameter']:
							if self.config_dict['ack_received_value'] is None or value_value == self.config_dict['ack_receieved_value']:
								self.state_dict['ack_received'] = True
			else:
				if self.config_dict['ack_received_parameter'] is None:
					if self.config_dict['ack_received_value'] is None or value == self.config_dict['ack_received_value']:
						self.state_dict['ack_received'] = True


		# third, check if ack_ready confirmation
		if self.config_dict['ack_ready_message'] in list(message_dict) or self.config_dict['ack_ready_message'] is None:
			value = message_dict.get(self.config_dict['ack_ready_message'])
			if isinstance(value, dict):
				if self.config_dict['ack_ready_parameter'] is None:
					self.state_dict['ack_ready'] = True
				else:
					for value_name, value_value in value.items():
						if value_name == self.config_dict['ack_ready_parameter']:
							if self.config_dict['ack_ready_value'] is None or str(value_value) == str(self.config_dict['ack_ready_value']):
								self.state_dict['ack_ready'] = True
							else:
								self.state_dict['ack_ready'] = False
			else:
				if self.config_dict['ack_ready_parameter'] is None:
					if self.config_dict['ack_ready_value'] is None or value == self.config_dict['ack_ready_value']:
						self.state_dict['ack_ready'] = True
					else:
						self.state_dict['ack_ready'] = False
				else:
					if value == self.config_dict['ack_ready_parameter']:
						self.state_dict['ack_ready'] = True
					else:
						self.state_dict['ack_ready'] = False					

		self._step_command_queue()


# Device callbacks
	def _on_connection_made(self):
		print(datetime.datetime.now(),' - driver._on_connection_made')
		self.state_dict['connected'] = True
		self.state_dict['transport'] = True if self.smoothie_transport else False
		print('*\t*\t* connected!\t*\t*\t*')
		if isinstance(self.meta_callbacks_dict['on_connect'],Callable):
			self.meta_callbacks_dict['on_connect'](self.connected_info['from'],self.connected_info['session_id'])


	def _on_raw_data(self, data):
		print(datetime.datetime.now(),' - driver._on_raw_data:')
		#print('\n\targs: ',locals(),'\n')
		if isinstance(self.meta_callbacks_dict['on_raw_data'],Callable):
			self.meta_callbacks_dict['on_raw_data'](self.current_info['from'],self.current_info['session_id'],data)


	def _smoothie_data_handler(self, datum):
		"""Handles incoming data from Smoothieboard that has already been split by delimiter
		"""
		print(datetime.datetime.now(),' - driver._smoothie_data_handler:')
		print('\n\targs: ',locals(),'\n')
		json_data = ""
		text_data = ""

		if isinstance(datum,dict):
			json_data = json.dumps(datum)
		else:
			str_datum = str(datum)
			text_data = str_datum

			if self.config_dict['ack_received_message'] in str_datum:
				self.ack_received = True

			if str_datum.find('{')>=0:
				json_data = str_datum[str_datum.find('{'):].replace('\n','').replace('\r','')
				text_data = str_datum[:str_datum.index('{')]

		if text_data != "":
			print('\ttext_data: ',text_data)
			text_message_list = self._format_text_data(text_data)
			
			for message in text_message_list:
				self._process_message_dict(message)

		if json_data != "":
			print('\tjson_data: ',json_data)
			try:
				json_data_dict = json.loads(json_data)
				json_message_list = self._format_json_data(json_data_dict)
				for message in json_message_list:
					self._process_message_dict(message)
			except:
				print(datetime.datetime.now(),' - {error:driver._smoothie_data_handler - json.loads(json_data)}\n\r',sys.exc_info())


	def _on_connection_lost(self):
		print(datetime.datetime.now(),' - driver._on_connection_lost')
		self.state_dict['connected'] = False
		self.state_dict['transport'] = True if self.smoothie_transport else False
		print('*\t*\t* not connected!\t*\t*\t*')
		if isinstance(self.meta_callbacks_dict['on_disconnect'],Callable):
			self.meta_callbacks_dict['on_disconnect'](self.disconnected_info['from'],self.disconnected_info['session_id'])


	def _adjust_positions(self, command_text, val, param):
		if command_text.startswith("G90"):					
			print('(1)')
			print(val)
			float_val = float(val)
			print(float_val)
			if float_val > self.state_dict['smoothie_pos'][param] and self.state_dict['direction'][param]==0:
				print('(2)')
				self.state_dict['direction'][param] = 1
				float_val+=self.config_dict['slack'][param]
			if float_val < self.state_dict['smoothie_pos'][param] and self.state_dict['direction'][param]==1:
				print('(3)')
				self.config_dict['direction'][param] = 0
				float_val-=self.config_dict['slack'][param]
				val = str(float_val)

		if command_text.startswith("G91"):

			float_val = float(val)
			if float_val > 0 and self.state_dict['direction'][param]==0:
				self.state_dict['direction'][param] = 1
				float_val+=self.config_dict['slack'][param]
			if float_val < 0 and self.state_dict['direction'][param]==1:
				self.state_dict['direction'][param] = 0
				float_val-=self.config_dict['slack'][param]
				val = str(float_val)

		return val


	def send_command(self, from_, session_id, data):
		"""

		data should be in one of 2 forms:

		1. string

		If there is additional information to go with the command, then it should
		be in JSON format. We're not going to parse the string to try to get additional
		values to go with the command

		2. {command:params}
			params --> {param1:value, ... , paramN:value}

		"""
		print(datetime.datetime.now(),' - driver.send_command:')
		#print('\n\targs: ',locals(),'\n')
		command_text = ""

		# data in form 1
		if isinstance(data, dict):
			command = list(data)[0]
		# data in form 2
		elif isinstance(data, str):
			command = data
		
		# check if command is in commands dictionary
		if command in list(self.commands_dict):
			command_text = self.commands_dict[command]["code"]
			print('command_text: ',command_text)
			if isinstance(data, dict):
				#print('data is dict')
				if isinstance(data[command], dict):
					#print('data[',command,'] is dict')
					for param, val in data[command].items():
						if param in self.commands_dict[command]["parameters"]:
							if param in list(self.state_dict['smoothie_pos']):

								val = self._adjust_positions(command_text, val, param)

							command_text += " "
							command_text += str(param)
							command_text += str(val)
			
			self._add_to_command_queue(from_ ,session_id, command_text)

		else:	#check whether command is actually a code in commands dictionary
			for cmd, dat in self.commands_dict.items():
				if command == dat.get("code"):
					# command is actually a code in the commands dictionary
					command_text = command
					if isinstance(data,dict):
						if isinstance(data[command], dict):
							for param, val in data[command].items():
								if param in val.parameters:
									if param in self.state_dict['smoothie_pos']:
										
										val = self._adjust_positions(command_text, val)

									command_text += " "
									command_text += str(param)
									command_text += str(val)

					self._add_to_command_queue(from_, session_id, command_text)
					break

		#else:
		#	print("command is NOT in list!")




if __name__ == '__main__':
	smooth = OTOneDriver()
	run_called = False


	def runner():
		smooth.connect()
		print()
		print("smooth.get_just_commands:")
		print(smooth.get_just_commands())
		print()
		print("-"*10)
		print()

		loop = asyncio.get_event_loop()
		loop.call_later(4, run_commands)
		loop.run_forever()


	def run_commands():
		#i = 0
		#for command in smooth.get_just_commands():
		#	i = i+1
		#	if i < 2:
		#		print()
		#		print("command to send:")
		#		print(command)
		#		print()
		print()
		cmd = input("enter a command:\n")
		if cmd == "clear":
			smooth.clear_queue()
		if cmd == "unlock":
			smooth.unlock()
		if cmd == "help" or cmd == "h":
			print()
			print("possible commands:")
			print("-"*10)
			print("clear")
			print("help")
			print("-"*10)
			print(smooth.get_just_commands())
		else:
			smooth.send_command(cmd)
		#command
		loop = asyncio.get_event_loop()
		loop.call_later(2, run_commands)


	def check_run_called():
		if run_called == False:
			run_commands()


	try:
		loop = asyncio.get_event_loop()
		loop.run_until_complete(runner())

		#loop.run_forever()
	finally:
		pass
		#loop.close()













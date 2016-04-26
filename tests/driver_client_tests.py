import unittest, os, json

from driver.driver_client import DriverClient
from driver.smoothie_driver import SmoothieDriver

order = 0

class DriverClientTest(unittest.TestCase):

	
	def setUp(self):
		self.driver_client = DriverClient()
		self.smoothie_driver = SmoothieDriver(simulate=True)
		self.driver_client.add_driver(self.driver_client.id,'','smoothie',self.smoothie_driver)


	#def test_add_driver(self):
		#self.smoothie_driver = SmoothieDriver(simulate=(os.environ.get('SMOOTHIE_SIMULATE', 'true')=='true'))
		#self.driver_client.add_driver(self.driver_client.id,'','smoothie',self.smoothie_driver)



	#meta callbacks
	def on_connect(from_,session_id):
		self.driver_client.publish(from_,from_,session_id,'connect','driver','result','connected')

	def on_disconnect(from_,session_id):
		self.driver_client.publish(from_,from_,session_id,'connect','driver','result','disconnected')

	def on_empty_queue(from_,session_id):
		self.driver_client.publish(from_,from_,session_id,'queue','driver','result','empty')

	def on_raw_data(from_,session_id,data):
		self.driver_client.publish(from_,from_,session_id,'raw','driver','data',data)


	#callbacks
	def none(name, from_, session_id, data_dict):
		dd_name = list(data_dict)[0]
		dd_value = data_dict[dd_name]
		self.driver_client.publish('frontend',from_,session_id,'driver',name,list(data_dict)[0],dd_value)
		if from_ != session_id:
			self.driver_client.publish(from_,from_,session_id,'driver',name,list(data_dict)[0],dd_value)

	def positions(name, from_, session_id, data_dict):
		dd_name = list(data_dict)[0]
		dd_value = data_dict[dd_name]
		self.driver_client.publish('frontend',from_,session_id,'driver',name,list(data_dict)[0],dd_value)
		if from_ != session_id:
			self.driver_client.publish(from_,from_,session_id,'driver',name,list(data_dict)[0],dd_value)

	def adjusted_pos(name, from_, session_id, data_dict):
		dd_name = list(data_dict)[0]
		dd_value = data_dict[dd_name]
		self.driver_client.publish('frontend',from_,session_id,'driver',name,list(data_dict)[0],dd_value)
		if from_ != session_id:
			self.driver_client.publish(from_,from_,session_id,'driver',name,list(data_dict)[0],dd_value)

	def smoothie_pos(name, from_, session_id, data_dict):
		dd_name = list(data_dict)[0]
		dd_value = data_dict[dd_name]
		self.driver_client.publish('frontend',from_,session_id,'driver',name,list(data_dict)[0],dd_value)
		if from_ != session_id:
			self.driver_client.publish(from_,from_,session_id,'driver',name,list(data_dict)[0],dd_value)

	def dummy_callback(name, from_, session_id, data_dict):
		dd_name = list(data_dict)[0]
		dd_value = data_dict[dd_name]
		self.driver_client.publish('dummy',from_,session_id,'dummy',name,list(data_dict)[0],dd_value)
		if from_ != session_id:
			self.driver_client.publish(from_,from_,session_id,'driver',name,list(data_dict)[0],dd_value)

	callbacks = [none, positions, adjusted_pos, smoothie_pos, dummy_callback]

	meta_callbacks = [on_connect, on_disconnect, on_empty_queue, on_raw_data]

	handshakes = [
		# handshakes to test
	]




	def test_add_and_remove_callbacks(self):	# 1
		"""
		Add and remove callbacks.
		"""
		global order
		order+=1
		print()
		print('TEST_ADD_AND_REMOVE_CALLBACKS: '+str(order))
		print()
		#ADD
		self.driver_client.add_callback(self.driver_client.id,'','smoothie', {self.none:['None']})
		self.driver_client.add_callback(self.driver_client.id,'','smoothie', {self.positions:['M114']})
		self.driver_client.add_callback(self.driver_client.id,'','smoothie', {self.adjusted_pos:['adjusted_pos']})
		self.driver_client.add_callback(self.driver_client.id,'','smoothie', {self.smoothie_pos:['smoothie_pos']})
		self.driver_client.add_callback(self.driver_client.id,'','smoothie', {self.dummy_callback:['None']})
		#REMOVE
		self.driver_client.remove_callback(self.driver_client.id,'','smoothie', 'dummy_callback')
		print()
		print()
		print()
		print()


	def test_set_meta_callbacks(self):	# 6
		global order
		order+=1
		print()
		print('TEST_SET_META_CALLBACKS: '+str(order))
		print()
		self.driver_client.set_meta_callback(self.driver_client.id,'','smoothie',{'on_connect':self.on_connect})
		self.driver_client.set_meta_callback(self.driver_client.id,'','smoothie',{'on_disconnect':self.on_disconnect})
		self.driver_client.set_meta_callback(self.driver_client.id,'','smoothie',{'on_empty_queue':self.on_empty_queue})
		self.driver_client.set_meta_callback(self.driver_client.id,'','smoothie',{'on_raw_data':self.on_raw_data})
		print()
		print()
		print()
		print()


	def test_driver_connect(self):	# 4
		global order
		order+=1
		print()
		print('TEST_DRIVER_CONNECT: '+str(order))
		print()
		result = self.driver_client.driver_connect(self.driver_client.id,'','smoothie',None)
		expected = ''
		self.assertEqual(expected, result)
		print()
		print()
		print()
		print()


	def test_driver_client_connect(self):	# 3
		global order
		order+=1
		print()
		print('TEST_DRIVER_CLIENT_CONNECT: '+str(order))
		print()
		self.driver_client.connect(
			url_domain=os.environ.get('CROSSBAR_HOST', '0.0.0.0'),
			url_port=int(os.environ.get('CROSSBAR_PORT', '8080'))
			)
		print()
		print()
		print()
		print()


	def test_handshakes(self):	# 5
		global order
		order+=1
		print()
		print('TEST_HANDSHAKES: '+str(order))
		print()
		# test handshakes in handshakes list
		for handshake in self.handshakes:
			self.driver_client.handshake(handshake)
		print()
		print()
		print()
		print()


	def test_all_meta_commands(self):	# 2
		global order
		order+=1
		print()
		print('TEST_ALL_META_COMMANDS: '+str(order))
		print()
		print(list(self.driver_client.meta_dict))
		for me in list(self.driver_client.meta_dict):
			print(me)

		for meta_element in list(self.driver_client.meta_dict):
			if meta_element != 'add_driver':
				print('+'*20)
				message_dict = {"type":"meta", "from":"", "sessionID":"abc123", "data": { "name":"smoothie", "message":str(meta_element)} }
				print(message_dict)
				message = json.dumps(message_dict)
				print(message)
				self.driver_client.dispatch_message(message)
				print()
				print()
				print('*'*20)
		print('wtf')
		print()
		print()
		print()
		print()


	#def tearDown(self):
		#self.driver_client.dispose()


if __name__ == '__main__':
	unittest.main()

















#!/usr/bin/env python3
import asyncio
import copy
import json
import uuid
import datetime

"""
TODO:
- Tests
- Exceptions
- Logging

"""

class Output(asyncio.Protocol):

    def __init__(self, outer):
        self._outer = outer
        if hasattr(outer,'loop'):
            self._loop = outer.loop
        else:
            self._loop = asyncio.get_event_loop()
        self._delimiter = "\n"
        self._data_remainder = ""
        self._data_list = []
        self._transport = None
        self._data_last = ""
        self._datum_last = ""

    # Continuously try to pop data from data_list and send to OUTER
    # 
    @asyncio.coroutine
    def _continuous_data_list_process(self):
        yield from self._data_list_processor()
        self._loop.create_task(self._continuous_data_list_process())

    @asyncio.coroutine
    def _data_list_processor(self):
        while len(self._data_list) > 0:
            data_to_send = self._data_list.pop(0)
            self._outer._on_data_handler(data_to_send)

    def connection_made(self, transport):
        self._transport = transport
        self._outer._transport = transport
        self._outer._on_connection_made_handler()
        self._loop.create_task(self._continuous_data_list_process())

    def data_received(self, data):
        """ First pass at normalizing raw data coming from motor-controller

            Output format is either text or JSON and fed to _data_handler and _on_raw_data
        """
        decoded_data = data.decode()
        self._buff_data(decoded_data)
        self._outer._on_raw_data_handler(decoded_data)

    def _buff_data(self, data):
        """ Processes data into _data_list"""
        self._data_remainder = self._data_remainder + data
        delimiter_index = self._data_remainder.rfind(self._delimiter)
        while delimiter_index > 0: # >=?
            current_data = self._data_remainder[:delimiter_index]
            self._data_remainder = self._data_remainder[delimiter_index+1:]
            self._data_list.append(current_data)
            delimiter_index = self._data_remainder.rfind(self._delimiter)

    def connection_lost(self, exc):
        self._transport = None
        if self._outer._transport is not None:
            self._outer._transport = None
        self._data_remainder = ""
        self.outer._on_connection_lost_handler()


class MotorController(object):

    """
    This object outputs raw GCode and other motor-controller specific commands
    """
# CLASS VARIABLES
    MOVE = "G91 G0"
    MOVE_TO = "G90 G0"
    RAPID_LINEAR_MOVE = "G1"
    LINEAR_MOVE = "G0"
    HOME = "G28"
    ABSOLUTE = "G90"
    RELATIVE = "G91"
    SPEED = "F"
    SPEED_A = "a"
    SPEED_B = "b"
    SPEED_C = "c"
    ENABLE_MOTORS = "M17"
    DISABLE_MOTORS = "M18"
    FEEDBACK_ON = "M62"
    FEEDBACK_OFF = "M63"
    HALT = "M112"
    POSITIONS = "M114"
    LIMIT_SWITCHES = "M119"
    FEED_RATE = "M198"
    SEEK_RATE = "M199"
    MAX_RATES = "M203"
    ACCELERATION = "M204"
    JUNCTION = "M205"
    RESET = "reset"
    RESET_FROM_HALT = "M999"


    def __init__(self, loop=None, simulate=False):

        if loop:
            self._loop = loop
        else:
            self._loop = asyncio.get_event_loop()

        # list of commands, commands are dictionaries with format:
        #   { SESSION_ID, WHERE_FROM, CODE, ARGS }
        self._cmd_q = CommandQueue()
    
        # hold Output protocol object for tcp communication with network connection to moto-controller
        self._output = None

        # hold transport object from Output protocol
        self._transport = None

        # Grouped all the "state" variables together
        self._state_dict = {
            'name':'smoothie',
            'simulation':False,
            'connected':False,
            'transport':False,
            'locked':False,
            'ack_received':True,
            'ack_ready':True,
            'queue_size':0,
            'direction':{'X':0,'Y':0,'Z':0,'A':0,'B':0,'C':0},  # 0 = positive, 1 = negative
            'reported_pos':{'X':0.0,'Y':0.0,'Z':0.0,'A':0.0,'B':0.0,'C':0.0},
            'actual_pos':{'X':0.0,'Y':0.0,'Z':0.0,'A':0.0,'B':0.0,'C':0.0},
            'error':{'X':0.0,'Y':0.0,'Z':0.0,'A':0.0,'B':0.0,'C':0.0},
            'absolute_mode':True,
            'feedback_on':False,
            'current_command_session_id':'default',
            'current_command_where_from':'default',
            'connected_session_id':'default',
            'disconnected_session_id':'default'
        }

        self._state_dict['simulation'] = simulate


        # IGNORING BEING ABLE TO EDIT THIS FROM API INTENTIONALLY FOR NOW
        # Grouped all the "config" variables together
        self._config_dict = {
            'delimiter':"\n",
            'message_ender':"\r\n",
            'ack_received_message':"ok",
            'ack_received_parameter':None,
            'ack_received_value':None,
            'ack_ready_message':"None",
            'ack_ready_parameter':"stat",
            'ack_ready_value':"0",
            'slack':{'X':0.5,'Y':0.5,'Z':0.0,'A':0.1,'B':0.1,'C':0.0},
            'timeout':5
        }

        # callbacks
        self._on_raw_data = None
        self._on_data = None
        self._on_empty_queue = None
        self._on_connection_made = None
        self._on_connection_lost = None

        self.test_command_list = []

        self._timeout_handler = None

        self._move_list = [self.ABSOLUTE, self.RELATIVE, self.MOVE, self.MOVE_TO, self.LINEAR_MOVE, self.RAPID_LINEAR_MOVE]

# PRIVATE
    def _adjust_positions_send(self, code, **kwargs):
        """
        Adjust command positions for slack errors. Save the errors in state variables
        so the positions can be adjusted as received from motorcontroller. Also adjusts 
        direction state variables


        errors always correspond to going from motorcontroller reported position to
        actual position ( reported position + error = actual position )

        """
        pos = {}
        for k,v in kwargs.items():
            K = k.upper()

            # CHECK WHETHER KEY IS POSITION THAT MIGHT REQUIRE ADJUSTMENT and IT'S A MOVEMENT
            if K in self._state_dict['actual_pos'] and code in self._move_list:

                # ABSOLUTE MODE
                if self._state_dict['absolute_mode'] == True:

                    aim_v_float = float(v)

                    # SWIT NEG
                    if aim_v_float < self._state_dict['actual_pos'][K] and self._state_dict['direction']==0:
                        
                        # update direction to negative
                        self._state_dict['direction'][K] = 1

                        # update position aimed at
                        aim_v_float-=self._config_dict['slack'][K]

                        # update error from reported to actual position
                        self._state_dict['error'][K] = self._config_dict['slack'][K]

                    # SWIT POS
                    elif aim_v_float > self._state_dict['actual_pos'][K] and self._state_dict['direction']==1:
                        
                        # update direction to positive
                        self._state_dict['direction'][K] = 0

                        # update position aimed at
                        aim_v_float+=self._config_dict['slack'][K]

                        # update error from reported to actual position
                        self._state_dict['error'][K] = -self._config_dict['slack'][K]

                    elif self._state_dict['direction']==1:
                        # update position aimed at
                        aim_v_float-=self._state_dict['slack'][K]

                    pos[K] = str(aim_v_float)

                # RELATIVE
                elif self._state_dict['absolute_mode'] == False:

                    aim_distance_v_float = float(v)
                    
                    
                    # SWIT NEG
                    if aim_distance_v_float < 0 and self._state_dict['direction'][K]==0:
                        
                        # update direction to negative
                        self._state_dict['direction'][K] = 0
                        
                        # update distance aimed for
                        aim_distance_v_float -= self._state_dict['slack'][K]

                        # update error for reported to actual position
                        self._state_dict['error'][K]+=self._state_dict['slack'][K]
                    
                    # SWIT POS
                    if aim_distance_v_float > 0 and self._state_dict['direction'][K]==1:
                        
                        # update direction to positive
                        self._state_dict['direction'][k] = 0
                        
                        # update distance aimed for
                        aim_distance_v_float += self._state_dict['slack'][K]

                        # update error for reported to actual position
                        self._state_dict['error'][K]-=self._state_dict['slack'][K]
                    
                    pos[K] = str(aim_distance_v_float)
                
                # ELSE SEND THROUGH WHATEVER IS THERE
                else:
                    pos[k] = str(v)
            # DOES NOT REQUIRE ADJUSTMENT, SEND IT THROUGH
            else:
                pos[k] = str(v)

        return pos

    def _send(self, session_id=None, where_from=None, code=None, **kwargs):
        """ Sends command to motorcontroller

            Last point of contact with data before it goes out to motor-controller, so 
            a number of state variables are dealt with here, eg:
                flow control variables
                adjustments for slack errors
        """
        self._state_dict['queue_size'] = self._cmd_q.size
        if session_id and where_from:
            
            # SETTING VARIABLES INVOLVED WITH FLOW CONTROL
            self._state_dict['ack_received'] = False
            self._state_dict['ack_ready'] = False
            if code == self.FEEDBACK_ON:
                self._state_dict['feedback_on'] = True
            elif code == self.FEEDBACK_OFF:
                self._state_dict['feedback_on'] = False

            # SET LOCK

            # SETTING ABSOLUTE MODE VERSUS RELATIVE MODE
            if code==self.ABSOLUTE or code==self.MOVE_TO:
                self._state_dict['absolute_mode'] = True
            if code==self.RELATIVE or code==self.MOVE:
                self._state_dict['absolute_mode'] = False
            
            # MAKE ADJUSTMENTS FOR SLACK
            pos = self._adjust_positions_send(code, **kwargs)

            args = []
            for k,v in pos.items():
                args.append("{}{}".format(k,v))
            if len(args)>0:
                if code:
                    command = code+" "+' '.join(args)+self._config_dict['message_ender']
                else:
                    command = ' '.join(args)+self._config_dict['message_ender']
            else:
                command = code + self._config_dict['message_ender']
            self._state_dict['current_command_session_id'] = session_id
            self._state_dict['current_command_where_from'] = where_from
            if self._state_dict['simulation'] == True:
                self.test_command_list.append(command)
            else:
                if self._transport is not None:
                    self._timeout_handler = self._loop.call_later(self._config_dict['timeout'],self._on_timeout_handler())
                    self._transport.write(command.encode())
                else:
                    pass
                # log
        else:
            pass
            # log - no session_id or where_from


    def _send_command(self, session_id=None, where_from=None, code='', **kwargs):
        """ Adds command to COMMAND QUEUE and then tries to step command queue
        """
        if session_id is not None and where_from is not None:
            cmd = {'session_id':session_id, 'code':code, 'where_from':where_from, 'args':kwargs}
            self._cmd_q.add_command(cmd)
            self._try_send()

    def _try_send(self):
        """ Try to get the next command from the command queue and 
            if successful, send it
        """
        next_cmd = self._cmd_q.next()
        if next_cmd is not None:
            self._send( session_id=next_cmd['session_id'], \
                        where_from=next_cmd['where_from'], \
                        code=next_cmd['code'], \
                        **next_cmd['args']
                        )

    # parse text data received from motor controller by commas and normalize into a list
    def _format_text_data(self, text_data):
        return_list = []
        remainder_data = text_data
        while remainder_data.find(',')>=0:
            message_dict = self._format_group( remainder_data[:remainder_data.find(',')] ) 
            return_list.append(message_dict)
            remainder_data = remainder_data[remainder_data.find(',')+1:]
        message_dict = self._format_group( remainder_data )
        return_list.append(message_dict)
        return return_list

    def _format_group(self, group_data):
        return_dict = {}
        remainder_data = group_data
        while remainder_data.find(':')>=0:
            message = remainder_data[:remainder_data.find(':')].replace('\n','').replace('\r','')
            remainder_data = remainder_data[remainder_data.find(':')+1:]
            if remainder_data.find(' ')>=0:
                parameter = remainder_data[:remainder_data.find(' ')].replace('\n','').replace('\r','')
                remainder_data = remainder_data[remainder_data.find(' ')+1:]
            else:
                parameter = remainder_data.replace('\r','').replace('\n','')
                return_dict[message] = parameter
        return return_dict

    def _adjust_positions_received(self, message_dict):
        """ Adjust positions for slack errors if positions in message_dict. 
            Return whether any positions are in message_dict.
            Save reported positions in report_pos dictionary state variable
            Save actual positions in actual_pos dictionary state variable
        """
        axis_found = False
        for key,value in message_dict.items():
            if key == 'None':

                for k,v in value.items():
                    aim_v_float = float(v)
                    # UPDATE REPORTED POS
                    if k in self._state_dict['reported_pos']:
                        self._state_dict['reported_pos'][k] = aim_v_float
                        self._state_dict['actual_pos'][k] = aim_v_float + self._state_dict['error'][k]
                        axis_found = True

        return axis_found

    def _process_message_dict(self, message_dict):
        """ 
        Process messages received from motorcontroller

        Example message_dict:
        { 'None': { "X": '6.107', "Y": '300.831' } }


        1.  If there is position data, adjust it to compensate for slack errors, put it 
            into a "pos" dictionary, and then try to send out with "_on_data" callback.


        2.  Try sending out "_on_data" callback of message received.


        3.  Check if message includes acknowledgement motorcontroller received message (ack_received).
            If received, update corresponding state variables for flow control.


        4.  Check if messsage includes acknowledgement motorcontroller ready for next command (ack_ready).
            If received, update corresponding state varialbes for flow control.


        5.  If flow control state variables indicate a command can be sent to motorcontroller, try 
            sending the next command in the command queue.
        """
        # 1.
        axis_found = False
        for name_message, value in message_dict.items():
            
            # if name_message is None then there was nothing prefixing name,value pairs reported
            if name_message == 'None':
                # so then check positions for making adjustments to reported positions
                axis_found = self._adjust_positions_received(message_dict)  
                
        # if axis data in message_didct and there's an on_data callback, send "pos" dictionary
        if axis_found == True:
            pos_dict = {'pos':copy.deepcopy(self._state_dict['actual_pos'])}
            if self._on_data:
                self._on_data(session_id=self._state_dict['current_command_session_id'],where_from=self._state_dict['current_command_where_from'],message=pos_dict) 
        
        # 2. if there's an on_data callback, send message_dict
        if self._on_data:
            self._on_data(session_id=self._state_dict['current_command_session_id'],where_from=self._state_dict['current_command_where_from'],message=message_dict)
        
        # 3. check if ack_received confirmation
        if self._config_dict['ack_received_message'] in message_dict or self._config_dict['ack_received_message'] is None:
            value = message_dict.get(self._config_dict['ack_received_message'])
            if isinstance(value, dict):
                if self._config_dict['ack_receieved_parameter'] is None:
                    self._state_dict['ack_received'] = True
                    if self._timeout_handler is not None:
                        self._timeout_hadler.cancel()
                else:
                    for value_name, value_value in value.items():
                        if value_name == self._config_dict['ack_received_parameter']:
                            if self._config_dict['ack_received_value'] is None or value_value == self._config_dict['ack_receieved_value']:
                                self._state_dict['ack_received'] = True
                                if self._timeout_handler is not None:
                                    self._timeout_hadler.cancel()
            else:
                if self._config_dict['ack_received_parameter'] is None:
                    if self._config_dict['ack_received_value'] is None or value == self._config_dict['ack_received_value']:
                        self._state_dict['ack_received'] = True
                        if self._timeout_handler is not None:
                            self._timeout_hadler.cancel()

        # 4. check if ack_ready confirmation
        if self._config_dict['ack_ready_message'] in message_dict or self._config_dict['ack_ready_message'] is None:
            value = message_dict.get(self._config_dict['ack_ready_message'])
            if isinstance(value, dict):
                if self._config_dict['ack_ready_parameter'] is None:
                    self._state_dict['ack_ready'] = True
                else:
                    for value_name, value_value in value.items():
                        if value_name == self._config_dict['ack_ready_parameter']:
                            if self._config_dict['ack_ready_value'] is None or str(value_value) == str(self._config_dict['ack_ready_value']):
                                self._state_dict['ack_ready'] = True
                            else:
                                self._state_dict['ack_ready'] = False
            else:
                if self._config_dict['ack_ready_parameter'] is None:
                    if self._config_dict['ack_ready_value'] is None or value == self._config_dict['ack_ready_value']:
                        self._state_dict['ack_ready'] = True
                    else:
                        self._state_dict['ack_ready'] = False
                else:
                    if value == self._config_dict['ack_ready_parameter']:
                        self._state_dict['ack_ready'] = True
                    else:
                        self._state_dict['ack_ready'] = False                   

        # 5. done processing message, ready to try next command in queue
        if self._state_dict['ack_received'] == True:
            if self._state_dict['feedback_on'] == True:
                if self._state_dict['ack_ready'] == True:
                    self._try_send()
            else:
                self._try_send()


# PROTOCOL CALLBACKS
    def _on_connection_made_handler(self):
        """ Fire callback notifying connection made to motorcontroller and set corresponding state variables """
        self._state_dict['connected'] = True
        self._state_dict['transport'] = True if self._transport else False
        if self._on_connection_made:
            self._on_connection_made(session_id=self._state_dict['connected_session_id'])

    def _on_raw_data_handler(self, data):
        """ Fire callback that returns raw data from the motorcontroller """
        if self._on_raw_data:
            self._on_raw_data(where_from=self._state_dict['current_command_where_from'],session_id=self._state_dict['current_command_session_id'],data=data)

    def _on_data_handler(self, datum):
        """ Normalizes incoming data from Output(asyncio.protocol) and then procesess with _process_message_dict()
        """
        json_data = ""
        text_data = ""

        if isinstance(datum,dict):
            json_data = json.dumps(datum)
        else:
            str_datum = str(datum)
            text_data = str_datum

            if self._config_dict['ack_received_message'] in str_datum:
                self.ack_received = True

            if str_datum.find('{')>=0:
                json_data = str_datum[str_datum.find('{'):].replace('\n','').replace('\r','')
                text_data = str_datum[:str_datum.index('{')]

        if text_data != "":
            text_message_list = self._format_text_data(text_data)
            
            for message in text_message_list:
                self._process_message_dict(message)

        if json_data != "":
            try:
                json_data_dict = json.loads(json_data)
                self._process_message_dict(json_data_dict)
            except:
                pass
                # log

    def _on_connection_lost_handler(self):
        """ Fire callback notifying loss of connection to motorcontroller and reset corresponding state variables """
        self._state_dict['connected'] = False
        self._state_dict['transport'] = True if self._transport else False
        if self._on_connection_lost:
            self.on_connection_lost(session_id=self._state_dict['connected_session_id'])

    def _on_timeout_handler(self):
        """ Fire the timeout callback for messages sent to motorcontroller """
        if self._on_timeout:
            self._on_timeout(self._state_dict['current_command_session_id'])


# API - "META"
    def connect(self, session_id=None, host='0.0.0.0', port=3333):
        """ Connect to the motor-controller. Try to use environment variables for the 
            host and port if available, otherwise use the host and port provided as 
            arguments.
        """
        self._callbacker = Output(self)
        self._state_dict['connected_session_id'] = session_id
        try:
            smoothie_host=os.environ.get('SMOOTHIE_HOST', '0.0.0.0')
            smoothie_port=int(os.environ.get('SMOOTHIE_PORT', '3333'))
            self._loop.create_task(self.the_loop.create_connection(
                    lambda: self._callbacker,
                    host=smoothie_host,
                    port=smoothie_port))
        except:
            pass
            # log

    def disconnect(self, session_id=""):
        self._state_dict['disconnected_session_id'] = session_id
        if self._transport:
            self._transport.close()

    def on_data_handler_tester(self, datum):
        """ Injects datum into _on_data_handler for testing
        """
        self._on_data_handler(datum)

    def get_state(self):
        """ Return a read-only copy of the state variables """
        return copy.deepcopy(self._state_dict)

    def clear_queue(self, session_id, where_from=""):
        """ Clear the queue, reset the flow control state variables, and take note 
            of the session_id and where_from used to send the command.
        """
        self._command_queue = []
        self._state_dict['current_command_session_id'] = session_id
        self._state_dict['current_command_where_from'] = where_from
        self._state_dict['ack_ready'] = True
        self._state_dict['ack_received'] = True
        self._cmd_q.clear_queue()
        return self.get_state()


    def register_on_connection_made(self, callback):
        if callable(callback):
            self._on_connection_made = callback

    def register_on_raw_data(self, callback):
        if callable(callback):
            self._on_raw_data = callback

    def register_on_connection_lost(self, callback):
        if callable(callback):
            self._on_connection_lost = callback

    def register_on_empty_queue(self, callback):
        if callable(callback):
            self._on_empty_queue = callback

    def register_on_data(self, callback):
        if callable(callback):
            self._on_data = callback

    def register_on_timeout(self, callback):
        if callable(callback):
            self._on_timeout = callback
 
# API - "COMMANDS"
    def move(self, session_id, where_from="", **kwargs):
        """ Relative linear move (G90 G0) """
        self._send_command(session_id=session_id, where_from="where_from", code=self.MOVE, **kwargs)
        
    def move_to(self,session_id,where_from="", **kwargs):
        """ Absolute linear move (G91 G0) """
        self._send_command(session_id=session_id, where_from="where_from", code=self.MOVE_TO, **kwargs)

    def rapid_linear_move(self,session_id,where_from="", **kwargs):
        """ Rapid linear move (G1)

        Do things like running extruders while moving. Uses feed rate. """
        self._send_command(session_id=session_id, where_from="where_from", code=self.RAPID_LINEAR_MOVE, **kwargs)

    def linear_move(self,session_id,where_from="", **kwargs):
        """ Linear move (G0)

        Go to position and then do things, like run extruders. Uses seek rate. """
        self._send_command(session_id=session_id, where_from="where_from", code=self.LINEAR_MOVE, **kwargs)

    def home(self,session_id,where_from="", **kwargs):
        """ Home (G28) """
        self._send_command(session_id=session_id, where_from="where_from", code=self.HOME, **kwargs)

    def absolute(self, session_id,where_from="", **kwargs):
        """ Absolute mode (G90) """
        self._send_command(session_id=session_id, where_from="where_from", code=self.ABSOLUTE, **kwargs)

    def relative(self, session_id,where_from="", **kwargs):
        """ Relative mode (G91) """
        self._send_command(session_id=session_id, where_from="where_from", code=self.RELATIVE, **kwargs)

    def speed_xyz(self, session_id,speed,where_from=""):
        """ XYZ speed (F) """
        args = {'F':speed}
        self._send_command(session_id=session_id, where_from="where_from", code='', **args)

    def speed_a(self, session_id,speed,where_from=""):
        """ A speed (a) """
        args = {self.SPEED_A:speed}
        self._send_command(session_id=session_id, where_from="where_from", code='', **args)

    def speed_b(self, session_id,speed,where_from=""):
        """ B speed (b) """
        args = {self.SPEED_B:speed}
        self._send_command(session_id=session_id, where_from="where_from", code='', **args)

    def speed_c(self, session_id,speed,where_from=""):
        """ C speed """
        args = {self.SPEED_C:speed}
        self._send_command(session_id=session_id, where_from="where_from", code='', **args)

    def enable_motors(self, session_id,where_from=""):
        """ Enable motors (M17) """
        self._send_command(session_id=session_id, where_from="where_from", code=self.ENABLE_MOTORS)

    def disable_motors(self, session_id,where_from=""):
        """ Disable motors (M18) """
        self._send_command(session_id=session_id, where_from="where_from", code=self.DISABLE_MOTORS)

    def feedback_on(self, session_id,where_from=""):
        """ Turn on feedback (M62) """
        self._send_command(session_id=session_id, where_from="where_from", code=self.FEEDBACK_ON)

    def feedback_off(self, session_id,where_from=""):
        """ Turn off feedback (M63) """
        self._send_command(session_id=session_id, where_from="where_from", code=self.FEEDBACK_OFF)

    def halt(self, session_id,where_from=""):
        """ Halt everything (M112) 

        No commands will be accepted until a RESET FROM HALT (M999).
        """
        self._send_command(session_id=session_id, where_from="where_from", code=self.HALT)

    def positions(self, session_id,where_from=""):
        """ Report positions (M114) """
        self._send_command(session_id=session_id, where_from="where_from", code=self.POSITIONS)

    def limit_switches(self, session_id,where_from=""):
        """ Report limit switches (M119) """
        self._send_command(session_id=session_id, where_from="where_from", code=self.LIMIT_SWITCHES)

    def feed_rate(self, session_id,where_from="", **kwargs):
        """ Show/set feed rates (M198) """
        self._send_command(session_id=session_id, where_from="where_from", code=self.FEED_RATE, **kwargs)

    def seek_rate(self, session_id,where_from="", **kwargs):
        """ Show/set seek rates (M199) """
        self._send_command(session_id=session_id, where_from="where_from", code=self.SEEK_RATE, **kwargs)

    def max_rates(self, session_id,where_from="", **kwargs):
        """ Show/set max rates (M203) """
        self._send_command(session_id=session_id, where_from="where_from", code=self.MAX_RATES, **kwargs)

    def acceleration(self, session_id,where_from="", **kwargs):
        """ Show/set acceleration (M204) """

        " S = XY, ZAB"
        self._send_command(session_id=session_id, where_from="where_from", code=self.ACCELERATION, **kwargs)

    def junction(self, session_id,where_from="", **kwargs):
        """ Show/set junction (M205) """
        self._send_command(session_id=session_id, where_from="where_from", code=self.JUNCTION, **kwargs)

    def reset(self, session_id,where_from=""):
        """ Reset motorcontroller (reset) 

        This will shut-down the motorcontroller in 5 seconds and then restart it.
        Connection will be lost.
        """
        self._send_command(session_id=session_id, where_from="where_from", code=self.RESET)

    def reset_from_halt(self, session_id,where_from=""):
        """ Reset from halt (M999) """
        self._send_command(session_id=session_id, where_from="where_from", code=self.RESET_FROM_HALT)




class CommandQueue():
    """
    This object stores commands FIFO and tracks information about them as they are processed.


    Commands are stored in two lists:

    "command_queue" : Commands yet to be completed
    "completed" : Commands completed

    Commands are added to the end of the "command_queue" with add_command(command)

    Commands are retrieved FIFO with next(), moving the "current_command" being processed
    to "completed" and returning the .

    """

    def __init__(self):
        self._size = 0

        self._command_queue = []

        self._completed = []

        self._current_command = None

        self._counter = 0


    @property
    def size(self):
        """ Number of commands in queue """
        return self._size

    def add_command(self, command):
        """ Add a command to the queue
        """
        if command is not None:
            self._counter+=1
            self._command_element = {'uid': uuid.uuid4(),
                                     'number': self._counter,
                                     't_add': datetime.datetime.utcnow(),
                                     't_out': 'na',
                                     't_com': 'na',
                                     'command': command,
                                     'result': 'tbd'}
            self._command_queue.append(self._command_element)
            self._size = len(self._command_queue)
        else:
            return False

    def next(self, result='success',show_all=False):
        """ Return the next command if there is one and move the current command to the
            completed list with a note about its result.
        """
        if self._size > 0:
            if self._current_command is not None:
                self._current_command['t_com'] = datetime.datetime.utcnow()
                self._current_command['result'] = result

                self._completed.append(self._current_command)

            self._size = len(self._command_queue)
            
            self._current_command = self._command_queue.pop(0)
            self._current_command['t_out'] = datetime.datetime.utcnow()
            return_command = copy.deepcopy(self._current_command)

            if show_all == True:
                return return_command
            else:
                return return_command['command']
        
        return None

    #@property? read-only getter
    def completed(self):
        """ Return a read-only copy of the completed list """
        return copy.deepcopy(self._completed)


    #@property? read-only getter
    def command_queue(self, show_all=False):
        """
        Get a copy of the "command queue". Only sends the actual commands by default.
        If you want the "command queue" in all its gory details, pass 'show_all' as True
        """
        if show_all == True:
            return copy.deepcopy(self._command_queue)
        else:
            command_list = [c['command'] for c in self._command_queue]
            return command_list


    def flush_completed(self):
        """ Flush "the completed queue" """
        self._completed = []


    def clear_queue(self, save_cleared=False):
        """
        Clear the "command queue", and if you want to save the entries to 
        the "completed lists" pass save_cleared as True
        """
        if save_cleared == False:
            self._command_queue = []
        else:
            for c in self._command_queue: c['t_com']=datetime.datetime.utcnow()
            for c in self._command_queue: c['result']='cleared'
            self._completed.append(self._command_queue)
            self._command_queue = []
        self._counter = 0
        self._size = 0























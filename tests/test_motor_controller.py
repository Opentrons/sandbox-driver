# #!/usr/bin/env python3
#
# import unittest
# import asyncio
# import ast
# from apollo.driver.motor_controller import MotorController
# from tests.sernet import STNSimServerClientProtocol
#
#
#
# class SernetTestCase(unittest.TestCase):
#
#     def assertLastCommand(self, *commands):
#         foundOne = False
#         msg = ""
#         if len(self.mc.test_command_list)>0:
#             lastCommand = self.mc.test_command_list[-1]
#             for command in commands:
#                 if lastCommand == command:
#                     foundOne = True
#                     break
#
#             msg = "Expected last command to be "
#
#             if len(commands) is 1:
#                 msg += '"'+repr(commands[0])+'" '
#             else:
#                 msg += "one of: "+", ".join(commands)+" "
#
#                 msg += "but got \""+repr(lastCommand)+"\"."
#         else:
#             msg="test_command_list empty"
#
#         self.assertTrue(foundOne, msg=msg)
#
#
# #		for k,v in mc_state_dict.items():
# #			element = repr(k)+' = '+repr(state_dict[k])+' vs. '+repr(k)+' = '+repr(v)
# #			blob.append(element)
# #
# #		msg="EXPECTED state_dict versus ACTUAL state_dict:\n\n"
# #		msg+='\n'.join(blob)+'\n\n'
# #		print(msg)
# #		self.assertDictEqual(self.mc.get_state(),state_dict, self.mc.get_state())
#
#     def assertStateVariables(self, **kwargs):
#         state_dict = self.mc.get_state()
#
#         all_the_same = True
#         print()
#
#         for k,v in kwargs.items():
#             if k in list(state_dict):
#                 wtf = (state_dict[k] == v)
#                 print('wtf: ',wtf)
#                 msg1 = ''
#                 if state_dict[k] == v:
#                 #    print('+ | '+repr(k)+' : '+repr(state_dict[k])+' == '+repr(k)+' : '+repr(v))
#                     msg1 = '+ | '+repr(k)+' : '+repr(state_dict[k])+' ==  : '+repr(v)
#                 else:
#                     all_the_same = False
#                 #    print('- | '+repr(k)+' : '+repr(state_dict[k])+' == '+repr(k)+' : '+repr(v))
#                     msg1 = '- | '+repr(k)+' : '+repr(state_dict[k])+' == : '+repr(v)
#                 try:
#                     self.assertFalse(wtf,msg1)
#                 except:
#                     print('stuff')
#         self.assertFalse(all_the_same,'not all the same!')
#
#
# #    def assertStateName(self, name='smoothie'):
# #        pass
# #
# #    def assertStateSimulation(self, simulation=False):
# #        pass
# #
# #    def assertStateConnected(self,
#
# class MotorControllerTest(SernetTestCase):
#
# 	def setUp(self):
# 		self.loop = asyncio.get_event_loop()
# 		self.mc = MotorController(loop=self.loop, simulate=True)
# 		self.mc.connect()
#
#
# 	def tearDown(self):
# 		self.mc.disconnect()
#
#
# 	def test_register_on_connection_made(self):
# 		def on_connection_made_print():
# 			print('connection made')
# 		self.mc.register_on_connection_made(on_connection_made_print)
# 		self.assertEqual(on_connection_made_print,self.mc._on_connection_made)
#
# 	def test_register_on_raw_data(self):
# 		self.assertTrue(True,msg="True")
#
# 	def test_register_on_connection_lost(self):
# 		self.assertTrue(True,msg="True")
#
# 	def test_register_on_empty_queue(self):
# 		self.assertTrue(True,msg="True")
#
# 	def test_register_on_data(self):
# 		self.assertTrue(True,msg="True")
#
# 	def test_output_connection_made(self):
# 		class EchoClientProtocol:
# 			def __init__(self, loop):
# 				self.loop = loop
# 				self.transport = None
#
# 			def connection_made(self, transport):
# 				self.transport = transport
#
# 			def data_received(self, data):
# 				pass
#
# 			def connection_lost(self, exc):
# 				self.loop.stop()
#
# 		loop = asyncio.get_event_loop()
# 		connect = loop.create_connection(
# 			lambda: EchoClientProtocol(loop),
# 			host='127.0.0.1', port=8888)
# 		transport, protocol = loop.run_until_complete(connect)
# 		self.mc.connect(session_id='session_id')
# 		self.mc._callbacker.connection_made(transport)
# 		transport.close()
#
# 	def test_output_data_one(self):
# 		MOCK_RESPONSE = "{\"x\":12.345,\"y\":67.890,\"stat\":1}\n\r"
# 		MOCK_RESPONSE_UTF = MOCK_RESPONSE.encode('utf-8')
# 		self.mc.connect(session_id='session_id')
# 		self.mc._callbacker.data_received(MOCK_RESPONSE_UTF)
# 		self.assertStateVariables(direction="{'X':1,'Y':1,'Z':1,'A':0,'B':0,'C':0}", \
# 							reported_pos="{'X':20,'Y':20,'Z':20,'A':0,'B':0,'C':0}", \
# 							actual_pos="{'X':20,'Y':20,'Z':20,'A':0,'B':0,'C':0}", \
# 							ack_received=True, \
# 							ack_ready=True
# 						)
#
# 	def test_output_data_two(self):
# 		MOCK_RESPONSE = "{\"x\":-12.345,\"y\":-67.890,\"stat\":1}\n\r"
# 		MOCK_RESPONSE_UTF = MOCK_RESPONSE.encode('utf-8')
# 		self.mc.connect(session_id='session_id')
# 		self.mc._callbacker.data_received(MOCK_RESPONSE_UTF)
# 		#self.assertEntireState(direction="{'X':1,'Y':1,'Z':1,'A':0,'B':0,'C':0}", \
# 		#					reported_pos="{'X':20,'Y':20,'Z':20,'A':0,'B':0,'C':0}", \
# 		#					actual_pos="{'X':20,'Y':20,'Z':20,'A':0,'B':0,'C':0}", \
# 		#					ack_received=True, \
# 		#					ack_ready=True
# 		#				)
#
# 	def test_output_data_three(self):
# 		MOCK_RESPONSE = "ok{\"a\":12.345,\"b\":67.890}\n\r"
# 		MOCK_RESPONSE_UTF = MOCK_RESPONSE.encode('utf-8')
# 		self.mc.connect(session_id='session_id')
# 		self.mc._callbacker.data_received(MOCK_RESPONSE_UTF)
# 		#self.assertEntireState(direction="{'X':1,'Y':1,'Z':1,'A':0,'B':0,'C':0}", \
# 		#					reported_pos="{'X':20,'Y':20,'Z':20,'A':0,'B':0,'C':0}", \
# 		#					actual_pos="{'X':20,'Y':20,'Z':20,'A':0,'B':0,'C':0}", \
# 		#					ack_received=True, \
# 		#					ack_ready=True
# 		#				)
#
# 	def test_data_response(self):
# 		DATUM = {'None':{'X':'20','Y':'20','Z':'20'}}
# 		self.mc.on_data_handler_tester(DATUM)
# 		#self.assertEntireState(direction="{'X':1,'Y':1,'Z':1,'A':0,'B':0,'C':0}", \
# 		#					reported_pos="{'X':20,'Y':20,'Z':20,'A':0,'B':0,'C':0}", \
# 		#					actual_pos="{'X':20,'Y':20,'Z':20,'A':0,'B':0,'C':0}", \
# 		#					ack_received=True, \
# 		#					ack_ready=True
# 		#				)
#
# 	def test_move(self):
# 		self.mc.move('session_id',x=10)
# 		self.assertLastCommand('G91 G0 X10.0\r\n')
#
# 	def test_move_to(self):
# 		self.mc.move_to('session_id',x=20)
# 		self.assertLastCommand('G90 G0 X20.0\r\n')
#
# 	def test_rapid_linear_move(self):
# 		self.mc.rapid_linear_move('session_id',x=10)
# 		self.assertLastCommand('G1 X10.0\r\n')
#
# 	def test_linear_move(self):
# 		self.mc.linear_move('session_id',x=20)
# 		self.assertLastCommand('G0 X20.0\r\n')
#
# 	def test_home(self):
# 		self.mc.home('session_id')
# 		self.assertLastCommand('G28\r\n')
#
# 	def test_absolute(self):
# 		self.mc.absolute('session_id')
# 		self.assertLastCommand('G90\r\n')
#
# 	def test_relative(self):
# 		self.mc.relative('session_id')
# 		self.assertLastCommand('G91\r\n')
#
# 	def test_speed_xyz(self):
# 		self.mc.speed_xyz('session_id',6000)
# 		self.assertLastCommand('F6000\r\n')
#
# 	def test_speed_a(self):
# 		self.mc.speed_a('session_id',500)
# 		self.assertLastCommand('a500\r\n')
#
# 	def test_speed_b(self):
# 		self.mc.speed_b('session_id',400)
# 		self.assertLastCommand('b400\r\n')
#
#
#
#
#
#
# if __name__ == '__main__':
#     unittest.main()

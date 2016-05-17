#!/usr/bin/env python3

# https://medium.com/@theHQ/using-mock-and-trial-to-create-unit-tests-for-crossbar-applications-867e5b941cf2#.aru3coz3i
# http://python-mock.sourceforge.net/
# https://github.com/python/asyncio/blob/master/tests/test_base_events.py

import asyncio
import unittest
from unittest import mock

from apollo.controller import Controller
from apollo.session import Session
from tests import socket


class ControllerTest(unittest.TestCase):

		

	def setUp(self):
		self.loop = asyncio.new_event_loop()
		# asyncio.set_event_loop(None)

		# self.addr = self.get_free_address()

		# self.server = self.loop.run_until_complete(
		# 	asyncio.start_server(
		# 		self.handle_client_callback,
		# 		host=self.addr[0],
		# 		port=self.addr[1],
		# 		loop=self.loop
		# 	)
		# )
		self.controller = Controller()

	def test_handle_message(self):
		start_session_message = {'start_session' : ""}
		close_session_message = {'close_session' : ""}

		self.controller.start_session = mock.Mock()
		self.controller.close_session = mock.Mock()

		self.controller.handle_message(start_session_message)
		self.controller.handle_message(close_session_message)

		self.assertEqual(1, self.controller.start_session.call_count)
		self.assertEqual(1, self.controller.close_session.call_count)

	def test_start_session(self):
		input_message = {'start_session' : ""}
		self.controller.connect_session = mock.Mock()
		self.controller.publish = mock.Mock()

		self.controller.start_session(input_message)

		sessions = self.controller._sessions

		self.assertEqual(1, len(sessions.items()))
		
		session_id, sessions_obj = list(sessions.items())[0]

		self.assertTrue(isinstance(sessions_obj, Session))
		self.assertTrue(self.controller.publish.called)
		self.assertTrue(self.controller.connect_session.called)

	def test_close_session(self):
		session_id = "foobar123"
		input_message = {'close_session' : session_id}
		self.controller._sessions[session_id] = mock.Mock()
		self.controller.close_session(input_message)
		self.assertTrue(
			mock.call.close() in self.controller._sessions[session_id].method_calls
		)
		

	def test_publish(self):
		pass

	# def test_handshake_with_invalid_msg(self):
	# 	input_message = 'start_sessionFooBar'

	# 	self.controller.handshake(input_message)

	# 	self.assertEqual(1, length(sessions.items()))
		
	# 	session_id, sessions_obj = sessions.items()[0]

	# 	self.assertTrue(isinstance(sessions_obj, Session))
		


	def test_connect(self):
		pass


	def test_publish(self):
		pass


	def test_handshake_start_session(self):
		pass


	def test_handshake_close_session(self):
		pass




if __name__ == '__main__':
    unittest.main()

#!/usr/bin/env python3

# https://medium.com/@theHQ/using-mock-and-trial-to-create-unit-tests-for-crossbar-applications-867e5b941cf2#.aru3coz3i
# http://python-mock.sourceforge.net/
# https://github.com/python/asyncio/blob/master/tests/test_base_events.py

import unittest
from controller.controller import Controller


class ControllerTestCase(unittest.TestCase):

	def assertSomething(self):
		pass


class ControllerTest(ControllerTestCase):

	def setUp(self):
		self.ctrl = Controller()
		pass


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

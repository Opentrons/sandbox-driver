#!/usr/bin/env python3

import unittest
import asyncio
import ast
from driver.motor_controller import MotorController
from tests.sernet import STNSimServerClientProtocol



class CmdQueueTestCase(unittest.TestCase):

	def assertSize(self, size):
		pass


	def assertCompleted(self, *commands):
		pass


	def assertCommand(self, **kwargs):
		pass


	def assertCommands(self, ):
		pass



class CommandQueueTest(CmdQueueTestCase):

	test_commands = []

	def setUp(self):
		self.cq = CommandQueue()


	def test_add_one_command(self):
		pass


	def test_add_commands(self):
		pass


	def test_next(self):
		pass


	def test_cleare_queue(self):
		pass





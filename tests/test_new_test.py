#!/usr/bin/env python3
import sys
sys.path.append('../driver')
import motor_controller

def test_command_queue_one():
	"""Test adding a single command. Assert whether it is returned with next()?"""
	cq = motor_controller.CommandQueue()

	command = {"test": "command"}
	cq.add_command(command)

	result = cq.next()

	assert result == command


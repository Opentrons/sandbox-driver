import unittest
from unittest import mock
import asyncio

from apollo.command_to_gcode import CommandProcessor

class CommandToGCodeTestCase(unittest.TestCase):


    def setUp(self):

        self.mock = mock.Mock()

        @asyncio.coroutine
        def mMock(m):
            self.mock(m)


        self.loop = asyncio.new_event_loop()

        self.processor = CommandProcessor()

        self.processor.smoothie_com.send = mMock


    def test_move_command(self):
        '''
        Testing the 'move' command for absolute coordinates
        '''

        self.loop.run_until_complete(self.processor.process({
            'type':'move',
            'data': {
                'x': 100.123,
                'y': 200.234,
                'z': -300.987,
                'a': 10.011,
                'b': 20.12
            }
        }))

        result = self.mock.call_args_list

        expected = [
            mock.call('G91'),
            mock.call('G0 X100.123 Y200.234 Z-300.987 A10.011 B20.12'),
        ]

        self.assertEquals(expected, result)
        self.mock.reset_mock()


    def test_move_to_command(self):
        '''
        Testing the 'move_to' command for relative coordinates
        '''

        self.loop.run_until_complete(self.processor.process({
            'type':'move_to',
            'data': {
                'x': 100,
                'y': 200,
                'z': 300,
                'a': 10,
                'b': 20
            }
        }))

        result = self.mock.call_args_list

        expected = [
            mock.call('G90'),
            mock.call('G0 X100 Y200 Z300 A10 B20'),
        ]

        self.assertEquals(expected, result)
        self.mock.reset_mock()


    def test_speed_command(self):
        '''
        Testing the 'speed' command
        '''

        self.loop.run_until_complete(self.processor.process({
            'type':'speed',
            'data': {
                'xyz': 3000,
                'y': 200,       # should be ignored
                'z': 300,       # should be ignored
                'a': 400,
                'b': 500
            }
        }))

        result = self.mock.call_args_list

        expected = [
            mock.call('F3000'),
            mock.call('a400'),
            mock.call('b500'),
        ]

        self.assertEquals(expected, result)
        self.mock.reset_mock()


    def test_acceleration_command(self):
        '''
        Testing the 'acceleration' command
        '''

        self.loop.run_until_complete(self.processor.process({
            'type':'acceleration',
            'data': {
                'xy': 3000,
                'z': 200,
                'x': 300,       # should be ignored
                'a': 400,
                'b': 500
            }
        }))

        result = self.mock.call_args_list

        expected = [
            mock.call('M204 S3000 Z200 A400 B500')
        ]

        self.assertEquals(expected, result)
        self.mock.reset_mock()

        self.loop.run_until_complete(self.processor.process({
            'type':'acceleration',
            'data': {}
        }))

        result = self.mock.call_args_list

        expected = []

        self.assertEquals(expected, result)
        self.mock.reset_mock()


    def test_home_command(self):
        '''
        Testing the 'home' command
        '''

        expected = []

        # test ALL axis
        self.loop.run_until_complete(self.processor.process({
            'type':'home',
            'data': ['x','y','z','a','b']
        }))

        result = self.mock.call_args_list

        expected = [mock.call('G28 X Y Z A B')]

        self.assertEquals(expected, result)
        self.mock.reset_mock()

        # test a few of the axis
        self.loop.run_until_complete(self.processor.process({
            'type':'home',
            'data': ['x','b']
        }))

        result = self.mock.call_args_list

        expected = [mock.call('G28 X B')]

        self.assertEquals(expected, result)
        self.mock.reset_mock()

        # test if data is None
        self.loop.run_until_complete(self.processor.process({
            'type':'home',
            'data': None
        }))

        result = self.mock.call_args_list

        expected = [mock.call('G28')]

        self.assertEquals(expected, result)
        self.mock.reset_mock()


    def test_hardstop_command(self):
        '''
        Testing the 'hardstop' command
        '''

        self.loop.run_until_complete(self.processor.process({
            'type':'hardstop'
        }))

        result = self.mock.call_args_list

        expected = [
            mock.call('M112'),
            mock.call('M999')
        ]

        self.assertEquals(expected, result)
        self.mock.reset_mock()














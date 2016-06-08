import unittest
from unittest import mock
import asyncio

from apollo.command_to_gcode import CommandToGCode

class CommandToGCodeTestCase(unittest.TestCase):


    def setUp(self):

        self.mock = mock.Mock()

        self.coords = {'X':0,'Y':0,'Z':0,'A':0,'B':0,'x':0,'y':0,'z':0,'a':0,'b':0}

        @asyncio.coroutine
        def mMock(m):
            self.mock(m)
            if m[0:4] == 'M114':
                return self.coords


        self.loop = asyncio.new_event_loop()

        self.com2gcode = CommandToGCode()

        self.com2gcode.smoothie_com.send = mMock


    def test_move_rel_command(self):
        '''
        Testing the 'move' command for relative coordinates
        '''

        self.loop.run_until_complete(self.com2gcode.process({
            'type':'move',
            'data': {
                'relative' : True,
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


    def test_move_abs_command(self):
        '''
        Testing the 'move' command for absolute coordinates
        '''

        self.loop.run_until_complete(self.com2gcode.process({
            'type':'move',
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


    def test_position_get_command(self):
        '''
        Testing the 'position' command for getting the current axis values
        '''

        @asyncio.coroutine
        def change_position():
            returned_value = yield from self.com2gcode.process({
                'type':'position',
                'data': None
            })
            self.assertEquals({'x':0,'y':0,'z':0,'a':0,'b':0}, returned_value)

        self.loop.run_until_complete(change_position())

        result = self.mock.call_args_list

        expected = [
            mock.call('M114')
        ]

        self.assertEquals(expected, result)
        self.mock.reset_mock()


    def test_position_set_command(self):
        '''
        Testing the 'position' command for setting the current axis values to something new
        '''

        self.loop.run_until_complete(self.com2gcode.process({
            'type':'position',
            'data': {
                'x' : 123,
                'y' : 321.123,
                'z' : 34.02,
                'a' : 12,
                'b' : 444
            }
        }))

        result = self.mock.call_args_list

        expected = [
            mock.call('G92 X123 Y321.123 Z34.02 A12 B444')
        ]

        self.assertEquals(expected, result)
        self.mock.reset_mock()


    def test_speed_command(self):
        '''
        Testing the 'speed' command
        '''

        self.loop.run_until_complete(self.com2gcode.process({
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
            mock.call('G0 F3000 a400 b500'),
        ]

        self.assertEquals(expected, result)
        self.mock.reset_mock()


    def test_acceleration_command(self):
        '''
        Testing the 'acceleration' command
        '''

        self.loop.run_until_complete(self.com2gcode.process({
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

        self.loop.run_until_complete(self.com2gcode.process({
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
        self.loop.run_until_complete(self.com2gcode.process({
            'type':'home',
            'data': ['x','y','z','a','b']
        }))

        result = self.mock.call_args_list

        expected = [mock.call('G28 X Y Z A B')]

        self.assertEquals(expected, result)
        self.mock.reset_mock()

        # test a few of the axis
        self.loop.run_until_complete(self.com2gcode.process({
            'type':'home',
            'data': ['x','b']
        }))

        result = self.mock.call_args_list

        expected = [mock.call('G28 X B')]

        self.assertEquals(expected, result)
        self.mock.reset_mock()

        # test if data is None
        self.loop.run_until_complete(self.com2gcode.process({
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

        self.loop.run_until_complete(self.com2gcode.process({
            'type':'hardstop'
        }))

        result = self.mock.call_args_list

        expected = [
            mock.call('M112'),
            mock.call('M999')
        ]

        self.assertEquals(expected, result)
        self.mock.reset_mock()














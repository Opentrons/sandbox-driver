import unittest
from unittest import mock


from apollo.command_to_gcode import CommandProcessor

class CommandProcessorTestCase(unittest.TestCase):
    def test_move_command(self):
        processor = CommandProcessor()

        processor.smoothie_com = mock.Mock()
        processor.smoothie_com.send = mock.Mock()

        processor.process({
            'type':'move',
            'data': {
                'x': 100,
                'y': 200,
                'z': 300,
                'a': 10,
                'b': 20
            }
        })

        result = processor.smoothie_com.send.call_args_list

        expected = [
            mock.call('G90'),
            mock.call('G0 X100 Y200 Z300 a10 b20'),
        ]

        self.assertEqual(result, expected)



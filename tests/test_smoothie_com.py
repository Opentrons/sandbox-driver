import asyncio
import unittest
from apollo import utils

from apollo.smoothie import SmoothieCom


class SmoothieComTest(unittest.TestCase):
    def setUp(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

        self.address = utils.get_free_os_address()
        self.smc = SmoothieCom(
            self.address[0],
            self.address[1],
        )

    def test_send_M114_gcode(self):
        smoothie_read_sequence = [
            'feedback engaged',
            'ok',
            'ok {"foo":123}',
            'feedback disengaged',
            'ok',
        ]

        smoothie_write_sequence = [b'M62\r\n', b'M114\r\n', b'M63\r\n']

        self.smc.writer = utils.Writer()
        self.smc._read = utils.Reader(smoothie_read_sequence)._read

        self.loop.run_until_complete(self.smc.send('M114', None))

        self.assertEqual(self.smc.writer.drain_buffer, smoothie_write_sequence)



if __name__ == '__main__':
    unittest.main()


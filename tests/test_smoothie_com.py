import asyncio
import unittest
from unittest import mock
import apollo.utils

from apollo.smoothie import SmoothieCom

def get_mock_coro(return_value):
    @asyncio.coroutine
    def mock_coro(*args, **kwargs):
        return return_value
    return mock.Mock(wraps=mock_coro)


class Reader(object):
    def __init__(self, read_sequence):
        self.q = asyncio.Queue()
        [self.q.put_nowait(i) for i in read_sequence]

    @asyncio.coroutine
    def _read(self):
        return (yield from self.q.get())

class Writer(object):
    def __init__(self):
        self.write_buffer = []
        self.drain_buffer = []

    def write(self, data):
        self.write_buffer.append(data)

    @asyncio.coroutine
    def drain(self):
        for item in self.write_buffer:
            self.drain_buffer.append(item)
        self.write_buffer = []


class SmoothieComTest(unittest.TestCase):
    def setUp(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

        self.address = apollo.utils.get_free_os_address()
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

        self.smc.writer = Writer()
        self.smc._read = Reader(smoothie_read_sequence)._read

        self.loop.run_until_complete(self.smc.send('M114', None))

        self.assertEqual(self.smc.writer.drain_buffer, smoothie_write_sequence)



if __name__ == '__main__':
    unittest.main()


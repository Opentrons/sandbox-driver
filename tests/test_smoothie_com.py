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
    @asyncio.coroutine
    def readline(self):
        yield from 1

class Writer(object):
    def __init__(self):
        self.write_buffer = []
        self.drain_buffer = []

    @asyncio.coroutine
    def write(self, data):
        self.write_buffer.append(data)
        print('write buffer has', self.write_buffer)

    @asyncio.coroutine
    def drain(self):
        for item in self.write_buffer:
            self.drain_buffer.append(item)
        self.write_buffer = []


class SmoothieComTest(unittest.TestCase):
    def setUp(self):
        # asyncio.set_event_loop(None)
        # self.loop = asyncio.new_event_loop()
        self.loop = asyncio.get_event_loop()

        self.address = apollo.utils.get_free_os_address()
        self.smc = SmoothieCom(
            self.address[0],
            self.address[1],
            # self.loop,
        )

    def run_in_loop(self, coro):
        return self.loop.run_until_complete(coro)

    def test_send_M114_gcode(self):
        self.smc.writer = Writer()
        self.smc.reader = Reader()

        self.loop.run_until_complete(self.smc.send('M114', None))

        import pdb; pdb.set_trace()


    # def test_send_G0_gcode(self):
    #     pass
    #
    # def test_send_G1_gcode(self):
    #     pass
    #
    # def test_send_G21_gcode(self):
    #     pass
    #
    # def test_turn_off_feedback(self):
    #     pass
    #
    # def test_turn_on_feedback(self):
    #     pass
    #
    #
    #


if __name__ == '__main__':
    unittest.main()


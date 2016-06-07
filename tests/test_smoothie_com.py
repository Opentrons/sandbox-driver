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
        asyncio.set_event_loop(None)
        self.loop = asyncio.new_event_loop()

        self.address = apollo.utils.get_free_os_address()
        self.smc = SmoothieCom(
            self.address[0],
            self.address[1],
            self.loop,
        )
        # self.run_in_loop(self.smc.connect())

    def run_in_loop(self, coro):
        return self.loop.run_until_complete(coro)

    def test_send_M114_gcode(self):
        write_mock = mock.Mock()
        writer_mock = mock.Mock()
        drain_mock = mock.Mock()

        reader_mock = mock.Mock()
        read_mock = mock.Mock()
        read_line_mock = mock.Mock()

        self.smc.writer = get_mock_coro(writer_mock)
        self.smc.writer.drain = get_mock_coro(drain_mock)
        self.smc.writer.write = get_mock_coro(write_mock)

        self.smc.reader = get_mock_coro(reader_mock)
        self.smc.reader.read = get_mock_coro(read_mock)
        self.smc.reader.readline = get_mock_coro(read_line_mock)


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


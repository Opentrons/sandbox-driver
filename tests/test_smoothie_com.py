import asyncio
import unittest
from unittest import mock
import apollo.utils

from apollo.smoothie import SmoothieCom


class SmoothieComTest(unittest.TestCase):
    def setUp(self):
        asyncio.set_event_loop(None)
        self.loop = asyncio.new_event_loop()

        self.address = apollo.utils.get_free_os_address()
        self.smc = SmoothieCom(
            self.address[0],
            self.address[1],
            self.loop,
            is_feedback_enabled=False
        )
        self.run_in_loop(self.smc.connect())

    def run_in_loop(self, coro):
        return self.loop.run_until_complete(coro)

    def tearDown(self):
        self.run_in_loop(self.smc.writer.close())

    def test_connect(self):
        smc = SmoothieCom(
            self.address[0],
            self.address[1],
            self.loop,
            is_feedback_enabled=False
        )
        self.assertTrue(self.run_in_loop(smc.connect()))

    # def test_send_M114_gcode(self):
    #     write_mock = mock.Mock()
    #
    #     import pdb; pdb.set_trace()
    #     self.smc.writer.write = write_mock
    #
    #     self.loop.run_until_complete(self.smc.send('M114'))
    #
    #
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


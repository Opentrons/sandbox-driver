import asyncio
import unittest
import apollo.utils

from apollo.smoothie import SmoothieCom


class SmoothieComTest(unittest.TestCase):
    def setUp(self):
        loop = asyncio.get_event_loop()
        self.address = apollo.utils.get_free_os_address()
        self.sc = SmoothieCom(self.address[0], self.address[1], loop, is_feedback_enabled=False)


    def test_connect(self):
        self.assertTrue(True) 






if __name__ == '__main__':
    unittest.main()


import multiprocessing
import unittest

from apollo.command_receiver_component import enqueue_message


class CommandReceiverComponentTestCase(unittest.TestCase):
    def test_enqueue_message(self):
        qq = multiprocessing.Manager().Queue()

        msg_input = {'type': 'msg'}
        enqueue_message(qq, msg_input)

        idx, msg_output = qq.get_nowait()

        self.assertEqual(msg_input, msg_output)
        self.assertTrue(isinstance(idx, str))

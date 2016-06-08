import asyncio
import multiprocessing
import unittest
from unittest import mock

from autobahn.wamp.types import ComponentConfig

from apollo.command_receiver_component import (
    enqueue_message,
    CommandReceiverComponent
)


class CommandReceiverComponentTestCase(unittest.TestCase):
    def test_enqueue_message(self):
        qq = multiprocessing.Manager().Queue()

        msg_input = {'type': 'msg'}
        enqueue_message(qq, msg_input)

        idx, msg_output = qq.get_nowait()

        self.assertEqual(msg_input, msg_output)
        self.assertTrue(isinstance(idx, str))


    def test_command_recv(self):

        command_queue = mock.Mock()

        config = ComponentConfig(extra={'command_queue': command_queue})

        comp = CommandReceiverComponent(config)
        comp._transport = mock.Mock()

        loop = asyncio.get_event_loop()

        loop.run_until_complete(comp.onJoin(None))

        import pdb; pdb.set_trace()



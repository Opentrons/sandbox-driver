import asyncio
import multiprocessing
import unittest
from unittest import mock

from autobahn.wamp.types import ComponentConfig

from apollo.command_receiver_component import (
    message_queue_router,
    CommandReceiverComponent
)

from apollo import utils


class CommandReceiverComponentTestCase(unittest.TestCase):
    def test_enqueue_message(self):
        qq = multiprocessing.Manager().Queue()

        msg_input = {'type': 'msg'}
        message_queue_router(qq, msg_input)

        idx, msg_output = qq.get_nowait()

        self.assertEqual(msg_input, msg_output)
        self.assertTrue(isinstance(idx, str))


    def test_command_recv_subscribes_on_joining(self):
        command_queue = mock.Mock()
        config = ComponentConfig(extra={'command_queue': command_queue})
        comp = CommandReceiverComponent(config)
        comp._transport = mock.Mock()

        subscribe_mock, subscribe_mock_coro = utils.mock_coro_factory()
        comp.subscribe = subscribe_mock_coro

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(comp.onJoin(None))

        self.assertTrue(subscribe_mock.called)

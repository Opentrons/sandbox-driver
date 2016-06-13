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
    def test_message_queue_router(self):
        cmd_q = multiprocessing.Manager().Queue()
        cnt_q = multiprocessing.Manager().Queue()

        pause_msg = {'type': 'pause'}
        resume_msg = {'type': 'resume'}
        data_msg = {'type': 'foo'}
        erase_msg = {'type': 'erase'}

        message_queue_router(cmd_q, cnt_q, data_msg)
        message_queue_router(cmd_q, cnt_q, pause_msg)
        message_queue_router(cmd_q, cnt_q, data_msg)
        message_queue_router(cmd_q, cnt_q, resume_msg)
        message_queue_router(cmd_q, cnt_q, erase_msg)

        self.assertEqual(cmd_q.qsize(), 2)
        self.assertEqual(cnt_q.qsize(), 3)


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

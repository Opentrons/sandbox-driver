import asyncio
import multiprocessing
import unittest
from unittest import mock

from autobahn.wamp.types import ComponentConfig

from apollo.command_processor_component import (
    CommandProcessorComponent
)

from apollo import utils


class CommandProcessorComponentTestCase(unittest.TestCase):

    def test_command_processor_publishes_on_joining(self):
        command_queue = multiprocessing.Manager().Queue()
        control_queue = multiprocessing.Manager().Queue()

        command_queue.put_nowait({})
        command_queue.put_nowait(None)

        config = ComponentConfig(extra={
            'command_queue': command_queue,
            'control_queue': control_queue
        })
        comp = CommandProcessorComponent(config)
        comp._transport = mock.Mock()

        comp.publish = mock.Mock()

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(comp.onJoin(None))

        self.assertTrue(comp.publish.called)

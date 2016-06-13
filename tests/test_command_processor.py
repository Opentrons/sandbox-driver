import asyncio
import multiprocessing
import unittest
from unittest import mock

from autobahn.wamp.types import ComponentConfig

from apollo.command_processor_component import (
    CommandProcessorComponent
)


class CommandProcessorComponentTestCase(unittest.TestCase):

    def setUp(self):
        self.command_queue = multiprocessing.Manager().Queue()
        self.control_queue = multiprocessing.Manager().Queue()

        config = ComponentConfig(extra={
            'command_queue': self.command_queue,
            'control_queue': self.control_queue
        })
        self.comp = CommandProcessorComponent(config)
        self.comp._transport = mock.Mock()


    def test_command_processor_publishes_on_joining(self):
        self.command_queue.put_nowait({})
        self.command_queue.put_nowait(None)

        self.comp.publish = mock.Mock()

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.comp.onJoin(None))

        self.assertTrue(self.comp.publish.called)


    def test_command_processor_pauses_and_resumes(self):
        self.control_queue.put_nowait({'type': 'pause'})
        self.control_queue.put_nowait({'type': 'resume'})
        self.command_queue.put_nowait(None)

        self.comp.publish = mock.Mock()
        self.comp.on_pause = mock.Mock()
        self.comp.on_resume = mock.Mock()

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.comp.onJoin(None))

        self.assertTrue(self.comp.on_pause.called)
        self.assertTrue(self.comp.on_resume.called)

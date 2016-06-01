#!/usr/bin/env python3

import asyncio
import logging
import multiprocessing

from apollo import utils

from autobahn.asyncio import wamp


logger = logging.getLogger()


def get_command_processor_component(command_queue):
    class RobotCommandProcessorComponent(wamp.ApplicationSession):
        """WAMP application session for Controller"""

        @asyncio.coroutine
        def onJoin(self, details):
            logger.info('RobotCommandProcessor joined')

            while True:
                id, msg = yield from utils.coro_queue_get(command_queue)
                logger.debug('Dequeued Message ID: {} with {}'.format(id, msg))
                self.publish('com.opentrons.robot_to_browser', msg)

    return RobotCommandProcessorComponent


if __name__ == '__main__':
    URL_TEMPLATE = "ws://{host}:{port}/{path}"

    url = URL_TEMPLATE.format(
        host='localhost',
        port='8000',
        path='ws'
    )

    command_queue = multiprocessing.Manager().Queue(50)
    component = get_command_processor_component(command_queue)

    command_queue.put_nowait('foo')

    runner = wamp.ApplicationRunner(url, realm='ot_realm')
    runner.run(component)

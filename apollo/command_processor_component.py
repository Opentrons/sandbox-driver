#!/usr/bin/env python3

import asyncio
import logging
import multiprocessing

from apollo import utils

from autobahn.asyncio import wamp


logger = logging.getLogger()


class RobotCommandProcessorComponent(wamp.ApplicationSession):
    """WAMP application session for Controller"""

    @asyncio.coroutine
    def onJoin(self, details):
        logger.info('RobotCommandProcessor joined')

        command_queue = self.config.extra.get('command_queue')

        if not command_queue:
            raise Exception('A command_queue must be set in self.config.extra')

        while True:
            id, msg = yield from utils.coro_queue_get(command_queue)

            # TODO: execute roboto message and publish result

            logger.debug('Dequeued Message ID: {} with {}'.format(id, msg))
            self.publish('com.opentrons.robot_to_browser', msg)


if __name__ == '__main__':
    URL_TEMPLATE = "ws://{host}:{port}/{path}"

    url = URL_TEMPLATE.format(
        host='localhost',
        port='8000',
        path='ws'
    )

    command_queue = multiprocessing.Manager().Queue(50)

    print(type(command_queue))

    runner = wamp.ApplicationRunner(
        url, realm='ot_realm',
        extra={'command_queue': command_queue}
    )
    runner.run(RobotCommandProcessorComponent)

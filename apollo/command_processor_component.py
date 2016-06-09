#!/usr/bin/env python3

import asyncio
import logging
import multiprocessing

from autobahn.asyncio import wamp

from config.settings import Config
from apollo import utils


logger = logging.getLogger()


class CommandProcessorComponent(wamp.ApplicationSession):
    """WAMP application session for Controller"""

    @asyncio.coroutine
    def onJoin(self, details):
        logger.info('CommandProcessorComponent joined')

        command_queue = self.config.extra.get('command_queue')

        if not command_queue:
            raise Exception('A command_queue must be set in self.config.extra')

        # Consumes messages from queue; shutsdown if None is received
        while True:
            msg = yield from utils.coro_queue_get(command_queue)

            # Poison pill
            if msg is None:
                break

            # TODO: execute roboto message and publish result

            logger.debug(
                'Dequeued Message ID: {} with {}'.format(
                    msg.get('ID', 'ID NOT FOUND'), msg
                )
            )

            self.publish(Config.ROBOT_TO_BROWSER_TOPIC, msg)


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
    runner.run(CommandProcessorComponent)

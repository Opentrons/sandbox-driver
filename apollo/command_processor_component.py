#!/usr/bin/env python3

import asyncio
import logging
import multiprocessing
import queue

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
        control_queue = self.config.extra.get('control_queue')

        if not command_queue:
            raise Exception('A command_queue must be set in self.config.extra')

        if not control_queue:
            raise Exception('A control_queue must be set in self.config.extra')

        while True:
            cnt_msg = yield from utils.coro_queue_get(control_queue)

            if cnt_msg == 'pause':
                while True:
                    cnt_msg = yield from utils.coro_queue_get(control_queue)
                    if cnt_msg == 'resume':
                        break
                    yield from asyncio.sleep(0.1)

            elif cnt_msg == 'erase':
                utils.flush_queue(command_queue)
                continue

            elif cnt_msg == 'resume':
                pass

            else:
                logger.error('Received unknown control message: {}'.format(cnt_msg))
                break

            cmd_pkt = yield from utils.coro_queue_get(command_queue)
            pkt_id = cmd_pkt.get('id', 'ID NOT FOUND')

            # TODO: execute roboto message and publish result

            logger.debug('Dequeued Message ID: {} with {}'.format(pkt_id, cmd_pkt))
            self.publish(Config.ROBOT_TO_BROWSER_TOPIC, cmd_pkt)


if __name__ == '__main__':
    URL_TEMPLATE = "ws://{host}:{port}/{path}"

    url = URL_TEMPLATE.format(
        host='localhost',
        port='8000',
        path='ws'
    )

    command_queue = multiprocessing.Manager().Queue(50)
    control_queue = multiprocessing.Manager().Queue(50)

    print(type(command_queue))

    runner = wamp.ApplicationRunner(
        url, realm='ot_realm',
        extra={
            'command_queue': command_queue,
            'control_queue': control_queue
        }
    )
    runner.run(CommandProcessorComponent)

#!/usr/bin/env python3

import asyncio
import logging
import multiprocessing

from autobahn.asyncio import wamp

from apollo import utils
from config.settings import Config


logger = logging.getLogger()


class CommandProcessorComponent(wamp.ApplicationSession):
    """WAMP application session for Controller"""

    def on_erase(self, command_queue):
        logger.info('Erase control command received')
        utils.flush_queue(command_queue)

    def on_pause(self):
        logger.info('Pause control command received')

    def on_resume(self):
        logger.info('Resume control command received')

    def on_terminate(self):
        logger.info('Terminate control command received')

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
            # Handle control packets if any exist
            if control_queue.qsize() > 0:
                packet = yield from utils.coro_queue_get(control_queue)
                pkt_type = packet.get('type')
                if pkt_type == 'pause':
                    self.on_pause()
                    while True:
                        packet = yield from utils.coro_queue_get(control_queue)
                        pkt_type = packet.get('type')
                        if pkt_type == 'resume':
                            self.on_resume()
                            break
                        yield from asyncio.sleep(0.1)
                elif pkt_type == 'erase':
                    self.on_erase(command_queue)
                    continue
                elif pkt_type == 'resume':
                    self.on_resume()
                elif pkt_type == 'terminate':
                    self.on_terminate()
                    return
                else:
                    logger.error('Received unknown control message: {}'.format(pkt_type))

            # Handle command packets (loop suspends execution if queue is empty)
            cmd_pkt = yield from utils.coro_queue_get(command_queue)

            if cmd_pkt is None:
                logger.info('Received None in command_queue. Shutting down.')
                return

            pkt_id = cmd_pkt.get('id', 'NA')

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

import asyncio
from functools import partial
import logging
import multiprocessing
import uuid

from autobahn.asyncio import wamp

from config.settings import Config

logger = logging.getLogger('command-receiver-component')


def enqueue_message(command_queue, control_queue, message):
    CONTROL_PACKET_TYPES = ['pause', 'resume', 'erase']

    pkt_type = message.get('type', {})
    pkt_id = message.get('id', 'ID NOT FOUND')

    if pkt_type in CONTROL_PACKET_TYPES:
        logger.debug('Enqueueing Message ID {} to {}'.format(pkt_id, message))
        control_queue.put_nowait(message)

    else:
        logger.debug('Enqueueing Message ID {} to {}'.format(pkt_id, message))
        command_queue.put_nowait(message)

    logger.info('Enqueued Message ID {} to {}'.format(id, message))


class CommandReceiverComponent(wamp.ApplicationSession):
    """WAMP application session for Controller"""

    @asyncio.coroutine
    def onJoin(self, details):
        logger.info('CommandReceiverComponent has joined')

        command_queue = self.config.extra.get('command_queue')
        control_queue = self.config.extra.get('control_queue')

        if not command_queue:
            raise Exception('A control_queue must be set in self.config.extra')

        handle_message = partial(enqueue_message, command_queue, control_queue)
        yield from self.subscribe(handle_message, Config.BROWSER_TO_ROBOT_TOPIC)


if __name__ == '__main__':
    URL_TEMPLATE = "ws://{host}:{port}/{path}"

    url = URL_TEMPLATE.format(
        host='localhost',
        port='8000',
        path='ws'
    )

    command_queue = multiprocessing.Manager().Queue(50)

    runner = wamp.ApplicationRunner(
        url, realm='ot_realm',
        extra={'command_queue': command_queue}
    )
    runner.run(CommandReceiverComponent)
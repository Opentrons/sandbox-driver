import asyncio
from functools import partial
import logging
import multiprocessing
import uuid

from autobahn.asyncio import wamp

logger = logging.getLogger('command-reciever-component')


def enqueue_message(command_queue, message):
    id = str(uuid.uuid4())
    logger.debug('Enqueueing Message ID {} to {}'.format(id, message))
    command_queue.put_nowait((id, message))
    logger.info('Enqueued Message ID {} to {}'.format(id, message))
    return id


class CommandReceiverComponent(wamp.ApplicationSession):
    """WAMP application session for Controller"""

    @asyncio.coroutine
    def onJoin(self, details):
        logger.info('CommandRecieverComponent has joined')

        command_queue = self.config.extra.get('command_queue')

        if not command_queue:
            raise Exception('A command_queue must be set in self.config.extra')

        handle_message = partial(enqueue_message, command_queue)
        yield from self.subscribe(handle_message, 'com.opentrons.browser_to_robot')


if __name__ == '__main__':
    URL_TEMPLATE = "ws://{host}:{port}/{path}"

    url = URL_TEMPLATE.format(
        host='localhost',
        port='8000',
        path='ws'
    )

    command_queue = multiprocessing.Manager().Queue(50)

    runner = wamp.ApplicationRunner(url, realm='ot_realm')
    runner.run(CommandReceiverComponent)
import asyncio
from functools import partial
import logging
import uuid

from autobahn.asyncio import wamp

from config.settings import Config

logger = logging.getLogger('command-reciever-component')


def enqueue_message(command_queue, message):
    id = str(uuid.uuid4())
    logger.debug('Enqueueing Message ID {} to {}'.format(id, message))
    yield from command_queue.put((id, message))
    logger.info('Enqueued Message ID {} to {}'.format(id, message))
    return id


class CommandReceiverComponent(wamp.ApplicationSession):
    """WAMP application session for Controller"""

    @asyncio.coroutine
    def command_processor(self):
        """
        A coroutine which consumes tasks from the command queue and continuously
        processes them.
        :return:
        """
        command_queue = self.config.extra.get('command_queue')

        if not command_queue:
            raise Exception('A command_queue must be set in self.config.extra')

        while True:
            id, msg = yield from command_queue.get()
            logger.info('Dequeued Message ID: {} with {}'.format(id, msg))

            # TODO: execute robot message and publish result

            self.publish(Config.ROBOT_TO_BROWSER_TOPIC, msg)

    @asyncio.coroutine
    def onJoin(self, details):
        logger.info('CommandRecieverComponent has joined')

        # Register Task to handle processing command messages
        asyncio.async(self.command_processor())

        command_queue = self.config.extra.get('command_queue')

        if not command_queue:
            raise Exception('A command_queue must be set in self.config.extra')

        handle_message = partial(enqueue_message, command_queue)
        yield from self.subscribe(handle_message, Config.BROWSER_TO_ROBOT_TOPIC)


if __name__ == '__main__':
    URL_TEMPLATE = "ws://{host}:{port}/{path}"

    url = URL_TEMPLATE.format(
        host='localhost',
        port='8000',
        path='ws'
    )

    command_queue = asyncio.Queue()

    runner = wamp.ApplicationRunner(
        url, realm='ot_realm',
        extra={'command_queue': command_queue}
    )
    runner.run(CommandReceiverComponent)
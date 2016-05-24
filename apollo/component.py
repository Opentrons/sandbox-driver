#!/usr/bin/env python3

import asyncio
import logging
import uuid

from autobahn.asyncio import wamp

from apollo.session import Session


logger = logging.getLogger()


sessions = {}

def handle_message(message):
    print(message)
    if isinstance(message, dict):
        if 'start_session' in message:
            start_session(message)

        if 'close_session' in message:
            close_session(message)

def start_session(self, message):
    new_session_id = str(uuid.uuid4())
    new_session = Session(new_session_id)

    sessions[new_session_id] = new_session
    sessions[new_session_id].register_on_disconnect(on_session_disconnect)
    connect_session(new_session)

    # TODO: why do we need this???
    # publish the session_id
    # publish(msg='session_id',params=str(new_session_id))

def close_session(self, message):
    if message['close_session'] in sessions:
        sessions[message['close_session']].close()

def connect_session(self, session):
    session.connect()

def on_session_disconnect(session_id):
    """Delete session_id"""
    del sessions[session_id]


class ControllerComponent(wamp.ApplicationSession):
    """WAMP application session for Controller"""

    @asyncio.coroutine
    def onJoin(self, details):
        print('gonna join now...')
        yield from self.subscribe(handle_message, 'com.opentrons.browser_to_robot')


if __name__ == '__main__':
    URL_TEMPLATE = "ws://{host}:{port}/{path}"

    url = URL_TEMPLATE.format(
        host='localhost',
        port='8000',
        path='ws'
    )

    runner = wamp.ApplicationRunner(url, realm='ot_realm')
    runner.run(ControllerComponent)

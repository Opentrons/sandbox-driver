#!/usr/bin/env python3

import asyncio
import datetime
import json
import logging
import time
import traceback
import uuid

from autobahn.asyncio import wamp, websocket
from autobahn.asyncio.wamp import ApplicationRunner

from apollo.session import Session


logger = logging.getLogger()


class ControllerComponent(wamp.ApplicationSession):
    """WAMP application session for Controller"""


    def onConnect(self):
        """Callback fired when the transport this session will run over has been established."""
        self.join(u"ot_realm")


    @asyncio.coroutine
    def onJoin(self, details):
        """Callback fired when WAMP session has been established.

        May return a Deferred/Future.
        """
        if not self.factory._myAppSession:
            self.factory._myAppSession = self
        try:
            self.factory._crossbar_connected = True
        except AttributeError:
            pass
            # log here


        # def handshake(data):
        #     """Hook for factory to call _handshake"""
        #     try:
        #         self.factory._handshake(data)
        #     except AttributeError:
        #         pass
        #         # log here

        yield from self.subscribe(self.factory.handle_message, 'com.opentrons.driver_controller')
    

    def onLeave(self, details):
        """Callback fired when WAMP session has been closed.
        :param details: Close information.
        """
        if self.factory._myAppSession == self:
            self.factory._myAppSession = None
        try:
            self.disconnect()
        except:
            raise


    def onDisconnect(self):
        """Callback fired when underlying transport has been closed."""
        asyncio.get_event_loop().stop()
        try:
            self.factory._crossbar_connected = False
        except AttributeError:
            pass
            # log here


class Controller():

    # dictionary to hold sessions by session_id

    url_topic = 'driver.controller'

    def __init__(self, crossbar_host='localhost', crossbar_port=8080):

        # setup session factory for crossbar communication
        self._sessions = {}

        self._transport_factory = None
        self._session_factory = wamp.ApplicationSessionFactory()
        self._session_factory.session = ControllerComponent
        self._session_factory._myAppSession = None

        # track whether connected to crossbar for deciding whether to continue
        # trying to connect
        self._session_factory._crossbar_connected = False

        self._loop = asyncio.get_event_loop()

        self._transport = None
        self._protocol = None

        self.crossbar_host = crossbar_host
        self.crossbar_port = crossbar_port

    def connect(self, url_path='ws'):
        if self._transport_factory is None:
            URL_TEMPLATE = "ws://{host}:{port}/{path}"

            url = URL_TEMPLATE.format(
                host=self.crossbar_host,
                port=self.crossbar_port,
                path=url_path
            )

            self._transport_factory = websocket.WampWebSocketClientFactory(
                self._session_factory,
                url=url
            )

        # Add factory callbacks for WampComponent
        self._session_factory.handle_message = self.handle_message


        while self._session_factory._crossbar_connected == False:
            try:
                print('trying ',str(self.crossbar_host),' and ',str(self.crossbar_port))
                print('foo')
                coro = self._loop.create_connection(
                    self._transport_factory,
                    self.crossbar_host,
                    self.crossbar_port
                )
                transport, protocol = self._loop.run_until_complete(coro)

                self._transport = transport
                self._protocol = protocol

            except KeyboardInterrupt:
                self._session_factory._crossbar_connected = True
            except Exception as e:
                print(e)
                traceback.print_exc()

                # log here
            finally:
                time.sleep(6)



    def handle_message(self, message):
        if isinstance(message, dict):
            if 'start_session' in message:
                self.start_session(message)

            if 'close_session' in message:
                self.close_session(message)

    def start_session(self, message):
        new_session_id = str(uuid.uuid4())
        new_session = Session(new_session_id)
        
        self._sessions[new_session_id] = new_session
        self._sessions[new_session_id].register_on_disconnect(
            self._on_session_disconnect
        )
        self.connect_session(new_session)

        # publish the session_id
        self.publish(msg='session_id',params=str(new_session_id))

    def close_session(self, message):
        if message['close_session'] in self._sessions:
            self._sessions[message['close_session']].close()

    def connect_session(self, session):
        session.connect()

    def _make_connection(self):
        try:

            import pdb; pdb.set_trace()
        except Exception as e:
            logger.error("Error creating connection")

            raise e

    def _on_session_disconnect(self, session_id):
        """Delete session_id"""
        del self._sessions[session_id]


    def publish(self, msg=None, params=None, session_id='controller'):
        """Publish message to driver.controller url-topic "namespace" """
        if self._session_factory and msg and params:
            if self._session_factory._myAppSession:
                time_string = str(datetime.datetime.utcnow())
                message = {'time': time_string, 'session_id':session_id, 'data': {msg: params}}
                self._session_factory._myAppSession.publish(self.url_topic, json.dumps(message))
            else:
                raise Exception()
                # log here
        else:
            raise Exception()
            # log here
        return message, self.url_topic


if __name__ == '__main__':

    try:
        controller = Controller()
        controller.connect()
    except KeyboardInterrupt:
        pass
    finally:
        print('QUITTING!')












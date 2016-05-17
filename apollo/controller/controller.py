#!/usr/bin/env python3

from session.session import Session
import collections
import uuid
import asyncio
import datetime
import os
import time
from autobahn.asyncio import wamp, websocket
from autobahn.asyncio.wamp import ApplicationSession


class WampComponent(wamp.ApplicationSession):
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

    def __init__(self):

        # setup session factory for crossbar communication
        self._sessions = {}

        self._transport_factory = None
        self._session_factory = wamp.ApplicationSessionFactory()
        self._session_factory.session = WampComponent
        self._session_factory._myAppSession = None

        # track whether connected to crossbar for deciding whether to continue
        # trying to connect
        self._session_factory._crossbar_connected = False

        self._loop = asyncio.get_event_loop()

        self._transport = None
        self._protocol = None

        self.crossbar_host = None
        self.crossbar_port = None


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

    def _make_connection(
        self,
        url_protocol='ws',
        url_domain='0.0.0.0',
        url_port=8080,
        url_path='ws',
        debug=False,
        debug_wamp=False
    ):
        try:
            #yield from 
                #asyncio.ensure_future(
            self._transport, self._protocol = \
                self._loop.run_until_complete(
                    self._loop.create_connection(
                        self._transport_factory,
                        host=self.crossbar_host,
                        port=self.crossbar_port
                    )
                )
        except:
            raise
            # log here


    def connect(self, url_protocol='ws', url_domain='0.0.0.0', url_port=8080, url_path='ws', debug=False, debug_wamp=False):
        if self._transport_factory is None:
            
            self.crossbar_host = os.environ.get('CROSSBAR_HOST', url_domain)
            self.crossbar_port = os.environ.get('CROSSBAR_PORT', url_port)

            url = "{url_protocol}://{host}:{port}/{path}".format(
                url_protocol=url_protocol,
                host=self.crossbar_host,
                port=self.crossbar_port,
                path=url_path
            )

            self._transport_factory = websocket.WampWebSocketClientFactory(
                self._session_factory,
                url=url
                # debug=debug
                # debug_wamp=debug_wamp
            )

        # Add factory callbacks for WampComponent
        self._session_factory.handle_message = self.handle_message

            
        while self._session_factory._crossbar_connected == False:
            try:
                print('trying ',str(self.crossbar_host),' and ',str(self.crossbar_port))
                self._make_connection(url_domain=self.crossbar_host, url_port=self.crossbar_port)
            except KeyboardInterrupt:
                self._session_factory._crossbar_connected = True
            except:
                raise
                # log here
            finally:
                time.sleep(6)


    def _on_session_disconnect(self, session_id):
        """Delete session_id"""
        del self._sessions[session_id]


    def publish(self, msg=None, params=None, session_id='controller'):
        """Publish message to driver.controller url-topic "namespace" """
        if self._session_factory and msg and params:
            if self._session_factory._myAppSession:
                time_string = str(datetime.datetime.utcnow())
                message = {'time': time_string, 'session_id':session_id, 'data': {msg: param}}
                self._session_factory._myAppSession.publish(self.url_topic, json.dumps(message))
            else:
                raise
                # log here
        else:
            raise
            # log here
        return message, self.url_topic


    def test_handshake(self, data):
        self._handshake(self, data)
        
            




if __name__ == '__main__':

    try:
        controller = Controller()
        controller.connect()
    except KeyboardInterrupt:
        pass
    finally:
        print('QUITTING!')











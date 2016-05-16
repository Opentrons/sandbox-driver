#!/usr/bin/env python3

from session.session import Session
import collections
import uuid
import asyncio
import datetime
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


        def handshake(data):
            """Hook for factory to call _handshake"""
            try:
                self.factory._handshake(data)
            except AttributeError:
                pass
                # log here

        yield from self.subscribe(handshake, 'com.opentrons.driver_controller')
    

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
    _sessions = {}

    url_topic = 'driver.controller'

    def __init__(self):

        # setup session factory for crossbar communication
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


    def _handshake(self, data):
        """Handles starting and closing sessions"""
        if isinstance(data, dict):
            data_dict = collections.OrderedDict(json.loads(data.strip(), object_pairs_hook=collections.OrderedDict))

            if 'start_session' in data_dict:
                if data_dict['session'] in self._sessions:
                    # log here
                    # publish the session_id
                    self.publish(msg='session_id',params=str(new_session_id))
                else:
                    new_session_id = uuid.uuid4()
                    new_session = Session(new_session_id)
                    self._sessions[new_session_id] = new_session
                    self._sessions[new_session_id].register_on_discconect(self._on_session_disconnect)
                    self._sessions[new_session_id].connect()
                    # publish the session_id
                    self.publish(msg='session_id',params=str(new_session_id))
                    

            if 'close_session' in data_dict:
                if data_dict['close_session'] in self._sessions:
                    self._sessions[data_dict['close_session']].close()


    def _make_connection(self, url_protocol='ws', url_domain='0.0.0.0', url_port=8080, url_path='ws', debug=False, debug_wamp=False):
        try:
            
            #yield from 
                #asyncio.ensure_future(
            self._transport, self._transport = \
                self._loop.run_until_complete(
                                        self._loop.create_connection(
                                                                    self._transport_factory,
                                                                    host=crossbar_host,
                                                                    port=crossbar_port
                                                                    )
                                    )
        except:
            raise
            # log here


    def connect(self, url_protocol='ws', url_domain='0.0.0.0', url_port=8080, url_path='ws', debug=False, debug_wamp=False):
        if self._transport_factory is None:
            
            crossbar_host = os.environ.get('CROSSBAR_HOST', url_domain)
            crossbar_port = os.environ.et('CROSSBAR_PORT', url_port)

            url = url_protocol+'://'+crossbar_host+':'+str(crossbar_port)+'/'+url_path

            self._transport_factory = websocket.WampWebSocketClientFactory(self.session_factory,
                                                                            url=url,
                                                                            debug=debug,
                                                                            debug_wamp=debug_wamp)

        # Add factory callbacks for WampComponent
        self.session_factory._handshake = self.handshake
        self.session_factory._dispatch_message = self.dispatch_message

            
        while self._session_factor._crossbar_connected == False:
            try:
                self._make_connection(url_domain=crossbar_host, url_port=crossbar_port)
            except KeyboardInterrupt:
                self._session_factory._crossbar_connected = True
            except:
                pass
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
        pass
        
            



    
        












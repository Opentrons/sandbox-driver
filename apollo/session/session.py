#!/usr/bin/env python3

import json
import collections
import asyncio
import datetime
import uuid
import os

from driver.motor_controller import MotorController

from autobahn.asyncio import wamp, websocket
from autobahn.asyncio.wamp import ApplicationSession, ApplicationRunner


_motor_controller = None
# thinking about = {} for additional devices in { name : device } form
# ...baby steps



class WampComponent(wamp.ApplicationSession):
    """WAMP application session for Session"""


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
            self._url_topic = 'driver.'+self.factory._session_id
        except AttributeError:
            raise
            # log here


        def handle_data(data):
            """Hook for session/factory to handle data"""
            try:
                self.factory._handle_data(data)
            except AttributeError:
                raise
                # log here

        yield from self.subscribe(handle_data, self._url_topic)


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
            #log here


    def onDisconnect(self):
        """Callback fired when underlying transport has been closed."""
        #asyncio.get_event_loop().stop()
        try:
            self.factory._on_disconnect()
        except AttributeError:
            pass
            # log here


# store all sessions
_sessions = {}


class Session():

    def __init__(self, session_id : str, driver=None):

        global _motor_controller
        # what session am I?
        self._session_id = session_id
        self._url_topic = 'driver.'+self._session_id

        # Callback for when session disconnects
        self._on_disconnect = None

        # setup session factory for crossbar communication
        self._transport_factory = None
        self._session_factory = wamp.ApplicationSessionFactory()
        self._session_factory.session = WampComponent
        self._session_factory._myAppSession = None

        self._loop = asyncio.get_event_loop()

        self._transport = None
        self._protocol = None

        if driver:
            self._driver = driver
        elif not _motor_controller:
            # Initialize motor controller for ALL sessions
            self._driver = MotorController()
            _motor_controller = self._driver


    def connect(self,
                url_protocol='ws', 
                url_domain='0.0.0.0', 
                url_port=8080, 
                url_path='ws'):
        """Connect to Crossbar.io"""

        # CROSSBAR environment variables
        crossbar_host = os.environ.get('CROSSBAR_HOST', url_domain)
        crossbar_port = os.environ.get('CROSSBAR_PORT', url_port)

        if self._transport_factory is None:
            url = url_protocol+'://'+crossbar_host+':'+str(crossbar_port)+'/'+url_path

            self._transport_factory = websocket.WampWebSocketClientFactory(self._session_factory,
                                                                            url=url)

        
        # Add factory callbacks for WampComponent
        self._session_factory._handle_message = self.handle_message
        self._session_factory._on_disconnect = self.on_disconnect

        try:
            #yield from asyncio.ensure_future(
            self._transport, self._protocol = self._loop.run_until_complete(
                                                self._loop.create_connection(
                                                                            self._transport_factory, 
                                                                            host=crossbar_host, 
                                                                            port=crossbar_port
                                                                        )
                                                )
#                                                                            )
        except:
            raise
            # log here


    def handle_message(self, message):
        """First normalize the message and then send to motor-controller """
        nom_message = self._normalize_message(message)
        method = None
        if nom_message:
            method = getattr(self._motor_controller, norm_message.command)
            if not method:
                raise KeyError("Command not found.")
            else:
                method(norm_message.params)
        return nom_message, method


    def _normalize_message(self, message, **kwargs):
        """
        Normalize the message to pull out information to match the example below.
        Example command:

        message = { 'command': 'move', 'params': { 'x': 0, 'y': 0 } }
        """
        if isinstance(message, dict):
            if 'data' in message:
                data_dict = message['data']
                command, params = data_dict.items()[0]
                return_message = {'command': command, 'params': params}
                return return_message
        return None


    def register_on_disconnect(self, callback):
        """Register a callback for handling disconnect."""
        if callable(callback):
            self._on_disconect = callback
        return self._on_disconnect


    def on_disconnect(self):
        """Handle disconnect"""
        if self._on_disconnect:
            try:
                self._on_disconnect(self._session_id)
            except:
                raise
                # log here
        return self._session_id, self._on_disconnect


    def close(self):
        """Close this session."""
        if self._transport:
            self._transport.close()


    def publish(self, msg=None, params=None):
        """Publish message to session_id url-topic "namespace" """
        message = {}
        if self._session_factory and msg and params:
            if self._session_factory._myAppSession:
                time_string = str(datetime.datetime.utcnow())
                message = {'time': time_string, 'session_id':self._session_id, 'data': {msg: params}}
                self._session_factory._myAppSession.publish(self._url_topic, json.dumps(message))
            else:
                raise
                # log here
        else:
            raise
            # log here
        return message, self._url_topic












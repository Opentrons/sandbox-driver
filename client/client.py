#!/usr/bin/env python3




class WampComponent(wamp.ApplicationSession):
    """WAMP application session for Client
    """

    def onConnect(self):
        """Callback fired when the transport this session will run over has been established.
        """
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
            self._url_topic = 'driver.'+self.factory._session_id
        except AttributeError:
            # log here

        def _handle_data(data):
            """Hook for factory to handle data"""
            try:
                self.factory.handle_data(data)
            except AttributeError:
                # log here

        yield from self.subscribe(_handle_data, self._url_topic)


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
        #asyncio.get_event_loop().stop()
        try:
            self.factory._on_disconnect()
        except AttributeError:
            # log here












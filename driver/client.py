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
			pass
			# log here


		def dispatch(client_data):
			"""Hook for factory to call _handshake()
			"""
			print(datetime.datetime.now(),' - driver_client : WampComponent.handshake:')
			print('\n\targs: ',locals(),'\n')
			try:
				self.factory._handshake(client_data)
			except AttributeError:
				pass
				# log here

		yield from self.subscribe(dispatch, self._url_topic)


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
		"""Callback fired when underlying transport has been closed.
		"""
		print(datetime.datetime.now(),' - driver_client : WampComponent.onDisconnect:')
		asyncio.get_event_loop().stop()
		crossbar_connected = False
		try:
			self.factory._crossbar_connected = False
		except AttributeError:
			pass
			# log here











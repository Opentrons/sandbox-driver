#!/usr/bin/env python3

# https://medium.com/@theHQ/using-mock-and-trial-to-create-unit-tests-for-crossbar-applications-867e5b941cf2#.aru3coz3i
# http://python-mock.sourceforge.net/
# https://github.com/python/asyncio/blob/master/tests/test_base_events.py

import unittest
import uuid
import asyncio
import os
import socket
import datetime
from session.session import Session

#from twisted.trial import unittest
#import mock



session_id = str(uuid.uuid4())
crossbar_host = os.environ.get('CROSSBAR_HOST', '127.0.0.1')
crossbar_port = os.environ.get('CROSSBAR_PORT', 8080)

class SessionTestCase(unittest.TestCase):

# ensure_future and create_connection - return transport and protocol
# ~~~ @patch_socket
# self._loop.create_connection = mock.MagicMock(side_effect=self.mock_create_connection)
# self.ensure_future = mock.MagicMock(side_effect=self.mock_ensure_future)



	def mock_ensure_future(self):
		pass


	def assertSomething(self):
		pass


class SessionTest(SessionTestCase):

	addr = []
	test_session_id = 'test_session_id'
	test_message_1 = {'time':str(datetime.datetime.utcnow()),
					'session_id':test_session_id,
					'data':{'move',{'x':123.456,'y':7.89}}}

	@asyncio.coroutine
	def handle_client(self, client_reader, client_writer):
		data = yield from client_reader.readline()
		client_writer.write(data)
		yield from client_writer.drain()
		client_writer.close()

	def handle_client_callback(self, client_reader, client_writer):
		self.loop.create_task(self.handle_client(client_reader,
												 client_writer))

	def setUp(self):
		print()
		print('setUp')
		sock = socket.socket()
		sock.bind(('127.0.0.1', 0))
		self.loop = asyncio.new_event_loop()
		#asyncio.set_event_loop(None)
		self.addr = sock.getsockname()
		print('addr=',self.addr)
		sock.close()
		self.server = self.loop.run_until_complete(
													asyncio.start_server(self.handle_client_callback,
													host=self.addr[0], port=self.addr[1],
													loop=self.loop)
													)
		self.sesh = Session(session_id)


	def tearDown(self):
		if self.server is not None:
			self.server.close()
			self.loop.run_until_complete(self.server.wait_closed())
			self.server = None


	#def test_connect(self):
	#	self.sesh.connect()


	def test_handle_message(self):
		nom_message, method = self.sesh.handle_message(self.test_message_1)
		self.assertTrue(True)


	def test_register_on_disconnect(self):
		
		def my_on_disconnect(session_id):
			print('Session disconnected')
			print('by session_id '+session_id)

		self.sesh.register_on_disconnect(my_on_disconnect)



	def test_on_disconnect(self):

		def my_on_disconnect(session_id):
			print('Session disconnected')
			print('by session_id '+session_id)

		self.sesh.register_on_disconnect(my_on_disconnect)

		self.sesh.connect(url_domain=self.addr[0], 
							url_port=self.addr[1])

		self.sesh.close()

		
		



	def test_close(self):
		self.sesh.connect(url_domain=self.addr[0], 
							url_port=self.addr[1])
		self.sesh.close()
		self.assertTrue(True)


	def test_publish(self):
		self.sesh.connect(url_domain=self.addr[0], 
							url_port=self.addr[1])
		pass


	def test_connect_failure(self):
		if self.server is not None:
			self.server.close()
			self.loop.run_until_complete(self.server.wait_closed())
			self.server = None
		self.sesh.connect(url_domain=self.addr[0], 
							url_port=self.addr[1])




if __name__ == '__main__':
    unittest.main()

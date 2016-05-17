#!/usr/bin/env python3

# https://medium.com/@theHQ/using-mock-and-trial-to-create-unit-tests-for-crossbar-applications-867e5b941cf2#.aru3coz3i
# http://python-mock.sourceforge.net/
# https://github.com/python/asyncio/blob/master/tests/test_base_events.py

import asyncio
import datetime
import os
import unittest
from unittest import mock
import uuid

from apollo import utils
from apollo.session import Session


session_id = str(uuid.uuid4())
crossbar_host = os.environ.get('CROSSBAR_HOST', '127.0.0.1')
crossbar_port = os.environ.get('CROSSBAR_PORT', 8080)


# ensure_future and create_connection - return transport and protocol
# ~~~ @patch_socket
# self._loop.create_connection = mock.MagicMock(side_effect=self.mock_create_connection)
# self.ensure_future = mock.MagicMock(side_effect=self.mock_ensure_future)


class SessionTest(unittest.TestCase):
    def setUp(self):
        self.test_session_id = 'test_session_id'
        self.test_message_1 = {
            'time': str(datetime.datetime.utcnow()),
            'session_id': self.test_session_id,
            'data': {'move': {'x': 123.456, 'y': 7.89}}
        }

        self.addr = utils.get_free_os_address()

        self.loop = asyncio.get_event_loop()
        asyncio.set_event_loop(None)

        self.server = self.loop.run_until_complete(
            asyncio.start_server(
                self.handle_client_callback,
                host=self.addr[0], port=self.addr[1],
                loop=self.loop
            )
        )
        self.session = Session(session_id, self.loop)


    def handle_client_callback(self, client_reader, client_writer):
        @asyncio.coroutine
        def handle_client(client_reader, client_writer):
            data = yield from client_reader.readline()
            client_writer.write(data)
            yield from client_writer.drain()
            client_writer.close()

        self.loop.create_task(handle_client(client_reader, client_writer))

    def tearDown(self):
        self.server.close()
        self.loop.run_until_complete(self.server.wait_closed())
        self.server = None

    def test_register_on_disconnect(self):
        on_disconnect = mock.Mock()
        self.session.register_on_disconnect(on_disconnect)
        self.assertEqual(self.session._on_disconnect, on_disconnect)

    def test_on_disconnect(self):
        on_disconnect = mock.Mock()
        self.session.register_on_disconnect(on_disconnect)
        self.session.on_disconnect()
        self.assertTrue(on_disconnect.called)

    # def test_close(self):
    #     self.session.connect(url_domain=self.addr[0], url_port=self.addr[1])
    #     self.session.close()
    #     self.assertTrue(True)

    # def test_publish(self):
    #     self.session.connect(url_domain=self.addr[0], url_port=self.addr[1])

    # def test_connect_failure(self):
    #     if self.server is not None:
    #         self.server.close()
    #         self.loop.run_until_complete(self.server.wait_closed())
    #         self.server = None
    #
    #     self.session.connect(url_domain=self.addr[0], url_port=self.addr[1])

if __name__ == '__main__':
    unittest.main()

import asyncio
import unittest
from unittest.mock import Mock
import apollo.utils

from apollo.smoothie import SmoothieCom


mock_messages_in = []
mock_messages_out = []


@asyncio.coroutine
def mock_write_and_drain(gcode):
    print('should be appending gcode to mock_messages_out here')
    mock_messages_out.append(gcode)
    return gcode


class MockSmoothieServer():
    
    def __init__(self, host, port, full_smoothie_mock=False, loop=None):
        self.server = None
        self.host = host
        self.port = port
        self.full_smoothie_mock = full_smoothie_mock
        if not loop:
            self.loop = asyncio.get_event_loop()
        self.clients = {}
        self.mock_initiation = ['Smoothie', 'ok']

    def _accept_client(self, client_reader, client_writer):
        task = asyncio.Task(self._handle_client(client_reader, client_writer))
        self.clients[task] = (client_reader, client_writer)
        client_writer.write('{}{}'.format(self.mock_initiation.pop(0),'\r\n').encode('utf-8'))
        yield from client_writer.drain()
        client_writer.write('{}{}'.format(self.mock_initiation.pop(0),'\r\n').encode('utf-8'))
        yield from client_writer.drain()

        def client_done(task):
            del self.clients[task]

        task.add_done_callback(client_done)

    @asyncio.coroutine
    def _handle_client(self, client_reader, client_writer):
        
        if self.full_smoothie_mock == True:
            while True:
                data = (yield from client_reader.readline()).decode()
                if not data:
                    break
            
            yield from client_writer.drain()

        else:
            # LOAD LOCAL COPY OF MOCK MESSAGES IN (MESSAGES OUT FROM SMOOTHIE)
            local_mock_messages_in = []
            [local_mock_messages_in.append(x) for x in mock_messages_in]
            
            local_mock_messages_in.append('feedback engaged\r\n')
            local_mock_messages_in.append('ok {"stuff":stuff}\r\n')
            local_mock_messages_in.append('{"stat":0}\r\n')
            local_mock_messages_in.append('feedback disengaged\r\n')

            while True:
                data = (yield from client_reader.readline()).decode()
                if not data:
                    break
                while len(local_mock_messages_in) > 0:
                    client_writer.write('{}{}'.format(local_mock_messages_in.pop(0),'\r\n').encode('utf-8'))
                    yield from client_writer.drain()
                else:
                    client_writer.write('EMPTY LIST\r\n'.encode('utf-8'))

            yield from client_writer.drain()

    def start(self, loop):
        self.server = loop.run_until_complete(
            asyncio.streams.start_server(
                self._accept_client,
                self.host,
                self.port,
                loop=self.loop
            )
        )

    def stop(self, loop):
        if self.server is not None:
            self.server.close()
            loop.run_until_complete(self.server.wait_closed())
            self.server = None


class SmoothieComSendTest(unittest.TestCase):

    def setUp(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        mock_address = apollo.utils.get_free_os_address()
        self.mock_server = MockSmoothieServer(mock_address[0], mock_address[1])
        self.mock_server.start(self.loop)
#        mocked._read = mock_read
        self.mock_smc = SmoothieCom(
                                mock_address[0],
                                mock_address[1]
                            )
        self.mock_smc.write_and_drain = mock_write_and_drain
        mock_messages_out = []

    def tearDown(self):
        self.mock_server.stop(self.loop)

    def test_connect(self):
        """ TEST CONNECTING """
        loop = asyncio.get_event_loop()
        res = loop.run_until_complete(self.mock_smc.connect())

    def test_send_M114_gcode(self):
        """ TEST SENDING M114 """
        expected_messages_out = ['M114\r\n']
        loop = asyncio.get_event_loop()
        res = loop.run_until_complete(self.mock_smc.connect())
        if res:
            res = loop.run_until_complete(self.mock_smc.send('M114'))
        print('Exptected messages out:', expected_messages_out)
        print('Actual Messages out:', mock_messages_out)
        self.assertEqual(expected_messages_out, mock_messages_out)
        
if __name__ == '__main__':
    unittest.main()


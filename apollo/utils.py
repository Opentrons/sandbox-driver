import asyncio
from concurrent.futures import ThreadPoolExecutor
import socket
from unittest import mock



def get_free_os_address():
    sock = socket.socket()
    sock.bind(('127.0.0.1', 0))
    address = sock.getsockname()
    sock.close()
    return address


@asyncio.coroutine
def coro_queue_get(queue, loop=None):
    loop = loop or asyncio.get_event_loop()
    return (yield from loop.run_in_executor(ThreadPoolExecutor(1), queue.get))


def mock_coro_factory():
    mock_obj = mock.Mock()

    @asyncio.coroutine
    def mocked_coro(*args, **kwargs):
        mock_obj(*args, **kwargs)

    return (mock_obj, mocked_coro)
import asyncio
from concurrent.futures import ThreadPoolExecutor
import queue
import socket


def get_free_os_address():
    sock = socket.socket()
    sock.bind(('127.0.0.1', 0))
    address = sock.getsockname()
    sock.close()
    return address


@asyncio.coroutine
def coro_queue_get(q, loop=None):
    loop = loop or asyncio.get_event_loop()
    return (yield from loop.run_in_executor(ThreadPoolExecutor(1), q.get))

def flush_queue(q):
    items_cnt = q.qsize()

    while items_cnt > 0:
        try:
            q.get_nowait()
            items_cnt -= 1
        except queue.Empty:
            break


import socket


def get_free_address():
    sock = socket.socket()
    sock.bind(('127.0.0.1', 0))
    address = sock.getsockname()
    sock.close()
    return address
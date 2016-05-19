import asyncio
import logging


logger = logging.getLogger()

# smoothie = SmoothieTalker()
# smoothie.connect()
#
# smoothie.send("gcode")
# res = smoothie.get()
#
#
# q = []
#
#
# while True:
#     res = yield smoothie.read()
#     print(res)
#
#     q.append(input())
#
#     while q:
#         if smoothie.is_ready():
#             yield smoothie.send(q.pop(0))
#             print(yield from smoothie.read())
#         else:
#             cnt += 1
#             sleep(1)
#
#
# class SmoothieTestCase(...)
#     def test_send(self):
#         smoothie.transport.write = Mock(return_value={stat: ok})
#         smoothie.send()
#
#         assert smoothie.transport.write.called == True
#
#     def read(self):
#         pass
#



class SmoothieBoard(object):
    def __init__(self, host, port, loop):
        self.host = host
        self.port = port
        self.loop = loop

    def connect(self):
        try:
            reader, writer = yield from asyncio.open_connection(
                self.host,
                self.port,
                self.loop
            )
        except OSError as e:
            logger.log("foo")
            raise e

        self.reader = reader
        self.writer = writer

        yield from self.smoothie_handshake()

    @asyncio.coroutine
    def smoothie_handshake(self):
        status_dict = yield from self.read()

    @asyncio.coroutine
    def send(self, gcode, response_handler):
        yield from self.writer.write(gcode.encode())

        response_handler.send('start', gcode)

        done = False
        res = []

        while not done:
            data = (yield from self.read())
            response_handler.send(data)

            res.append(data)

            if data == "stat 0":
                done = True

        response_handler.send(None)

        return

    @asyncio.coroutine
    def _read(self):
        return (yield from asyncio.wait_for(self.reader.readline(), timeout=2))

    def is_ready(self):
        return self.status == "ok"

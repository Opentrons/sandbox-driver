import asyncio
import logging
import json
import concurrent

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
    def __init__(self, host, port, loop, feedback=False):
        self.host = host
        self.port = port
        self.loop = loop
        self.feedback = feedback

    def connect(self):
        try:
            reader, writer = yield from asyncio.open_connection(
                host=self.host,
                port=self.port,
                loop=self.loop
            )
        except OSError as e:
            logger.log("foo")
            raise e

        self.reader = reader
        self.writer = writer
        return (yield from self.smoothie_handshake())

    @asyncio.coroutine
    def smoothie_handshake(self):
        smoothie_ok = [False, False]

        while not (smoothie_ok[0] and smoothie_ok[1]):
            data = yield from self._read()
            if data == 'Smoothie':
                smoothie_ok[0] = True
            elif data == 'ok':
                smoothie_ok[1] = True

        return smoothie_ok[0] and smoothie_ok[1]

    @asyncio.coroutine
    def send(self, gcode, response_handler):
        self.writer.write(gcode.encode()) 
        yield from self.writer.drain()

        if response_handler:
            response_handler.send('start', gcode)

        done = False
        res = []

        while not done:
            data = (yield from self._read())
            if data == None:
                done = True
                break

            if response_handler:
                response_handler.send(data)

            if not self.feedback:
                done = True
                break
            
            # check whether JSON/dict format
            if data.find('{') > 0:
                # pull out any text data at beginning
                text = data[:data.find('{')]
                res.append(text)

                # convert to JSON object
                jtxt = data[data.find('{'):]
                res.append(jtxt)
                jobj = json.loads(jtxt)

                # check whether has "stat" and value if so
                if 'stat' in jobj:
                    if jobj['stat'] == 0:
                        done = True

        if response_handler:
            response_handler.send(None)

        return res

    @asyncio.coroutine
    def _read(self):
        try:
            data = yield from asyncio.wait_for(self.reader.readline(), timeout=2)
            return data.decode().strip()
        except concurrent.futures.TimeoutError:
            return None

    def is_ready(self):
        return self.status == "ok"

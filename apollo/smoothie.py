import asyncio
import logging
import json
import concurrent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()


class SmoothieCom(object):
    def __init__(self, host, port, loop=None, is_feedback_enabled=False):
        self.host = host
        self.port = port
        self.loop = loop or asyncio.get_event_loop()
        self.is_feedback_enabled = is_feedback_enabled

    def connect(self):
        try:
            reader, writer = yield from asyncio.open_connection(
                host=self.host,
                port=self.port,
                loop=self.loop
            )
        except OSError as e:
            logger.error("Did not connect")
            #raise e
            return False

        self.reader = reader
        self.writer = writer
        return (yield from self.smoothie_handshake())

    @asyncio.coroutine
    def smoothie_handshake(self):
        has_smoothie = False
        has_ok = False

        first_message = yield from self._read()
        second_message = yield from self._read()

        return (first_message == 'Smoothie') and (second_message == 'ok')

    @asyncio.coroutine
    def send(self, gcode, response_handler):
        delimiter = '\r\n'
        gcode = gcode.strip() + delimiter
        self.writer.write(gcode.encode('utf-8')) 
        yield from self.writer.drain()

        if response_handler:
            response_handler.send('start', gcode)

        done = False
        res = []


        tries_left = 3

        while tries_left:
            response = (yield from self._read())
            if not response:
                tries_left -= 1
                yield from asyncio.sleep(0.2)
                continue
            else:
                tries_left = 0

            if gcode == 'M114':
                status, data = response.split(' ')
                data_json = json.loads(data)

            if gcode == ' ':
                pass
            print('response is', response)

            if ' ' in response:
                pass
            else:
                status, data = 'ok', response


            print(data_json)

            #if data == None:
            #    done = True
            #    break

            #if response_handler:
            #    response_handler.send(data)

            #if not self.feedback:
            #    done = True
            #    break
            
            # check whether JSON/dict format
            #if data.find('{') > 0:
                # pull out any text data at beginning
            #    text = data[:data.find('{')]
            #    res.append(text)

                # convert to JSON object
            #    jtxt = data[data.find('{'):]
            #    res.append(jtxt)
            #    jobj = json.loads(jtxt)

                # check whether has "stat" and value if so
            #    if 'stat' in jobj:
            #        if jobj['stat'] == 0:
            #            done = True

        #if response_handler:
        #    response_handler.send(None)

        return res

    @asyncio.coroutine
    def _read(self):
        try:
            data = yield from asyncio.wait_for(self.reader.readline(), timeout=2)
            return data.decode().strip()
        except concurrent.futures.TimeoutError:
            print('Timeout Error')
            return None

    def is_ready(self):
        return self.status == "ok"


@asyncio.coroutine
def repl(smc):
    while True:
        req = input('>>> ').strip()
        res = yield from smc.send(req, None)
        print(res)

if __name__ == '__main__':
    smc = SmoothieCom('localhost',3335)
    loop = asyncio.get_event_loop()
    res = loop.run_until_complete(smc.connect())
    if res:
        loop.run_until_complete(repl(smc))
    print(res)

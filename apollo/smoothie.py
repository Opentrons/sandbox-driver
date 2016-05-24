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
            raise e
            # return False

        self.reader = reader
        self.writer = writer
        return (yield from self.smoothie_handshake())

    @asyncio.coroutine
    def smoothie_handshake(self):
        first_message = yield from self._read()
        second_message = yield from self._read()
        return (first_message == 'Smoothie') and (second_message == 'ok')

    @asyncio.coroutine
    def send(self, gcode, response_handler):


        # Turn on feedback
        yield from self.turn_on_feedback()

        gcode = gcode.strip()
        delimiter = '\r\n'

        # Add delimiter to gcode for Smoothie board
        delimited_gcode = gcode.strip() + delimiter

        self.writer.write(delimited_gcode.encode('utf-8'))
        yield from self.writer.drain()

        if response_handler:
            response_handler.send('start', gcode)

        is_gcode_done = False

        data_as_json = None

        while True:
            response = (yield from self._read())
            print('response is', response)

            # Handle M114 GCode
            if gcode == 'M114' and not is_gcode_done:
                try:
                    status, data = response.split(' ')
                    data_as_json = json.loads(data)
                    is_gcode_done = True
                    print('formatted data', data_as_json)
                except ValueError:
                    pass

            # Handle G0 GCode
            if gcode.startswith('G0') and not is_gcode_done:
                if response == '{"stat":0}':
                    is_gcode_done = True

            # Handle G1 GCode
            if gcode.startswith('G92') and not is_gcode_done:
                if response == 'ok':
                    is_gcode_done = True

            if response == '{"stat":0}':
                break


        yield from self.turn_off_feedback()

        return data_as_json

        #if response_handler:
        #    response_handler.send(None)



    @asyncio.coroutine
    def turn_on_feedback(self):
        yield from self.send_feedback_gcode('M62\r\n', 'feedback engaged')

    @asyncio.coroutine
    def turn_off_feedback(self):
        yield from self.send_feedback_gcode('M63\r\n', 'feedback disengaged')

    @asyncio.coroutine
    def send_feedback_gcode(self, delimited_gcode, expected_response_msg):

        self.writer.write(delimited_gcode.encode('utf-8'))
        yield from self.writer.drain()

        while True:
            response = (yield from self._read())
            print(response)
            if response == expected_response_msg:
                yield from self._read() # Next message is an ok message
                break
            else:
                yield from asyncio.sleep(0.001)

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

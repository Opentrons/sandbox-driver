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

        self.reader = reader
        self.writer = writer
        return (yield from self.smoothie_handshake())

    def get_delimited_gcode(self, gcode):
        """
        # Add delimiter to gcode for Smoothie board
        """
        return gcode.strip() + '\r\n'



    @asyncio.coroutine
    def smoothie_handshake(self):
        first_message = yield from self._read()
        second_message = yield from self._read()
        return (first_message == 'Smoothie') and (second_message == 'ok')

    @asyncio.coroutine
    def send(self, gcode, response_handler):
        yield from self.turn_on_feedback()

        delimited_gcode = self.get_delimited_gcode(gcode)

        # TODO: refactor into write and drain method coro
        self.writer.write(delimited_gcode.encode('utf-8'))
        yield from self.writer.drain()

        # TODO: Make this async?
        if response_handler:
            response_handler.send('start', gcode)


        is_gcode_done = False
        data_as_json = None

        while True:
            response = (yield from self._read())

            # TODO: do proper logging and remove print statements
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


@asyncio.coroutine
def repl(smc):
    while True:
        req = input('>>> ').strip()
        res = yield from smc.send(req, None)
        print(res)

if __name__ == '__main__':
    smc = SmoothieCom('localhost', 3335)
    loop = asyncio.get_event_loop()
    res = loop.run_until_complete(smc.connect())
    if res:
        loop.run_until_complete(repl(smc))
    print(res)

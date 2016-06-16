#!/user/bin/env python3

import asyncio
import logging
import json
import concurrent
import serial_asyncio

from config.settings import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

class SmoothieMaxReadsException(Exception):
    def __init__(self, gcode=None):
        self.gcode = gcode


class SmoothieCom(object):
    """ Class for communication with a Smoothieboard
    
        - Instantiate a SmoothieCom object with a device and optionally an event loop.
        
        - Call/Schedule connect to open a connection.
        
        - Once a connection is established, call/schedule send with an optional response_handler for 
          handling responses as the command executes.

        - Call halt() for an emergency Halt and send('M999') to Reset from Halt
    """
    def __init__(self, device, loop=None):
        self.device = device
        self.loop = loop or asyncio.get_event_loop()
        self._halt_state = 0 # 0 = Not Halted, 1 = To Be Halted, 2 = Halted

    @asyncio.coroutine
    def connect(self):
        """ Connect to Smoothie """
        try:
            reader, writer = yield from serial_asyncio.open_serial_connection(
                #self.device,
                baudrate=115200#,
                #loop=self.loop
            )
        except OSError as e:
            logger.error("Failed to connect to Smoothieboard")
            raise e
        self.reader = reader
        self.writer = writer
        return (yield from self.smoothie_handshake())

    def get_delimited_gcode(self, gcode):
        """ Add delimiter to gcode for Smoothie board """
        return gcode.strip() + '\r\n'

    def halt(self):
        """ Emergency halt """
        self.halt_state = 1

    def check_halt_state(self, gcode=''):
        """ Check halt state """
        if self.halt_state == 1:
            logger.info('Halting... sending M112')
            self.halt_state = 2
            self.writer.write('M112'.encode('utf-8'))
            yield from self.writer.drain()
            return true
        elif self.halt_state == 2 and gcode != 'M999':
            logger.info('Halted')
            return true
        return false

    @asyncio.coroutine
    def smoothie_handshake(self):
        first_message = yield from self._read()
        second_message = yield from self._read()
        return (first_message == 'Smoothie') and (second_message == 'ok')

    @asyncio.coroutine
    def write_and_drain(self, message):
        try:
            if check_halt_state(message):
                return
            self.writer.write(message.encode('utf-8'))
            yield from self.writer.drain()
        except Exception as exc:
            logger.error('Exception in write_and_drain: {}'.format(exc))

    @asyncio.coroutine
    def send(self, gcode, response_handler=None):
        """ Send Gcode
            
            Send Gcode as a string. Send will return with a response list. 
            In most cases the list will be empty. A line ending ('\r\n') will
            be added automatically. Set response_handler to a coroutine
            accepting a string description as the first argument and the message
            back as the second argument if you want it to handle responses 
            from the SmoothieBoard.
        """
        if not isinstance(gcode, str):
            logger.error('Gcode must be string')
            raise TypeError('Gcode must be string')
            return None
        # Skip if command is EMERGENCY STOP or RESET FROM HALT
        if not (gcode == 'M112' or gcode == 'M999'):
            yield from self.turn_on_feedback()

        if gcode == 'M999':
            self.halt_state = 0
            logger.info('Resetting from Halt')

        delimited_gcode = self.get_delimited_gcode(gcode)

        yield from self.write_and_drain(delimited_gcode)

        if response_handler and asyncio.iscoroutinefunction(response_handler):
            yield from response_handler('start', gcode)

        is_gcode_done = False
        json_result = None

        read_attempts = 0
        while not is_gcode_done:
            read_attempts += 1
            if read_attempts > Config.MAX_SEND_READS:
                raise SmoothieMaxReadsException(gcode) 
                break

            response = (yield from self._read())
            logger.info('Smoothie send response: {}'.format(response))

            if response is None:
                logger.warning('response is None')
                break

            if response == '{"!!":"!!"}':
                logger.info('HALT STATE, call M999')
                break

            # Handle M114 GCode
            if gcode == 'M114' and not is_gcode_done:
                try:
                    status, data = response.split(' ')
                    json_result = json.loads(data)
                    is_gcode_done = True
                except ValueError:
                    pass

            # Handle G0 GCode
            if gcode.startswith('G0') and not is_gcode_done:
                if response_handler and asyncio.iscoroutinefunction(response_handler):
                    yield from response_handler('gcode progress', response)

                if response == '{"stat":0}':
                    is_gcode_done = True

            # Handle G28
            if gcode.startswith('G28') and not is_gcode_done:
                if response == '{"stat":0}':
                    is_gcode_done  = True
        
            # Handle G92 GCode
            if gcode.startswith('G92') and not is_gcode_done:
                if response == 'ok':
                    is_gcode_done = True

            # Handle G90
            if gcode.startswith('G90') and not is_gcode_done:
                if response == 'ok':
                    is_gcode_done = True

            # Handle G91
            if gcode.startswith('G91') and not is_gcode_done:
                if response == 'ok':
                    is_gcode_done = True

            # Handle M112
            if gcode.startswith('M112') and not is_gcode_done:
                if response.startswith('ok'):
                    is_gcode_done = True

            # Handle M119
            if gcode.startswith('M119') and not is_gcode_done:
                try:
                    json_result = json.loads(response)
                    is_gcode_done = True
                except ValueError:
                    pass

            # Handle M199
            if gcode.startswith('M199') and not is_gcode_done:
                try:
                    json_result = json.loads(response)
                    is_gcode_done = True
                except ValueError:
                    pass

            # Handle M204
            if gcode.startswith('M204') and not is_gcode_done:
                try:
                    #status, data = response.split(' ')
                    json_result = json.loads(response)
                    is_gcode_done = True
                except ValueError:
                    pass

            # Handle: M999
            if gcode.startswith('M999') and not is_gcode_done:
                if response == 'ok':
                    is_gcode_done = True

            if response == '{"stat":0}':
                break

        if not (gcode == 'M112'):
            yield from self.turn_off_feedback()

        return json_result

    @asyncio.coroutine
    def turn_on_feedback(self):
        yield from self.send_feedback_gcode('M62\r\n', 'feedback engaged')

    @asyncio.coroutine
    def turn_off_feedback(self):
        yield from self.send_feedback_gcode('M63\r\n', 'feedback disengaged')

    @asyncio.coroutine
    def send_feedback_gcode(self, delimited_gcode, expected_response_msg):
        
        yield from self.write_and_drain(delimited_gcode)

        read_attempts = 0
        while read_attempts < Config.MAX_FEEDBACK_READS:
            read_attempts += 1
            try:
                response = (yield from self._read())
                logger.info('Smoothie send_feedback_gcode response(1): {}'.format(response))
            except:
                logger.error('Error getting "response" - Breaking send_feedback_gcode loop')
                raise
                break
            
            if response == expected_response_msg:
                try:
                    followup_response = (yield from self._read()) # Next message is an ok messagei
                    logger.info('Smoothie send_feedback_gcode response(2): {}'.format(followup_response))
                except:
                    raise
                # break at this level because it is also for response == expected_response_msg
                break
            # Handle HALT STATE response
            elif response == '{"!!":"!!"}':
                logger.warning('HALT STATE, call M999')
                break
            else:
                yield from asyncio.sleep(0.001)
            if read_attempts == Config.MAX_FEEDBACK_READS:
                logger.warning('MAX_FEEDBACK_READS reached: {} read attempts'.format(read_attempts))

    @asyncio.coroutine
    def _read(self):
        try:
            if check_halt_state():
                return
            data = yield from asyncio.wait_for(self.reader.readline(), timeout=2)
            return data.decode().strip()
        except concurrent.futures.TimeoutError:
            logger.error('concurrent.futures.TimeoutError in _read')
            raise
        except ConnectionResetError:
            logger.error('ConnectionResetError in _read')
            raise


# REPL app for quick testing
@asyncio.coroutine
def test_response_handler(description, message):
    print(' description => {}'.format(description))
    print(' message     => {}'.format(message))

@asyncio.coroutine
def repl(smc):
    while True:
        req = input('>>> ').strip()
        res = yield from smc.send(req, test_response_handler)
        print('res:', res)

if __name__ == '__main__':
    smc = SmoothieCom('/dev/tty.usbmodem1421')
    loop = asyncio.get_event_loop()
    res = loop.run_until_complete(smc.connect())
    if res:
        loop.run_until_complete(repl(smc))
    print('final result:', res)

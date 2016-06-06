import asyncio

from apollo.smoothie import SmoothieCom


class CommandProcessor(object):
    def __init__(self):
        self.smoothie_com = SmoothieCom('localhost', 8000)

    @asyncio.coroutine
    def connect(self):
        yield from self.smoothie_com.connect()

    def process(self, command):
        if command['type'] == 'move':
            data = command.get('data', {})

            args = ['X', 'Y', 'Z', 'a', 'b']

            gcode = ''

            for arg in args:
                gcode += (arg + '')

            gcode = (
                'G0 ' +

                ' '.join(
                    ["{}{}".format(str(axis), str(val)) for axis, val in data.items()
                ])
            )

            self.smoothie_com.send('G90')
            self.smoothie_com.send(gcode)


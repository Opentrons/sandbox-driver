import asyncio

from apollo.smoothie import SmoothieCom


class CommandProcessor(object):
    def __init__(self):
        self.smoothie_com = SmoothieCom('localhost', 8000)

    @asyncio.coroutine
    def connect(self):
        yield from self.smoothie_com.connect()

    @asyncio.coroutine
    def send_gcode(self,string):

        # TODO: smoothie_com.send is asynchronous, and must use 'yield from'
        #       however, for testing, mock() is being used, so we call it synchronously

        self.smoothie_com.send(string)

    @asyncio.coroutine
    def process(self, command):

        com_type = command.get('type', None)
        com_data = command.get('data', {})

        if (com_type=='move' or com_type=='move_to') and com_data:

            coord_types = {
                'move' : 'G91',
                'move_to' : 'G90'
            }

            axis = ['X', 'Y', 'Z', 'a', 'b']

            gcode = 'G0'

            for ax in axis:
                # accept both lower and upper case axis
                val = com_data.get(ax.lower()) if com_data.get(ax.lower())!=None else com_data.get(ax.upper())
                
                if val!=None:
                    gcode += ' '                    # ascii space
                    gcode += ax                     # axis
                    gcode += str(val)               # value

            yield from self.send_gcode(coord_types[com_type])   # relative
            yield from self.send_gcode(gcode)

        elif com_type=='speed' and com_data:

            if com_data.get('xyz') != None:
                yield from self.send_gcode('F{0}'.format(com_data['xyz']))
            if com_data.get('a') != None:
                yield from self.send_gcode('a{0}'.format(com_data['a']))
            if com_data.get('b') != None:
                yield from self.send_gcode('b{0}'.format(com_data['b']))

        elif com_type=='acceleration' and com_data:

            gcode = 'M204'

            if com_data['xy'] != None:
                gcode += ' S{}'.format(com_data['xy'])
            if com_data['z'] != None:
                gcode += ' Z{}'.format(com_data['z'])
            if com_data['a'] != None:
                 gcode += ' A{}'.format(com_data['a'])
            if com_data['b'] != None:
                 gcode += ' B{}'.format(com_data['b'])

            if gcode!='M204':
                yield from self.send_gcode(gcode)

        elif com_type=='home':

            gcode = 'G28'
            
            if com_data:
                for n in com_data:
                    gcode += ' '
                    gcode += n.upper()

            yield from self.send_gcode(gcode)

        elif com_type=='hardstop':

            yield from self.send_gcode('M112') # halt the motor driver
            yield from self.send_gcode('M999') # then reset it











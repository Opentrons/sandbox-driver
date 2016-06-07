import asyncio

from apollo.smoothie import SmoothieCom

class CommandProcessor(object): 

    '''
    class for handling received front-end commands
    converting them to GCode
    and sending GCode to Smoothie-Com
    '''

    def __init__(self):
        self.smoothie_com = SmoothieCom('localhost', 8000)

        self.compiler = GCodeCompiler()

    @asyncio.coroutine
    def connect(self):
        '''
        tell the smoothie module to connect to the motor controller
        '''
        yield from self.smoothie_com.connect()

    @asyncio.coroutine
    def send_gcode(self,string):
        '''
        send a GCode string to the smoothie module
        '''
        yield from self.smoothie_com.send(string)

    @asyncio.coroutine
    def process(self, command):
        '''
        receive front-end commands, and convert them to GCode
        '''
        com_type = command.get('type', None)
        com_data = command.get('data', {})

        gcode_creator = getattr(self.compiler, com_type, None)

        if gcode_creator:
            for c in gcode_creator(com_data):
                yield from self.send_gcode(c)



class GCodeCompiler(object):

    '''
    class for converting a front-end command to it's GCode equivalent
    '''

    def __init__(self):

        self.axis = ['X', 'Y', 'Z', 'A', 'B']

    def parse_coords(self,data):

        '''
        method used by 'move' and 'move_to' to create GCode coordinates for each supplied axis
        '''

        temp_string = ''

        for ax in self.axis:
            
            val = data.get(ax.lower())
            
            if val!=None:
                temp_string += ' '                    # ascii space
                temp_string += ax                     # axis
                temp_string += str(val)               # value

        return temp_string

    def move(self,data):

        '''
        create relative movement gcode
        '''

        coords_string = self.parse_coords(data)

        if len(coords_string):
            return ['G91','G0'+coords_string]

        else:
            return []


    def move_to(self,data):

        '''
        create absolute movement gcode
        '''

        coords_string = self.parse_coords(data)

        if len(coords_string):
            return ['G90','G0'+coords_string]

        else:
            return []

    def home(self,data):

        '''
        create 'home' gcode: if no axis are specified, all axis are homed at once
        '''

        command = 'G28'
            
        if data: # a None might be passed
            for n in data:
                command += ' '
                command += n.upper()

        return [command]

    def speed(self,data):

        '''
        create 'speed' gcode: XYZ axis speeds are tied together, others are independent
        '''

        commands = []

        if data.get('xyz') != None:
            commands.append('F{0}'.format(data['xyz']))
        if data.get('a') != None:
            commands.append('a{0}'.format(data['a']))
        if data.get('b') != None:
            commands.append('b{0}'.format(data['b']))

        return commands

    def acceleration(self,data):
        '''
        create 'acceleration' gcode: XY axis accelerations are tied together, others are independent
        '''

        command = 'M204'

        if data.get('xy') != None:
            command += ' S{}'.format(data.get('xy'))
        if data.get('z') != None:
            command += ' Z{}'.format(data.get('z'))
        if data.get('a') != None:
             command += ' A{}'.format(data.get('a'))
        if data.get('b') != None:
             command += ' B{}'.format(data.get('b'))

        if command!='M204':
            return [command]
        else:
            return []

    def hardstop(self,data):
        '''
        create 'hardstop' gcode: halt the motor driver, then reset it
        '''
        return ['M112','M999']








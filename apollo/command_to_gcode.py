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

        self.speed_axis = {
            'xyz'   : 'F',
            'a'     : 'a',
            'b'     : 'b'
        }

        self.accel_axis = {
            'xy'    : 'S',
            'z'     : 'Z',
            'a'     : 'A',
            'b'     : 'B'
        }

        self.codes = {
            'seek'      : 'G0',
            'abs'       : 'G90',
            'rel'       : 'G91',
            'home'      : 'G28',
            'accel'     : 'M204',
            'hardstop'  : 'M112',
            'reset'     : 'M999'
        }

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
            return [self.codes['rel'],self.codes['seek']+coords_string]

        else:
            return []


    def move_to(self,data):

        '''
        create absolute movement gcode
        '''

        coords_string = self.parse_coords(data)

        if len(coords_string):
            return [self.codes['abs'],self.codes['seek']+coords_string]

        else:
            return []

    def home(self,data):

        '''
        create 'home' gcode: if no axis are specified, all axis are homed at once
        '''

        command = self.codes['home']
            
        if data: # a None might be passed
            for n in data:
                command += ' '
                command += n.upper()

        return [command]

    def speed(self,data):

        '''
        create 'speed' gcode: XYZ axis speeds are tied together, others are independent
        '''

        command = self.codes['seek']

        if data.get('xyz') != None:
            command += ' '
            command += self.speed_axis['xyz']
            command += str(data['xyz'])
        if data.get('a') != None:
            command += ' '
            command += self.speed_axis['a']
            command += str(data['a'])
        if data.get('b') != None:
            command += ' '
            command += self.speed_axis['b']
            command += str(data['b'])

        if command!=self.codes['seek']:
            return [command]
        else:
            return []

    def acceleration(self,data):
        '''
        create 'acceleration' gcode: XY axis accelerations are tied together, others are independent
        '''

        command = self.codes['accel']

        if data.get('xy') != None:
            command += ' '
            command += self.accel_axis['xy']
            command += str(data['xy'])
        if data.get('z') != None:
            command += ' '
            command += self.accel_axis['z']
            command += str(data['z'])
        if data.get('a') != None:
            command += ' '
            command += self.accel_axis['a']
            command += str(data['a'])
        if data.get('b') != None:
            command += ' '
            command += self.accel_axis['b']
            command += str(data['b'])

        if command!=self.codes['accel']:
            return [command]
        else:
            return []

    def hardstop(self,data):
        '''
        create 'hardstop' gcode: halt the motor driver, then reset it
        '''
        return [self.codes['hardstop'],self.codes['reset']]








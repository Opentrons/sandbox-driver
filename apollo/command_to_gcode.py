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
        if len(string):
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

        self.axis = {
            'seek'  : ['x','y','z','a','b'],
            'speed' : ['xyz'      ,'a','b'],
            'accel' : ['xy'   ,'z','a','b']
        }

        self.commands = {
            'seek'      : 'G0',
            'speed'     : 'G0',
            'move_to'   : 'G90',
            'move'      : 'G91',
            'home'      : 'G28',
            'accel'     : 'M204',
            'hardstop'  : 'M112',
            'reset'     : 'M999'
        }

        self.codes = {
            'seek' : {
                'x'     : 'X',
                'y'     : 'Y',
                'z'     : 'Z',
                'a'     : 'A',
                'b'     : 'B'
            },
            # XYZ axis speeds are tied together, others are independent
            'speed' : {
                'xyz'   : 'F',
                'a'     : 'a',
                'b'     : 'b'
            },
            # XY axis accelerations are tied together, others are independent
            'accel' : {
                'xy'    : 'S',
                'z'     : 'Z',
                'a'     : 'A',
                'b'     : 'B'
            }
        }

    def parse_values(self,data,type):

        '''
        method to create GCode values for each supplied axis
        '''

        temp_string = ''

        for ax in self.axis[type]:
            
            val = data.get(ax,None)
            
            if val!=None:
                temp_string += ' '                    # ascii space
                temp_string += self.codes[type][ax]   # axis
                temp_string += str(val)               # value

        return temp_string

    def create_command(self,data,type):

        '''
        apply a given axis' commands/codes to the supplied front-end data
        '''

        tstring = self.commands[type]

        tstring += self.parse_values(data,type)

        if tstring!=self.commands[type]:
            return tstring
        else:
            return ''

    def move(self,data):

        '''
        create relative movement gcode
        '''

        return [ self.commands['move'] , self.create_command(data,'seek') ]


    def move_to(self,data):

        '''
        create absolute movement gcode
        '''

        return [ self.commands['move_to'] , self.create_command(data,'seek') ]

    def speed(self,data):

        '''
        create 'speed' gcode
        '''

        return [self.create_command(data,'speed')]


    def acceleration(self,data):
        '''
        create 'acceleration' gcode
        '''

        return [self.create_command(data,'accel')]

    def home(self,data):

        '''
        create 'home' gcode: if no axis are specified, all axis are homed at once
        '''

        tstring = self.commands['home']
            
        if data: # a None might be passed
            for n in data:
                tstring += ' '
                tstring += str(n).upper() # UPPER CASE

        return [tstring]

    def hardstop(self,data):
        '''
        create 'hardstop' gcode: halt the motor driver, then reset it
        '''
        return [self.commands['hardstop'],self.commands['reset']]








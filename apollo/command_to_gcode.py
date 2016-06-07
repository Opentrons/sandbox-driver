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
        com_type = command.get('type', '')
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

        # axis are given a predefined order, making testing easier
        self.command_axis = {
            'seek'  : ['x','y','z','a','b'],
            'speed' : ['xyz'      ,'a','b'],
            'acceleration' : ['xy'   ,'z','a','b']
        }

        # dict of gcode commands
        # only one command (plus its arguments/values) is sent to smoothie-com at a time
        self.gcode_commands = {
            'seek'          : 'G0',
            'speed'         : 'G0',
            'move_abs'      : 'G90',
            'move_rel'      : 'G91',
            'home'          : 'G28',
            'acceleration'  : 'M204',
            'hardstop'      : 'M112',
            'reset'         : 'M999'
        }

        # labels for any value passed with a command
        self.gcode_keys = {
            'seek' : {
                'x'     : 'X',
                'y'     : 'Y',
                'z'     : 'Z',
                'a'     : 'A',
                'b'     : 'B'
            },
            # XYZ speeds are tied together, others are independent
            'speed' : {
                'xyz'   : 'F',
                'a'     : 'a',
                'b'     : 'b'
            },
            # XY accelerations are tied together, others are independent
            'acceleration' : {
                'xy'    : 'S',
                'z'     : 'Z',
                'a'     : 'A',
                'b'     : 'B'
            }
        }

    def parse_values(self,data,type):

        '''
        method to create GCode values for each supplied axis
        returns a string
        '''

        temp_string = ''

        for axis in self.command_axis.get(type,[]):
                        
            if data.get(axis,None):
                temp_string += ' '                          # ascii space
                temp_string += self.gcode_keys[type][axis]  # axis
                temp_string += str(data[axis])              # value

        return temp_string

    def create_command_string(self,data,type):

        '''
        apply a given axis' commands/codes to the supplied front-end data
        returns a string
        '''

        temp_string = self.parse_values(data,type)

        # only return the string if it has grown beyond the initial command
        if temp_string:
            return self.gcode_commands[type] + temp_string
        else:
            return ''

    def move(self,data):

        '''
        create absolute or relative movement gcode
        returns array of strings
        '''

        mode_command = self.gcode_commands['move_rel'] if data.get('relative',False) else self.gcode_commands['move_abs']

        return [ mode_command , self.create_command_string(data,'seek') ]


    def speed(self,data):

        '''
        create 'speed' gcode
        returns array of strings
        '''

        return [ self.create_command_string(data,'speed') ]


    def acceleration(self,data):
        '''
        create 'acceleration' gcode
        returns array of strings
        '''

        return [ self.create_command_string(data,'acceleration') ]

    def home(self,data):

        '''
        create 'home' gcode: if no axis are specified, all axis are homed at once
        returns array of strings
        '''

        temp_string = self.gcode_commands['home']
            
        if data: # a None might be passed
            for n in data:
                temp_string += ' '
                temp_string += str(n[0]).upper() # UPPER CASE

        return [ temp_string ]

    def hardstop(self,data):
        '''
        create 'hardstop' gcode: halt the motor driver, then reset it
        returns array of strings
        '''
        return [ self.gcode_commands['hardstop'] , self.gcode_commands['reset'] ]








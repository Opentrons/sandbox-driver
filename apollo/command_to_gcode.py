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
        com_type = 'command_{}'.format(command.get('type', ''))
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
        self.axis = {
            'seek'  : ['x','y','z','a','b'],
            'speed' : ['xyz'      ,'a','b'],
            'accel' : ['xy'   ,'z','a','b']
        }

        # dict of gcode commands
        # only one command at a time (with its arguments) is sent to smoothie-com
        self.commands = {
            'seek'      : 'G0',
            'speed'     : 'G0',
            'move_abs'  : 'G90',
            'move_rel'  : 'G91',
            'home'      : 'G28',
            'accel'     : 'M204',
            'hardstop'  : 'M112',
            'reset'     : 'M999'
        }

        # labels for any value passed with a command
        self.codes = {
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
        returns a string
        '''

        temp_string = ''

        for ax in self.axis[type]:
            
            val = data.get(ax,None)
            
            if val!=None:
                temp_string += ' '                    # ascii space
                temp_string += self.codes[type][ax]   # axis
                temp_string += str(val)               # value

        return temp_string

    def create_command_string(self,data,type):

        '''
        apply a given axis' commands/codes to the supplied front-end data
        returns a string
        '''

        tstring = self.commands[type]

        tstring += self.parse_values(data,type)

        # only return the string if it has grown beyond the initial command
        if tstring!=self.commands[type]:
            return tstring
        else:
            return ''

    def command_move(self,data):

        '''
        create absolute or relative movement gcode
        returns array of strings
        '''

        com = self.commands['move_rel'] if data.get('relative',False) else self.commands['move_abs']

        return [ com , self.create_command_string(data,'seek') ]


    def command_speed(self,data):

        '''
        create 'speed' gcode
        returns array of strings
        '''

        return [self.create_command_string(data,'speed')]


    def command_acceleration(self,data):
        '''
        create 'acceleration' gcode
        returns array of strings
        '''

        return [self.create_command_string(data,'accel')]

    def command_home(self,data):

        '''
        create 'home' gcode: if no axis are specified, all axis are homed at once
        returns array of strings
        '''

        tstring = self.commands['home']
            
        if data: # a None might be passed
            for n in data:
                tstring += ' '
                tstring += str(n).upper() # UPPER CASE

        return [tstring]

    def command_hardstop(self,data):
        '''
        create 'hardstop' gcode: halt the motor driver, then reset it
        returns array of strings
        '''
        return [self.commands['hardstop'],self.commands['reset']]








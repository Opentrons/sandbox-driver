import asyncio

from apollo.smoothie import SmoothieCom

from config.settings import Config

class CommandToGCode(object): 

    '''
    class for handling received front-end commands
    converting them to GCode
    and sending GCode to Smoothie-Com
    '''

    def __init__(self):

        self.smoothie_com = SmoothieCom(Config.SMOOTHIE_URL, Config.SMOOTHIE_PORT)

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
        
        method = getattr(self, command.get('type', '') , None)

        if method:
            for line in method( command.get('data',{}) ):
                yield from self.send_gcode(line)

    def create_command_string(self,data,type):

        '''
        turn a front-end command dict into the equivalent gcode string
        returns a string
        '''

        temp_string = ''

        for axis in Config.GCODE_AXIS.get(type,[]):
            if data.get(axis,None):
                temp_key = Config.GCODE_KEYS[type][axis]
                temp_string += ' {0}{1}'.format( temp_key , data[axis] )

        # only return the string if it has grown beyond the initial command
        if len(temp_string):
            return Config.GCODE_COMMANDS[type] + temp_string # prepend with the appropriate gcode command
        else:
            return ''

    def move(self,data):

        '''
        create absolute or relative movement gcode
        returns array of strings
        '''

        mode = Config.GCODE_COMMANDS['move_rel'] if data.get('relative',False) else Config.GCODE_COMMANDS['move_abs']

        return [ mode , self.create_command_string(data,'seek') ]


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

        temp_string = Config.GCODE_COMMANDS['home']
            
        for n in (data if data else []): # a None might be passed
            temp_string += ' {}'.format(str(n[0]).upper()) # UPPER CASE

        return [ temp_string ]

    def hardstop(self,data):
        '''
        create 'hardstop' gcode: halt the motor driver, then reset it
        returns array of strings
        '''
        return [ Config.GCODE_COMMANDS['hardstop'] , Config.GCODE_COMMANDS['reset'] ]



import asyncio

from apollo.smoothie import SmoothieCom
from config.settings import Config


class CommandToGCode(object): 
    """
    this module converts front-end commands to GCode
    then sends GCode strings to Smoothie-Com module
    """

    def __init__(self):
        self.smoothie_com = SmoothieCom(Config.SMOOTHIE_URL, Config.SMOOTHIE_PORT)

        self.COMMAND_TYPE_TO_HANDLER = {
            'move': self.move,
            'position': self.position,
            'hardstop': self.hardstop,
            'home': self.home,
            'acceleration': self.acceleration,
            'speed': self.speed
        }

    @asyncio.coroutine
    def connect(self):
        """
        tell the smoothie module to connect to the motor controller
        return True if successful
        """
        return (yield from self.smoothie_com.connect())

    @asyncio.coroutine
    def send_gcode(self, gcode : str):
        """
        send a GCode string to the smoothie module
        """
        if gcode:
            return (yield from self.smoothie_com.send(gcode))

    @asyncio.coroutine
    def process(self, command):
        """
        receive front-end commands, and convert them to GCode
        returns None or a coordinate dict
        """

        # check to see if this module has a method matching the command's 'type'
        command_type = command.get('type', '')

        command_data = command.get('data',{})

        gcode_list = None

        try:
            handler = self.COMMAND_TYPE_TO_HANDLER[command_type]
            gcode_list = handler(command_data)
        except KeyError:
            log.error('invalid command: {}'.format(command_type))

        if gcode_list:

            coords = None

            # pass the data to the matching method, returning an array of gcode strings
            for gcode_string in gcode_list:

                ret = yield from self.send_gcode(gcode_string)

                if ret != None:
                    coords = self.parse_coordinates(ret)

            return coords

    def parse_coordinates(self,coords):
        """
        removes unnecessary data from the coordinates object returned from smoothie-com
        returns a dict
        """

        if type(coords) is dict:

            new_coords = {}

            for axis, label in Config.GCODE_KEYS['position'].items():
                if coords.get(label,None) != None:
                    new_coords[axis] = coords[label]

            return new_coords

    def create_gcode_string(self,data,type):
        """
        turns a front-end command dict into the equivalent gcode string
        returns a string
        """

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
        """
        create absolute or relative movement gcode
        returns array of strings
        """

        mode = Config.GCODE_COMMANDS['move_rel'] if data.get('relative',False) else Config.GCODE_COMMANDS['move_abs']

        return [ mode , self.create_gcode_string(data,'move') ]

    def position(self,data):
        """
        GET or SET the current axis positions
        returns array of strings
        """

        if data and type(data) is dict and len(data.keys()):
            return [ self.create_gcode_string(data,'position') ]
        else:
            return [ Config.GCODE_COMMANDS['position_get'] ]

    def speed(self,data):
        """
        create 'speed' gcode
        returns array of strings
        """

        return [ self.create_gcode_string(data,'speed') ]

    def acceleration(self,data):
        """
        create 'acceleration' gcode
        returns array of strings
        """

        return [ self.create_gcode_string(data,'acceleration') ]

    def home(self,data):
        """
        create 'home' gcode: if no axis are specified, all axis are homed at once
        returns array of strings
        """

        temp_string = Config.GCODE_COMMANDS['home']
        for n in (data if data else []): # a None might be passed
            temp_string += ' {}'.format(str(n[0]).upper()) # UPPER CASE

        return [ temp_string ]

    def hardstop(self,data):
        """
        create 'hardstop' gcode: halt the motor driver, then reset it
        returns array of strings
        """
        return [ Config.GCODE_COMMANDS['hardstop'] , Config.GCODE_COMMANDS['reset'] ]

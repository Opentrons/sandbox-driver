class Config(object):
    COMMAND_QUEUE_SIZE = 500

    BROWSER_TO_ROBOT_TOPIC = 'com.opentrons.browser_to_robot'
    ROBOT_TO_BROWSER_TOPIC = 'com.opentrons.robot_to_browser'

    ROUTER_REALM = 'ot_realm'

    ROUTER_URL = "ws://{host}:{port}/{path}".format(
        host='localhost',
        port='8000',
        path='ws'
    )

    SMOOTHIE_URL = 'localhost'
    SMOOTHIE_PORT = 8000

    # axis are given a predefined order, making testing easier
    GCODE_AXIS = {
        'move'  :           ['x','y','z','a','b'],
        'position' :        ['x','y','z','a','b'],
        'speed' :           ['xyz','a','b'],
        'acceleration' :    ['xy','z','a','b']
    }

    GCODE_MOVE                      = 'G0'
    GCODE_HOME                      = 'G28'
    GCODE_ABSOLUTE_POSITIONING      = 'G90'
    GCODE_RELATIVE_POSITIONING      = 'G91'
    GCODE_SET_POSITION              = 'G92'
    GCODE_EMERGENCY_STOP            = 'M112'
    GCODE_GET_POSITION              = 'M114'
    GCODE_GET_ENDSTOPS              = 'M119'
    GCODE_GET_SPEEDS                = 'M199'
    GCODE_ACCELERATION              = 'M204'
    GCODE_RESTART                   = 'M999'

    # dict of gcode commands
    # only one command (plus its arguments/values) is sent to smoothie-com at a time
    GCODE_COMMANDS = {
        'move'          : GCODE_MOVE,
        'position'      : GCODE_SET_POSITION,
        'position_get'  : GCODE_GET_POSITION,
        'speed'         : GCODE_MOVE,
        'speed_get'     : GCODE_GET_SPEEDS,
        'move_abs'      : GCODE_ABSOLUTE_POSITIONING,
        'move_rel'      : GCODE_RELATIVE_POSITIONING,
        'home'          : GCODE_HOME,
        'acceleration'  : GCODE_ACCELERATION,
        'hardstop'      : GCODE_EMERGENCY_STOP,
        'reset'         : GCODE_RESTART,
        'switches'      : GCODE_GET_ENDSTOPS
    }

    # labels for any value passed with a command
    GCODE_KEYS = {
        'move' : {
            'x'     : 'X',
            'y'     : 'Y',
            'z'     : 'Z',
            'a'     : 'A',
            'b'     : 'B'
        },
        'position' : {
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

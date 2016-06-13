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

    # dict of gcode commands
    # only one command (plus its arguments/values) is sent to smoothie-com at a time
    GCODE_COMMANDS = {
        'move'          : 'G0',
        'position'      : 'G92',
        'position_get'  : 'M114',
        'speed'         : 'G0',
        'move_abs'      : 'G90',
        'move_rel'      : 'G91',
        'home'          : 'G28',
        'acceleration'  : 'M204',
        'hardstop'      : 'M112',
        'reset'         : 'M999'
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

class Config(object):
    COMMAND_QUEUE_SIZE = 500

    BROWSER_TO_ROBOT_TOPIC = 'browser_to_robot'
    ROBOT_TO_BROWSER_TOPIC = 'robot_to_browser'

    ROUTER_REALM = 'ot_realm'

    ROUTER_URL = "ws://{host}:{port}/{path}".format(
        host='localhost',
        port='8000',
        path='ws'
    )

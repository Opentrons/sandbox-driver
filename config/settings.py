class Config(object):
    BROWSER_TO_ROBOT_TOPIC = 'browser_to_robot'
    ROBOT_TO_BROWSER_TOPIC = 'robot_to_browser'

    ROUTER_URL = "ws://{host}:{port}/{path}".format(
        host='localhost',
        port='8000',
        path='ws'
    )

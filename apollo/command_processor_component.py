import asyncio

from autobahn.asyncio import wamp


def get_command_processor_component(command_queue):
    class RobotCommandProcessorComponent(wamp.ApplicationSession):
            """WAMP application session for Controller"""

            def __init__(self, command_queue, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.command_queue = command_queue

            @asyncio.coroutine
            def onJoin(self, details):

                print('Result processor joined...')

                # loop = asyncio.get_event_loop()
                # c = MotorController()
                # yield from c.connect()


                while True:
                    import pdb; pdb.set_trace()
                    # msg = utils.coro_get(qq)
                    #
                    # res = yield from motorController.process(msg)

                    print('')

                    self.publish('com.opentrons.robot_to_browser', res)

            # @asyncio.coroutine
            # def onMessage(self, msg):
            #     # TODO enqueue message
            #     # TODO return message id
            #     pass
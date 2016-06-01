import asyncio

from autobahn.asyncio import wamp


def get_command_processor_component(command_queue):
    class RobotCommandProcessorComponent(wamp.ApplicationSession):
            """WAMP application session for Controller"""

            @asyncio.coroutine
            def onJoin(self, details):

                print('Robot command processor joined...')

                # loop = asyncio.get_event_loop()
                # c = MotorController()
                # yield from c.connect()


                while True:
                    import pdb; pdb.set_trace()
                    # msg = utils.coro_get(qq)
                    #
                    # res = yield from motorController.process(msg)

                    self.publish('com.opentrons.robot_to_browser', 'foo')

            # @asyncio.coroutine
            # def onMessage(self, msg):
            #     # TODO enqueue message
            #     # TODO return message id
            #     pass
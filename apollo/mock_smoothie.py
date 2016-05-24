import asyncio
import logging

# https://github.com/python/asyncio/blob/b6b6d28d161c2c6478932b5cbd4e32a6be576c79/examples/simple_tcp_server.py

class MockSmoothie():

    def __init__(self, host, port, loop=None):
        self.server = None
        self.host = host
        self.port = port
        if not loop:
            self.loop = asyncio.get_event_loop()
        self.clients = {}

    def _accept_client(self, client_reader, client_writer):

        task = asyncio.Task(self._handle_client(client_reader, client_writer))
        self.clients[task] = (client_reader, client_writer)

        client_writer.write("Smoothie\r\n".encode())
        yield from client_writer.drain()
        client_writer.write("ok\r\n".encode())
        yield from client_writer.drain()

        def client_done(task):
            del self.clients[task]

        task.add_done_callback(client_done)

    @asyncio.coroutine
    def _handle_client(self, client_reader, client_writer):

        while True:
            data = (yield from client_reader.readline()).decode()
            if not data:
                break
            #cmd, *
            #args = data.rstrip().split(' ')

            #print('cmd: ',cmd)
            #print('args: ',args)
            print('data: ',data)
            
            # JUST FOR GCODE
            # data -> possible_command
            # LOOP
            #   first char == G or M?
            #       find next G or M
            #           => single_command
            #           => possible_command
            #           single_command -> gcode()
            #       * stores if last was G1 or G0 for if just XYZFabc by itself,
            #       should include ABC
            #       ON_GCODE_RECEIVED ( gcode )
            #        - do things based on gcode params
            # 
            # gcode() - prepare_cached_values
            # - has_letter() - G M
            # - get_int() - G M
            # 
            # NON-GCODE
            # SimpleShell
            # string cmd = shift_parameter
            # parse_command( ) --> p->func(args, stream)
            #


            yield from client_writer.drain()

    def start(self, loop):
        self.server = loop.run_until_complete(
            asyncio.streams.start_server(
                self._accept_client,
                self.host,
                self.port,
                loop=self.loop
            )
        )

    def stop(self, loop):
        if self.server is not None:
            self.server.close()
            loop.run_until_complete(self.server.wait_closed())
            self.server = None

        
    


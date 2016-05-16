#!/usr/bin/env python3

import asyncio, time


class STNSimServerClientProtocol(asyncio.Protocol):

	ack_received = 'ok\r\n'.encode()
	ack_ready = '{"stat":0}\r\n'.encode()
	mock_response_1 = '{"x":21.123,"y":0.456,"stat":1}\r\n'
	mock_response_2 = '{"a":7.89,"b":0.321}\r\n'

	def connection_made(self, transport):
		print('asdf')
		peername = transport.get_extra_info('peername')
		self.transport = transport
		self.transport.write(ack_received)

	def data_received(self, data):
		message = data.decode(data)
		self.transport.write(ack_received)
		time.sleep(1)
		self.transport.write(mock_response_1)
		time.sleep(1)
		self.transport.write(mock_response_2)
		self.transport.write(ack_ready)
		# log







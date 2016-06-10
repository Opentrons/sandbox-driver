import asyncio
import unittest
from apollo import utils

from apollo.smoothie import SmoothieCom


class SmoothieComTest(unittest.TestCase):
    def setUp(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

        self.address = utils.get_free_os_address()
        self.smc = SmoothieCom(
            self.address[0],
            self.address[1],
        )
    def tearDown(self):
        self.loop.stop()
        self.loop.close()

    def test_send_M114(self):
        """ TEST SENDING M114 """
        print('\n\n','='*20,'TESTING M114','-'*20,'\n')
        smoothie_read_sequence = [
            'feedback engaged',
            'ok',
            'ok {"foo":123}',
            'feedback disengaged',
            'ok',
        ]

        smoothie_write_sequence = [b'M62\r\n', b'M114\r\n', b'M63\r\n']

        self.smc.writer = utils.Writer()
        self.smc._read = utils.Reader(smoothie_read_sequence)._read

        self.loop.run_until_complete(self.smc.send('M114', None))

        # THIS TESTS DATA SENT MATCHES WHAT IT IS SUPPOSED TO
        self.assertEqual(self.smc.writer.drain_buffer, smoothie_write_sequence)
        
        # TEST USING READ SEQUENCE? ... smoothie_read_sequence just keeps program running?

    def test_send_G0(self):
        """ TEST SENDING G0 """
        print('\n\n','='*20,'TESTING G0','-'*20,'\n')
        smoothie_read_sequence = [
            'feedback engaged',
            'ok',
            'ok {"stat":0}',
            '{"stat":0}',
            'feedback disengaged',
            'ok',
        ]

        smoothie_write_sequence = [b'M62\r\n', b'G0 X1.2 Y34.5 Z6 A7.08 B9.02\r\n', b'M63\r\n']

        self.smc.writer = utils.Writer()
        self.smc._read = utils.Reader(smoothie_read_sequence)._read

        self.loop.run_until_complete(self.smc.send('G0 X1.2 Y34.5 Z6 A7.08 B9.02', None))
        
        self.assertEqual(self.smc.writer.drain_buffer, smoothie_write_sequence)
        
    def test_send_G28(self):
        """ TEST SENDING G28 """
        print('\n\n','='*20,'TESTING G28','-'*20,'\n')
        smoothie_read_sequence = [
            'feedback engaged',
            'ok',
            'ok {"stat":0}',
            '{"stat":0}',
            'feedback disengaged',
            'ok',
        ]

        smoothie_write_sequence = [b'M62\r\n', b'G28\r\n', b'M63\r\n']

        self.smc.writer = utils.Writer()
        self.smc._read = utils.Reader(smoothie_read_sequence)._read

        self.loop.run_until_complete(self.smc.send('G28', None))

        self.assertEqual(self.smc.writer.drain_buffer, smoothie_write_sequence)

    def test_send_G90(self):
        """ TEST SENDING G90 """
        print('\n\n','='*20,'TESTING G90','-'*20,'\n')
        smoothie_read_sequence = [
            'feedback engaged',
            'ok',
            'ok {"foo":123}',
            'ok',
            'feedback disengaged',
            'ok',
        ]

        smoothie_write_sequence = [b'M62\r\n', b'G90\r\n', b'M63\r\n']

        self.smc.writer = utils.Writer()
        self.smc._read = utils.Reader(smoothie_read_sequence)._read

        self.loop.run_until_complete(self.smc.send('G90', None))

        self.assertEqual(self.smc.writer.drain_buffer, smoothie_write_sequence)

    def test_send_G91(self):
        """ TEST SENDING G91 """
        print('\n\n','='*20,'TESTING G91','-'*20,'\n')
        smoothie_read_sequence = [
            'feedback engaged',
            'ok',
            'ok {"foo":123}',
            'ok',
            'feedback disengaged',
            'ok',
        ]

        smoothie_write_sequence = [b'M62\r\n', b'G91\r\n', b'M63\r\n']

        self.smc.writer = utils.Writer()
        self.smc._read = utils.Reader(smoothie_read_sequence)._read

        self.loop.run_until_complete(self.smc.send('G91', None))

        self.assertEqual(self.smc.writer.drain_buffer, smoothie_write_sequence)

    def test_send_G92(self):
        """ TEST SENDING G92 """
        print('\n\n','='*20,'TESTING G92','-'*20,'\n')
        smoothie_read_sequence = [
            'feedback engaged',
            'ok',
            'ok {"foo":123}',
            'ok',
            'feedback disengaged',
            'ok',
        ]

        smoothie_write_sequence = [b'M62\r\n', b'G92 X1 Y2 Z3 A4 B5\r\n', b'M63\r\n']

        self.smc.writer = utils.Writer()
        self.smc._read = utils.Reader(smoothie_read_sequence)._read

        self.loop.run_until_complete(self.smc.send('G92 X1 Y2 Z3 A4 B5', None))

        self.assertEqual(self.smc.writer.drain_buffer, smoothie_write_sequence)

    def test_send_M112(self):
        """ TEST SENDING M112 """
        print('\n\n','='*20,'TESTING M112','-'*20,'\n')
        smoothie_read_sequence = [
            'feedback engaged',
            'ok',
            'ok {"foo":123}',
            'ok',
            'feedback disengaged',
            'ok',
        ]

        smoothie_write_sequence = [b'M112\r\n']

        self.smc.writer = utils.Writer()
        self.smc._read = utils.Reader(smoothie_read_sequence)._read

        self.loop.run_until_complete(self.smc.send('M112', None))

        self.assertEqual(self.smc.writer.drain_buffer, smoothie_write_sequence)


    def test_send_M119(self):
        """ TEST SENDING M119 """
        print('\n\n','='*20,'TESTING M119','-'*20,'\n')
        smoothie_read_sequence = [
            'feedback engaged',
            'ok',
            '{"M119":{"foo":123}}',
            'ok',
            'feedback disengaged',
            'ok',
        ]

        smoothie_write_sequence = [b'M62\r\n', b'M119\r\n', b'M63\r\n']

        self.smc.writer = utils.Writer()
        self.smc._read = utils.Reader(smoothie_read_sequence)._read

        self.loop.run_until_complete(self.smc.send('M119', None))

        self.assertEqual(self.smc.writer.drain_buffer, smoothie_write_sequence)

    def test_send_M199(self):
        """ TEST SENDING M199 """
        print('\n\n','='*20,'TESTING M199','-'*20,'\n')
        smoothie_read_sequence = [
            'feedback engaged',
            'ok',
            '{"M199":{"foo":123}}',
            'ok',
            'feedback disengaged',
            'ok',
        ]

        smoothie_write_sequence = [b'M62\r\n', b'M199\r\n', b'M63\r\n']

        self.smc.writer = utils.Writer()
        self.smc._read = utils.Reader(smoothie_read_sequence)._read

        self.loop.run_until_complete(self.smc.send('M199', None))

        self.assertEqual(self.smc.writer.drain_buffer, smoothie_write_sequence)

    def test_send_M204(self):
        """ TEST SENDING M204 """
        print('\n\n','='*20,'TESTING M204','-'*20,'\n')
        smoothie_read_sequence = [
            'feedback engaged',
            'ok',
            '{"M204":{"foo":123}}',
            'ok',
            'feedback disengaged',
            'ok',
        ]

        smoothie_write_sequence = [b'M62\r\n', b'M204\r\n', b'M63\r\n']

        self.smc.writer = utils.Writer()
        self.smc._read = utils.Reader(smoothie_read_sequence)._read

        self.loop.run_until_complete(self.smc.send('M204', None))

        self.assertEqual(self.smc.writer.drain_buffer, smoothie_write_sequence)

    def test_send_M999(self):
        """ TEST SENDING M999 """
        print('\n\n','='*20,'TESTING M999','-'*20,'\n')
        smoothie_read_sequence = [
            'feedback engaged',
            'ok',
            'ok {"foo":123}',
            'ok',
            'feedback disengaged',
            'ok',
        ]

        smoothie_write_sequence = [b'M999\r\n', b'M63\r\n']

        self.smc.writer = utils.Writer()
        self.smc._read = utils.Reader(smoothie_read_sequence)._read

        self.loop.run_until_complete(self.smc.send('M999', None))

        self.assertEqual(self.smc.writer.drain_buffer, smoothie_write_sequence)

if __name__ == '__main__':
    unittest.main()


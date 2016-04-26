import unittest

import driver.smoothie_driver



class SmoothieDriverTest(unittest.TestCase):

	def setUp(self):
		self.smooethie_driver = SmoothieDriver(simulate=(os.environ.get('SMOOTHIE_SIMULATE', 'true')=='true'))


	def test_add_and_remove_callbacks(self):


	def test_callbacks(self):


	def test_set_meta_callback(self):


	def test_meta_callbacks(self):


	def test_flow(self):


	def test_clear_queue(self):


	def test_connect(self):


	def test_disconnect(self):


	def test_commands(self):


	def test_configs(self):


	def test_set_config(self):

	# flow control tests
	# first, to smoothie flow
	def test_adjust_positions(self):


	def test_to_smoothie_flow(self):


	# second, from smoothie flow
	def test_format_group(self):


	def test_format_text_data(self):


	def test_format_json_data(self):


	def test_process_message_dict(self):



















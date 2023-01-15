#!/usr/bin/env python

'''A set of unittests for the Settings containers'''

import unittest

from helixstudios.utils import dict_diver_set
from helixstudios.utils import parent_url, localise_url


class UtilsTestCase(unittest.TestCase):
	'''A test case for the contents of the utils file.'''
	
	def test_dict_diver_set(self):
		'''Make sure setting a value in a nested dictionary works as expected'''

		my_dict = {'1': {'2': 'value'}}
		dict_diver_set(my_dict, '1', '2', value='new_value')
		self.assertEqual(my_dict['1']['2'], 'new_value')

	def test_parent_url(self):
		'''Make sure setting a value in a nested dictionary works as expected'''

		self.assertEqual(
			parent_url('https://www.google.com/path/to/url.php?param1=yes&param2=no#some_fragment'),
					   'https://www.google.com/path/to'
		)

	def test_relative_url(self):
		'''Make sure setting a value in a nested dictionary works as expected'''

		url = localise_url(
				'/my_video.mp4?id=1234567',
				'https://www.google.com/path/to/url.php?param1=yes&param2=no#some_fragment'
		)
		self.assertEqual(url, 'https://www.google.com/my_video.mp4?id=1234567')

		url = localise_url(
				'my_video.mp4?id=1234567',
				'https://www.google.com/path/to/url.php?param1=yes&param2=no#some_fragment'
		)
		self.assertEqual(url, 'https://www.google.com/path/to/my_video.mp4?id=1234567')


if __name__ == '__main__':
	unittest.main()
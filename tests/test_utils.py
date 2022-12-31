#!/usr/bin/env python

'''A set of unittests for the Settings containers'''

import unittest

from helixstudios.utils import dict_diver_set


class UtilsTestCase(unittest.TestCase):
	'''A test case for the contents of the utils file.'''
	
	def test_dict_diver_set(self):
		'''Make sure setting a value in a nested dictionary works as expected'''

		my_dict = {'1': {'2': 'value'}}
		dict_diver_set(my_dict, '1', '2', value='new_value')
		self.assertEqual(my_dict['1']['2'], 'new_value')


if __name__ == '__main__':
	unittest.main()
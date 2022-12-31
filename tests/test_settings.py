#!/usr/bin/env python

'''A set of unittests for the Settings containers'''

import os
import sys
import unittest
import tempfile

from helixstudios import SettingsYAML
from helixstudios import SettingsContainer

from helixstudios.utils import dict_diver_set


SAMPLE_RAW_DICT = {
	'key1': 'value1',
	'key2': 123456,
	'key3': '~/path/to/somewhere.txt',
	'key4': {
		'linux': '/linux/path',
		'darwin': '/darwin/path'
	},
	'key5': {
		'key5.1': 'value5.1'
	}
}

SAMPLE_YAML = b'''
key1: 
  key2:
    key3: this is a test
'''

class SettingsContainerTestCase(unittest.TestCase):
	'''A test case to test the settings container'''

	def setUp(self):
		self.sc = SettingsContainer(SAMPLE_RAW_DICT)

	def test_lookup(self):
		'''Ensure setting lookups works successfully'''

		self.assertEqual(self.sc['key1'], 'value1')
		self.assertEqual(self.sc.get('key1'), 'value1')

		self.assertEqual(self.sc['key2'], 123456)
		self.assertEqual(self.sc.get('key2'), 123456)

	def test_path_expansion(self):
		'''Ensure the tilde is replaced with the $HOME environment variable'''

		# this lookup should not replace the tilde
		self.assertEqual(self.sc['key3'], '~/path/to/somewhere.txt')

		# this should
		path = self.sc.get_path('key3')
		self.assertNotEqual(path, '~/path/to/somewhere.txt')
		self.assertTrue(os.environ['HOME'] in path)

	def test_platform_substitution(self):
		'''Ensure the correct path is chosen for this platform'''

		# temporarily hack sys.platform for this unittest
		platform = sys.platform
		sys.platform = 'linux'

		path = self.sc.get_path('key4')
		self.assertEqual(path, '/linux/path')

		# now change sys.platform to a value that's not supported and make sure it raises
		sys.platform = 'freebsd'

		with self.assertRaises(KeyError) as e:
			self.sc.get_path('key4')

		# make sure the exception text is right
		self.assertEqual(e.exception.args[0], 'no entry for platform "freebsd" found for path: key4')

	def test_nested_lookup(self):
		'''Ensure nested lookups work as expected.'''

		self.assertEqual(self.sc['key5']['key5.1'], 'value5.1')
		self.assertEqual(self.sc.get('key5', 'key5.1'), 'value5.1')

	def test_nested_set(self):
		'''Ensure nested lookups work as expected.'''

		self.assertEqual(self.sc.get('key5', 'key5.1'), 'value5.1')
		self.sc.set('key5', 'key5.1', value='new_value')
		self.assertEqual(self.sc.get('key5', 'key5.1'), 'new_value')

	def test_value_not_found(self):
		'''Ensure non-existent value raise exceptions.'''

		with self.assertRaises(KeyError) as e:
			self.sc['key6']

		self.assertIsNone(self.sc.get('key6'))
		self.assertEqual(self.sc.get('key6', default='my_default_arg'), 'my_default_arg')


class SettingsYAMLTestCase(unittest.TestCase):
	'''A test case to test loading a YAML file'''

	def test_file_loading(self):
		'''Ensure YAML files can be loaded from disk.'''

		with tempfile.NamedTemporaryFile(delete=False) as fp:
			fp.write(SAMPLE_YAML)
	
		settings = SettingsYAML(fp.name)
		self.assertEqual(settings['key1']['key2']['key3'], 'this is a test')
		self.assertEqual(settings.get('key1', 'key2', 'key3'), 'this is a test')


if __name__ == '__main__':
	unittest.main()
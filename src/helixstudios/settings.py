#!/usr/bin/env python

'''A settings container and localiser, returning 
only the valid settings for the current platform.'''

import os
import sys
import yaml
import copy

from .utils import dict_diver
from .utils import dict_diver_set


def localise_path(settings_value, location):
	'''Take a string/dict from the settings file, and localise it, i.e. if it's 
	a dict, choose the correct platform entry, and also expand any user path prefixes.'''

	if isinstance(settings_value, (dict, SettingsContainer)):
		# this path is a dictionary, need to do a platform lookup
		if sys.platform not in settings_value:
			raise KeyError(f'no entry for platform "{sys.platform}" found for setting: {" -> ".join(location)}')

		path = settings_value[sys.platform]
	elif isinstance(settings_value, str):
		path = settings_value
	else:
		raise TypeError(f'unrecognised value for setting {" -> ".join(location)}')

	return os.path.expanduser(path)


class SettingsYAML:
	'''A container for the YAML settings file.'''

	def __init__(self, path):
		self._path = path
		
		with open(path) as f:
			settings = yaml.safe_load(f)
		
		self._raw_settings = SettingsContainer(settings)

	def __getitem__(self, item):
		return self._raw_settings[item]

	def get(self, *location, default=None):
		return self._raw_settings.get(*location, default=default)

	def get_path(self, *location, default=None):
		return self._raw_settings.get_path(*location, default=default)

	def get_path_list(self, *location, default=None):
		return self._raw_settings.get_path_list(*location, default=default)


class SettingsContainer:
	'''A generic container that can encapsulate the settings dictionary,
	which allows nested lookups into any level of the dictionary.'''

	def __init__(self, raw_dict):
		self._raw_dict = copy.deepcopy(raw_dict)

	def __contains__(self, item):
		return item in self._raw_dict

	def __getitem__(self, item):
		if item not in self._raw_dict:
			raise KeyError(f'{item} not found')

		value = self._raw_dict[item]
		if isinstance(value, dict):
			return SettingsContainer(value)
		else:
			return value

	def set(self, *location, value=None):
		'''Update a value in the stored dictionary'''
		dict_diver_set(self._raw_dict, *location, value=value)

	def get(self, *location, default=None):
		'''Get a nested setting from the settings file.'''
		value = dict_diver(self._raw_dict, *location, default=default)
		if isinstance(value, dict):
			return SettingsContainer(value)
		else:
			return value

	def get_path(self, *location, default=None):
		'''Get a nested path from the settings file, and localise the 
		path based on platform.'''

		value = self.get(*location, default=default)
		return localise_path(value, location)

	def get_path_list(self, *location, default=None):
		'''Get a list of paths.'''

		paths = self.get(*location, default=default)
		if isinstance(paths, str):
			# this is just one string path, wrap it in a list
			return [localise_path(paths, location)]

		elif isinstance(paths, list):
			return [localise_path(p, location) for p in paths]

		else:
			raise TypeError(f'unrecognised type for path list setting {" -> ".join(location)}')

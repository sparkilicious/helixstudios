#!/usr/bin/env python

'''Parse the video page for all video metadata and links.'''

import re

from urllib.parse import urlparse
from .utils import localise_url

from functools import cached_property


PLAYLIST_FILE_LINKS_REGEX = re.compile(r'^#EXT-X-STREAM-INF:(?P<details>[a-zA-Z0-9".,=-]*)\n(?P<url>.*)$', re.M)
STREAM_FILE_LINKS_REGEX = re.compile(r'^#EXTINF:9,\n(?P<url>.*)$', re.M)

DETAILS_STRING_REGEX = re.compile(r'(?P<key>[A-Z-]+)=(?P<value>([^",]+|"[^"]+"))')


def _cast_value(value):
	'''Convert the given value from the details dictionary to its native type'''

	if value.isnumeric() and '.' in value:
		return float(value)
	elif value.isnumeric():
		return int(value)
	elif value.startswith('"') and value.endswith('"'):
		return value.strip('"')
	elif value == 'NONE':
		return None
	else:
		return value


def details_to_dict(details_string):
	'''Convert the details string to a dictionary'''

	return dict([(match.group('key'), _cast_value(match.group('value')))
		for match in DETAILS_STRING_REGEX.finditer(details_string)])


class M3U8PlaylistFile:
	'''Parser the primary playlist file'''
	
	def __init__(self, playlist_text, playlist_url):
		self._playlist_text = playlist_text
		self._playlist_url = playlist_url

	def __repr__(self):
		uri = urlparse(self._playlist_url)
		return f'<M3U8PlaylistFile("{uri.path}")>'

	def iter_streams(self):
		'''Iterate over all streams available in the playlist file'''

		for stream in PLAYLIST_FILE_LINKS_REGEX.finditer(self._playlist_text):
			details = details_to_dict(stream.group('details'))
			details.update(
				{'url': localise_url(stream.group('url'), self._playlist_url)}
			)

			yield details
	
	def all_streams(self):
		return list(self.iter_streams())

	@property
	def highest_bandwidth_stream(self):
		return max(self.iter_streams(), key=lambda x: x.get('BANDWIDTH'))


class M3U8Stream:
	'''Parser the primary playlist file'''
	
	def __init__(self, stream_file_text, stream_file_url):
		self._stream_file_text = stream_file_text
		self._stream_file_url = stream_file_url

	def __repr__(self):
		uri = urlparse(self._stream_file_url)
		return f'<M3U8Stream("{uri.path}")>'

	def iter_chunks(self):
		'''Iterate over all chunks in the file'''

		for chunk in STREAM_FILE_LINKS_REGEX.finditer(self._stream_file_text):
			yield localise_url(chunk.group('url'), self._stream_file_url)

	def all_chunks(self):
		return list(self.iter_chunks())


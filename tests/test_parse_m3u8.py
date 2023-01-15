#!/usr/bin/env python3

'''Using the downloaded sample video_listing.html file, make sure 
the parser extracts all the needed information.'''

import re
import unittest

from helixstudios import M3U8Stream
from helixstudios import M3U8PlaylistFile

from download_samples import sample_path, VIDEO_LISTING_URL


class M3U8PlaylistFileTestCase(unittest.TestCase):
	'''A test case for checking the M3U8PlaylistFile class'''

	def setUp(self):
		with open(sample_path('vod_playlist.m3u8')) as f:
			text = f.read()

		self.playlist = M3U8PlaylistFile(text, 
			'https://www.helixstudios.com/m3u8/sample.m3u8')

	def test_highest_resolution_stream(self):
		'''Conversion of date text to date object'''

		stream = self.playlist.highest_bandwidth_stream
		self.assertTrue('url' in stream)
		self.assertTrue('BANDWIDTH' in stream)
		self.assertTrue('https://www.helixstudios.com/m3u8' in stream['url'])


class M3U8StreamTestCase(unittest.TestCase):
	'''A test case for checking the M3U8Stream class'''

	def setUp(self):
		with open(sample_path('vod_stream.m3u8')) as f:
			text = f.read()

		self.stream = M3U8Stream(text, 
			'https://www.helixstudios.com/m3u8/child-1234-0.m3u8?ttl=123456789&token=abcdefghijklmnopqrstuvwxyz')

	def test_links(self):
		'''Make sure the links can all be parsed from the M3U8 file'''

		links = self.stream.all_chunks()
		self.assertIsInstance(links, list)
		self.assertGreater(len(links), 50)

		self.assertTrue(all([l.startswith('https://media.helixstudios.com/scenes/') for l in links]))
		

if __name__ == '__main__':
	unittest.main()





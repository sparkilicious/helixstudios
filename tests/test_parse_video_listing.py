#!/usr/bin/env python3

'''Using the downloaded sample video_listing.html file, make sure 
the parser extracts all the needed information.'''

import unittest

from helixstudios import VideoListingPage

from download_samples import sample_path, VIDEO_LISTING_URL


class VideoListingPageTestCase(unittest.TestCase):
	'''A test case for checking the VideoListingPage class'''

	def setUp(self):
		with open(sample_path('video_listing.html')) as f:
			text = f.read()

		self.vlp = VideoListingPage(text, VIDEO_LISTING_URL)

	def test_link_parsing(self):
		'''Ensure the parser picks out all video links'''
		# make sure at least 40 videos were found
		self.assertGreater(len(self.vlp.all_videos()), 40)
		

	def test_next_page(self):
		'''Ensure the parser picks out the next page link'''
		self.assertIsNotNone(self.vlp.next_page)
		self.assertTrue(
			self.vlp.next_page.startswith(VIDEO_LISTING_URL))

	def test_webpage_title(self):
		'''Make sure the title is correctly parsed'''
		print(self.vlp.webpage_title)


if __name__ == '__main__':
	unittest.main()
#!/usr/bin/env python3

'''Using the downloaded sample video_listing.html file, make sure 
the parser extracts all the needed information.'''

import pprint
import unittest


from helixstudios import ModelPage

from download_samples import sample_path, VIDEO_LISTING_URL


class ModelPageTestCase(unittest.TestCase):
	'''A test case for checking the VideoListingPage class'''

	def setUp(self):
		with open(sample_path('model.html')) as f:
			text = f.read()

		self.mp = ModelPage(text, VIDEO_LISTING_URL)

	def test_name(self):
		'''Ensure the model name is correctly extracted'''
		print(self.mp.model_name)

	def test_description(self):
		'''Ensure the model name is correctly extracted'''
		print(self.mp.description)

	def test_stats(self):
		'''Ensure the model name is correctly extracted'''
		pprint.pprint(self.mp.stats)


if __name__ == '__main__':
	unittest.main()
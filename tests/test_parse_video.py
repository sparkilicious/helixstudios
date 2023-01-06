#!/usr/bin/env python3

'''Using the downloaded sample video_listing.html file, make sure 
the parser extracts all the needed information.'''

import json
import datetime
import unittest

from helixstudios import VideoPage
from helixstudios import date_text_to_date_object

from download_samples import sample_path, VIDEO_LISTING_URL


class VideoPageTestCase(unittest.TestCase):
	'''A test case for checking the VideoListingPage class'''

	def setUp(self):
		with open(sample_path('video.html')) as f:
			text = f.read()

		self.vp = VideoPage(text, VIDEO_LISTING_URL)

	def test_date_text_to_date_object(self):
		'''Conversion of date text to date object'''

		self.assertIsInstance(date_text_to_date_object('Today'), datetime.date)
		self.assertIsInstance(date_text_to_date_object('Yesterday'), datetime.date)
		
		one_day_ago = date_text_to_date_object('1 day ago')
		fifteen_days_ago = date_text_to_date_object('15 days ago')

		self.assertIsInstance(one_day_ago, datetime.date)
		self.assertIsInstance(fifteen_days_ago, datetime.date)

		# make sure the dates returned are 14 days apart
		self.assertEqual((one_day_ago - fifteen_days_ago).days, 14)

		june_this_year = date_text_to_date_object('Jun 15th')
		june_2015 = date_text_to_date_object('Jun 15th, 2015')
		
		# make sure the dates returned are 14 days apart
		self.assertGreater((june_this_year - june_2015).days, 365*7)

	def test_description(self):
		'''Ensure the description parsing works'''

		# description should be at least 100 chars
		self.assertGreater(len(self.vp.description), 100)

	def test_studio_name(self):
		'''Ensure the studio name parsing works'''
		self.assertIsInstance(self.vp.studio_name, str)

	def test_director(self):
		'''Ensure the director parsing works'''
		self.assertIsInstance(self.vp.director, str)

	def test_title(self):
		'''Ensure the title parsing works'''

		# title should be at least 3 chars
		self.assertGreater(len(self.vp.title), 3)

	def test_released(self):
		'''Ensure the release date parsing is working'''

		# title should be at least 3 chars
		self.assertIsInstance(self.vp.released, datetime.date)

	def test_released_string(self):
		'''Ensure the release date parsing is working'''

		# title should be at least 3 chars
		self.assertIsInstance(self.vp.released_string, str)
		self.assertEqual(len(self.vp.released_string), 10)

	def test_banner_image_link(self):
		'''Make sure the banner image link was found'''

		# link should be at least 50 chars
		self.assertGreater(len(self.vp.banner_image_link), 50)
		self.assertTrue(self.vp.banner_image_link.startswith(
			'https://cdn.helixstudios.com/media/stills_ws'))

	def test_video_thumbnail_image_link(self):
		'''Make sure the video thumbnail image link was found'''

		# link should be at least 50 chars
		self.assertGreater(len(self.vp.video_thumbnail_image_link), 50)
		self.assertTrue(self.vp.video_thumbnail_image_link.startswith(
			'https://cdn.helixstudios.com/img'))

	def test_cast(self):
		'''Make sure the video thumbnail image link was found'''

		self.assertIsInstance(self.vp.cast, list)
		self.assertGreater(len(self.vp.cast), 0)

	def test_tags(self):
		'''Make sure the video thumbnail image link was found'''

		self.assertIsInstance(self.vp.tags, list)
		self.assertGreater(len(self.vp.tags), 5)

	def test_downloads(self):
		'''Make sure the video thumbnail image link was found'''

		self.assertIsInstance(self.vp.downloads, list)
		self.assertGreater(len(self.vp.downloads), 3)

	def test_photo_links(self):
		'''Make sure the video thumbnail image link was found'''

		self.assertIsInstance(self.vp.photo_link_list, list)
		self.assertGreater(len(self.vp.photo_link_list), 20)

	def test_find_info_items_comments(self):
		'''Make sure any comments in the info-items section are found'''

		self.assertIsInstance(self.vp._views_and_likes_comment, str)
		self.assertGreater(len(self.vp._views_and_likes_comment), 100)

	def test_view_count(self):
		'''Make sure the view count is correctly extracted from the comment.'''

		self.assertGreater(self.vp.view_count, 100)

	def test_like_count(self):
		'''Make sure the view count is correctly extracted from the comment.'''

		self.assertGreater(self.vp.like_count, 0)

	def test_details_dict_is_json_serialisable(self):
		'''Make sure the details dictionary can be successfully JSON serialised.'''

		json.dumps(self.vp.details_dictionary())



if __name__ == '__main__':
	unittest.main()





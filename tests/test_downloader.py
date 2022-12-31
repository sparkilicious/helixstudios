#!/usr/bin/env python3

'''Test the functions in the downloader.'''

import datetime
import unittest

from helixstudios import find_best_quality


SAMPLE_DOWNLOAD_LINKS = [
    {
        "item": "SD 360p",
        "link": "https://www.helixstudios.com/members/download-video.php?id=8303&s=360"
    },
    {
        "item": "SD 480p",
        "link": "https://www.helixstudios.com/members/download-video.php?id=8303&s=480"
    },
    {
        "item": "HD 720p",
        "link": "https://www.helixstudios.com/members/download-video.php?id=8303&s=720"
    },
    {
        "item": "HD 1080p",
        "link": "https://www.helixstudios.com/members/download-video.php?id=8303&s=1080"
    },
    {
        "item": "26 Photos",
        "link": "https://www.helixstudios.com/members/download-gallery.php?id=8303"
    }
]


class VideoPageTestCase(unittest.TestCase):
	'''A test case for checking the VideoListingPage class'''

	def test_find_best_quality(self):
		'''Make sure the best quality video is found.'''

		best_quality = find_best_quality(SAMPLE_DOWNLOAD_LINKS)
		self.assertEqual(best_quality['item'], 'HD 1080p')


if __name__ == '__main__':
	unittest.main()
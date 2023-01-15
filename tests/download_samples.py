#!/usr/bin/env python

'''A script to download new sample webpages from the main website.
All unittests are based on these cached html pages.'''

import os
import sys
import copy
import logging

from helixstudios import HelixSession
from helixstudios import VideoPage
from helixstudios import VideoListingPage
from helixstudios import SettingsContainer
from helixstudios import M3U8PlaylistFile


SETTINGS = {
	'username': 'my_username',
	'password': 'my_password',

	'session': '~/.config/helixstudios/session.bin',

	'links': {
		'members': 'https://www.helixstudios.com/members/',
		'videos': 'https://www.helixstudios.com/members/videos/'
	}
}


# where the sample HTML files should be downloaded to
SAMPLES_FOLDER = os.path.join(os.path.dirname(__file__), 'samples')
os.makedirs(SAMPLES_FOLDER, exist_ok=True)


# video page listing
VIDEO_LISTING_URL = 'https://www.helixstudios.com/members/videos/'


logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
log = logging.getLogger(__name__)


def sample_path(filename):
	'''Create the full path to the sample file with given filename'''
	return os.path.join(SAMPLES_FOLDER, filename)


def create_session():
	'''Create an active session with HelixStudios'''

	sc = SettingsContainer(SETTINGS)
	return HelixSession(sc, start_session=True)


def download_page(session, url, save_filename):
	'''Download the video listing landing page.'''

	code, text = session.get(url)
	with open(sample_path(save_filename), 'w') as f:
		f.write(text)

	return text



if __name__ == '__main__':
	sess = create_session()
	
	vid_list = download_page(sess, VIDEO_LISTING_URL, 'video_listing.html')
	vlp = VideoListingPage(vid_list, VIDEO_LISTING_URL)

	# download the first video and save
	vid_text = download_page(sess, vlp.all_videos().pop(), 'video.html')
	vid_page = VideoPage(vid_text, VIDEO_LISTING_URL)

	# download the first model on that page
	download_page(sess, vid_page.cast.pop()['actor_page'], 'model.html')

	# download the m3u8 playlist file from the VOD player
	playlist_text = download_page(sess, vid_page.vod_playlist_url, 'vod_playlist.m3u8')
	pl = M3U8PlaylistFile(playlist_text, vid_page.vod_playlist_url)

	# download the m3u8 file from the VOD player
	download_page(sess, pl.highest_bandwidth_stream.get('url'), 'vod_stream.m3u8')

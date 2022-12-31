#!/usr/bin/env python

'''Downloader runs the main sequence of downloads.'''

import re

from typing import Iterable

from .session import HelixSession

from .parse_video import VideoPage
from .parse_video_listing import VideoListingPage


class HelixDownloader:
	'''A downloader to grab all metadata and videos from the 
	HelixStudios website.'''

	def __init__(self, settings, start_session=True):
		self._settings = settings
		
		self._session = HelixSession(
			settings['session'], start_session=start_session)

	@property
	def session(self):
		return self._session

	def all_video_links(self, page_limit=None, video_limit=None) -> Iterable[str]:
		'''Iterate over all videos links on all pages, starting from the beginning,
		limiting the total number of either video-listing pages or videos'''

		page_count = 0
		video_count = 0

		next_page_url = self._settings['session']['links']['videos']
		
		while True:
			status_code, page_text = self.session.get(next_page_url)

			page = VideoListingPage(page_text, self.session.last_url)
			for video_link in page.all_videos():
				yield video_link

				video_count += 1
				if video_limit is not None and video_count >= video_limit:
					return

			page_count += 1
			if page_limit is not None and page_count >= page_limit:
				return

			next_page_url = page.next_page

	def all_video_pages(self, page_limit=None, video_limit=None) -> Iterable[VideoPage]:
		'''Iterate over all videos, downloading the pages for each and yield the video pages'''

		for link in self.all_video_links(page_limit=page_limit, video_limit=video_limit):
			status, page_text = self.session.get(link)

			page = VideoPage(page_text, self.session.last_url)
			yield page


def _resolution(quality_description):
	'''Return the resolution as an int, 0 if it cannot be found.'''

	my_int = re.search(r'\d+', quality_description)
	if my_int:
		return int(my_int.group(0))
	else:
		return 0


def find_best_quality(link_list):
	'''Accepts a list of video download links, and returns the highest quality.'''

	# make sure there's no links to Photos
	vid_links = [d for d in link_list if 'photo' not in d['item'].lower()]

	qualities = [_resolution(v['item']) for v in vid_links]
	return vid_links[qualities.index(max(qualities))]



#!/usr/bin/env python

'''Parse the video listing pages for links to videos and the navigation 
buttons to find the next page of videos.'''

from .parse_utils import Tag, TagClass
from .parse_utils import Page, flatten_html

from urllib.parse import urlparse


# the <a> tag and css class of the video links
VIDEO_LINK = TagClass('a', 'thumbnail-link')

# the <a> tag and css class of the "next" page button
NEXT_PAGE = TagClass('a', 'next')


class VideoListingPage(Page):
	'''A parser for the general video listing page'''

	def _video_link_iter(self):
		for l in self.find_all(VIDEO_LINK):
			yield self._base_url.rstrip('/') + l['href']

	def all_videos(self):
		'''Return a list of all video links on the listing page'''
		return list(self._video_link_iter())
	
	@property
	def next_page(self):
		'''Find the link to the next page'''

		link = self.find(NEXT_PAGE)

		if link is not None:
			# link has a leading //, strip it out along with host ("netloc")
			path = urlparse(link['href'])._replace(netloc='').geturl()
			return self._base_url.rstrip('/') + path



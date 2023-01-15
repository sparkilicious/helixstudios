#!/usr/bin/env python

'''Parse the video page for all video metadata and links.'''

import re
import json
import datetime

from functools import cached_property

from bs4 import Comment
from bs4 import BeautifulSoup

from .parse_utils import Tag, TagClass, TagId
from .parse_utils import TagClassAttr, TagIdAttr
from .parse_utils import Page, flatten_html

DATE_FORMAT = '%Y-%m-%d'



# html tag definitions for the data we want
VIDEO_TITLE = Tag('h1')
VIDEO_DESCRIPTION1 = TagClass('div', 'description-content')
VIDEO_DESCRIPTION2 = TagClass('div', 'video-description')
VIDEO_RELEASED = TagClass('span', 'info-item date')
VIDEO_STUDIO = TagClass('span', 'studio-name')
VIDEO_DIRECTOR = TagClass('span', 'info-item director')
VIDEO_INFO_ITEMS = TagClass('div', 'info-items')

LINK_BANNER_IMAGE = TagIdAttr('img', 'titleImage', 'src')
LINK_VIDEO_THUMBNAIL = TagClassAttr('video', 'video-js vjs-default-skin', 'poster')

VIDEO_CAST_SECTION = TagClass('div', 'video-cast')
VIDEO_CAST_MEMBER = TagClass('a', 'thumbnail-link')
VIDEO_CAST_THUMBNAIL = TagClassAttr('img', 'pure-img lazyload thumbnail-img', 'src')

TAG_SECTION = TagClass('div', 'video-tags-wrapper')
DOWNLOAD_SECTION = TagClass('div', 'downloads-link-wrapper')
PHOTO_SECTION = TagClass('div', 'main-section video-gallery')

STREAMING_PLAYER_TAG = TagId('video', 'sparkplayer2')

ITEMS = Tag('a')

# view count and like count are commented out in the HTML, but the data
# is still there in the comment and is accruate for each video!
VIEWS_REGEX = re.compile(r'<span class="info-item views"><i [- a-z="]+></i>\s*([0-9.k]+)\s*views</span>', re.IGNORECASE)
LIKES_REGEX = re.compile(r'<span class="like-count">([0-9.k]+)</span>', re.IGNORECASE)


def video_page_url_to_video_name(url):
	'''Convert the URL for the video to a unique folder name'''
	return '_'.join(url.split('/')[-2:]).replace('-', '_')


class VideoPage(Page):
	'''Parser for the individual video pages'''
	
	def __repr__(self):
		return f'<VideoPage("{self.video_folder_name}")>'

	@cached_property
	def video_folder_name(self):
		'''Return a unique video folder name for this video'''
		return '_'.join(self.url.split('/')[-2:]).replace('-', '_')

	@cached_property
	def title(self):
		'''The video title.'''

		title = self.find(VIDEO_TITLE)
		return flatten_html(title.contents)

	@cached_property
	def description(self):
		'''Find the text description of the video'''

		description = self.find(VIDEO_DESCRIPTION1)
		if description is None:
			description = self.find(VIDEO_DESCRIPTION2)
		if description is None:
			return ''
		else:
			return flatten_html(description.contents)

	@cached_property
	def studio_name(self):
		'''Find the text description of the video'''

		studio = self.find(VIDEO_STUDIO)
		if studio is None:
			return ''
		else:
			return flatten_html(studio.contents)

	@cached_property
	def director(self):
		'''Find the text description of the video'''

		# the director tag is f'ed up, needs some fixing, it has the 
		# director string inside the tag.
		director = self.find(VIDEO_DIRECTOR)
		if director is None:
			return ''

		text = flatten_html(director.contents)
		if text.lower().startswith('director'):
			return text[8:]
		else:
			return text

	@cached_property
	def _release_date_raw(self):
		'''The raw date text of when the video was released. This will be one
		of 3 types, "Today", "20 days ago", "Aug 6th", "Jan 31st, 2015".'''

		release_text = self.find(VIDEO_RELEASED)
		return flatten_html(release_text.contents)

	@cached_property
	def released(self):
		'''The date the video was released, as a datetime object.'''
		return date_text_to_date_object(self._release_date_raw)

	@cached_property
	def released_string(self):
		'''The date the video was released, as a datetime object.'''
		return self.released.strftime(DATE_FORMAT)

	@cached_property
	def _views_and_likes_comment(self):
		'''Find the commented out section of code that has the views and likes'''

		info_items = self.find(VIDEO_INFO_ITEMS).find_all(
							string=lambda text: isinstance(text, Comment))
		return flatten_html(info_items)

	def _extract_views_likes_using_regex(self, regex):
		'''Parse the comments and likes text using a regex'''

		value = 0
		
		result = regex.search(self._views_and_likes_comment)
		if result:
			try:
				value = string_count_to_int(result.group(1))
			except ValueError:
				pass   # it's not valid, return 0
		
		return value

	@cached_property
	def view_count(self):
		'''Return the number of views the video has'''
		return self._extract_views_likes_using_regex(VIEWS_REGEX)

	@cached_property
	def like_count(self):
		'''Return the number of views the video has'''
		return self._extract_views_likes_using_regex(LIKES_REGEX)

	@cached_property
	def banner_image_link(self):
		'''A link to the banner image across the top of the page'''
		return self.find(LINK_BANNER_IMAGE)
	
	@cached_property
	def video_thumbnail_image_link(self):
		'''A link to the banner image across the top of the page'''
		return self.find(LINK_VIDEO_THUMBNAIL)
	
	def _cast_member_section_iter(self):
		'''Iterate through the cast members, and return one section
		for each actor'''

		for link in self.find(VIDEO_CAST_SECTION).find_all(VIDEO_CAST_MEMBER):
			actor_page = self._base_url.rstrip('/') + link.get('href', '')
			actor_name = link.get('title', '')
			_actor_img_tag = link.find('img', attrs={'class': 'pure-img lazyload thumbnail-img'})
			actor_thumbnail = _actor_img_tag.get('src', '')
			
			yield {
				'actor_page': actor_page,
				'actor_name': actor_name,
				'actor_thumbnail': actor_thumbnail
			}

	@cached_property
	def cast(self):
		'''A list of all cast details'''
		return list(self._cast_member_section_iter())

	def _section_iter(self, section_search, items, attr_name):
		'''Iterate through all category sections'''

		results = self.find(section_search)
		if results is None:
			return

		for link in results.find_all(items):
			link_prefix = '' if link.get(attr_name, '').startswith('http') else self._base_url.rstrip('/')
			yield {
				'item': flatten_html(link.contents),
				'link': link_prefix + link.get(attr_name, '')
			}

	@cached_property
	def tags(self):
		'''A list of all cast details'''
		return list(self._section_iter(TAG_SECTION, ITEMS, 'href'))

	@cached_property
	def downloads(self):
		'''A list of all download details'''
		return list(self._section_iter(DOWNLOAD_SECTION, ITEMS, 'href'))

	@cached_property
	def photo_link_list(self):
		'''A list of all download details'''
		return [photo.get('link') for photo in self._section_iter(
			PHOTO_SECTION, ITEMS, 'href')]

	@cached_property
	def vod_playlist_url(self):
		'''Download the VOD embedded player list of available streaming quality
		versions of the video.'''

		video_tag = self.find(STREAMING_PLAYER_TAG)
		if video_tag is None:
			raise ValueError('streaming play could not be found')

		source_tag = video_tag.find('source')
		if source_tag is None:
			raise ValueError('streaming player has no "source" tag')

		src = source_tag.get('src')

		# take off the leading / if there is one
		src = src[1:] if src.startswith('/') else src

		return None if src is None else self.base_url + src

	def details_dictionary(self):
		'''Return all details parsed from the page as a dictionary'''

		return {
			'url':                         self.url,
			'title':                       self.title,
			'description':                 self.description,
			'studio_name':                 self.studio_name,
			'director':                    self.director,
			'released':                    self.released_string,
			'view_count':                  self.view_count,
			'like_count':                  self.like_count,
			'banner_image_link':           self.banner_image_link,
			'video_thumbnail_image_link':  self.video_thumbnail_image_link,
			'cast':                        self.cast,
			'tags':                        self.tags,
			'downloads':                   self.downloads,
			'photo_link_list':             self.photo_link_list
		}

	@property
	def details_dictionary_is_json_serialisable(self):
		'''Return true if the details dictionary can be flattened to JSON'''

		try:
			json.dumps(video_page.details_dictionary())
		except Exception:
			return False
		else:
			return True


DAYS_AGO_REGEX = re.compile(r'([0-9]+) days? ago', re.IGNORECASE)
MONTH_YEAR_REGEX = re.compile(r'(?P<date>[A-Za-z]+ [0-9]+)[a-z]+(?P<year>, [0-9]{4})?')

def date_text_to_date_object(date_text):
	'''Convert one of the many date text formats to a date object.'''

	if date_text.lower() == 'today':
		return datetime.date.today()
	if date_text.lower() == 'yesterday':
		return datetime.date.today() - datetime.timedelta(days=1)

	days_ago = DAYS_AGO_REGEX.match(date_text)
	if days_ago:
		return datetime.date.today() - datetime.timedelta(days=int(days_ago.group(1)))

	month_year = MONTH_YEAR_REGEX.match(date_text)
	if month_year:
		clean_date_text = month_year.group('date') + (
					month_year.group('year') or f', {datetime.date.today().year}')
		return datetime.datetime.strptime(clean_date_text, '%b %d, %Y')

	raise ValueError(f'date not recognised: {date_text}')


MULTIPLIERS = {
	'none': 1,
	'k': pow(10, 3),
	'm': pow(10, 6),
	'g': pow(10, 9)
}

def string_count_to_int(string_number):
	'''Convert a string integer to an actual integer. The integer can have 
	a trailing letter like 'k' or 'M' to represent 10^3 or 10^6'''

	num = re.match(r'(?P<num>[0-9.]+)\s*(?P<mult>[a-z])?', string_number.lower())
	if num:
		number, multiplier = num.group('num'), num.group('mult') or 'none'
		if multiplier not in MULTIPLIERS:
			raise ValueError(f'multiplier "{multiplier}" not recognised for: {string_number}')
		else:
			return int(float(number) * MULTIPLIERS.get(multiplier))
	else:
		raise ValueError(f'number not recognised: {string_number}')





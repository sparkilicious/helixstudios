#!/usr/bin/env python

'''Parse the video page for all video metadata and links.'''

import bs4

from bs4 import BeautifulSoup
from urllib.parse import urlparse

from collections import namedtuple

Tag = namedtuple('Tag', ['tag'])
TagClass = namedtuple('TagClass', ['tag', 'cls'])
TagId = namedtuple('TagId', ['tag', 'id'])

def base_url(url):
	'''Return the base URL for any link, just the protocol
	and hostname section.'''

	uri = urlparse(url)
	return f'{uri.scheme}://{uri.netloc}/'


class Page:
	'''A generic Beautiful Soup page parser'''

	def __init__(self, page_text, page_final_url):
		self._page_text = page_text
		self._page = BeautifulSoup(self._page_text, 'html.parser')

		self._url = page_final_url
		self._base_url = base_url(self._url)

	@property
	def url(self):
		return self._url

	@property
	def page(self):
		return self._page

	@property
	def page_text(self):
		return self._page_text
	
	@property
	def base_url(self):
		'''The base URL if this page, just the protocol and hostname'''
		return self._base_url

	def find(self, item, *args, **kwargs):
		if isinstance(item, Tag):
			return self.page.find(item.tag, *args, **kwargs)
		elif isinstance(item, TagClass):
			return self.page.find(item.tag, *args,
								  attrs={'class': item.cls}, **kwargs)
		elif isinstance(item, TagId):
			return self.page.find(item.tag, *args,
								  attrs={'id': item.id}, **kwargs)
		else:
			return self.page.find(item, *args, **kwargs)

	def find_all(self, item, *args, **kwargs):
		if isinstance(item, Tag):
			return self.page.find_all(item.tag, *args, **kwargs)
		elif isinstance(item, TagClass):
			return self.page.find_all(item.tag, *args,
								  attrs={'class': item.cls}, **kwargs)
		elif isinstance(item, TagId):
			return self.page.find_all(item.tag, *args,
								  attrs={'id': item.id}, **kwargs)
		else:
			return self.page.find_all(item, *args, **kwargs)
	

def _flatten_iter(tag, paragraph_delimiter='\n'):
	'''An iterator to work through all levels of the HTML'''

	if isinstance(tag, list):
		for t in tag:
			yield from _flatten_iter(t)

	elif isinstance(tag, bs4.element.Tag):
		yield from _flatten_iter(tag.contents)
		if tag.name == 'p':
			yield paragraph_delimiter

	elif isinstance(tag, bs4.element.NavigableString):
		yield str(tag).strip()


def flatten_html(tags, paragraph_delimiter='\n'):
	'''Take a list of BS tags, flatten all HTML to text.'''
	return ''.join(_flatten_iter(tags, paragraph_delimiter=paragraph_delimiter))

	
#!/usr/bin/env python

'''Parse the video page for all video metadata and links.'''

import re
import bs4

from .utils import base_url

from bs4 import BeautifulSoup

from collections import namedtuple
from functools import cached_property


Tag = namedtuple('Tag', ['tag'])
TagClass = namedtuple('TagClass', ['tag', 'cls'])
TagClassAttr = namedtuple('TagClassAttr', ['tag', 'cls', 'attr'])
TagId = namedtuple('TagId', ['tag', 'id'])
TagIdAttr = namedtuple('TagId', ['tag', 'id', 'attr'])


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

	@cached_property
	def webpage_title(self):
		'''The HTML title of the webpage'''
		title = self.page.find('title')
		if title:
			return title.string

	def find(self, item, *args, **kwargs):
		return find_dispatch(self.page.find, item, *args, **kwargs)

	def find_all(self, item, *args, **kwargs):
		return find_dispatch(self.page.find_all, item, *args, **kwargs)
	

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


def find_dispatch(find_func, search_obj, *args, **kwargs):
	'''A dispatch function to call the find/find_all function with 
	the correct args, based on the search object provided.'''

	if isinstance(search_obj, Tag):
		return find_func(search_obj.tag, *args, **kwargs)
	elif isinstance(search_obj, TagClass):
		return find_func(search_obj.tag, *args,
						 attrs={'class': search_obj.cls}, **kwargs)
	elif isinstance(search_obj, TagClassAttr):
		obj = find_func(search_obj.tag, *args,
						attrs={'class': search_obj.cls}, **kwargs)
		return _attr_lookup(obj, search_obj.attr)
	elif isinstance(search_obj, TagId):
		return find_func(search_obj.tag, *args,
						 attrs={'id': search_obj.id}, **kwargs)
	elif isinstance(search_obj, TagIdAttr):
		obj = find_func(search_obj.tag, *args,
						attrs={'id': search_obj.id}, **kwargs)
		return _attr_lookup(obj, search_obj.attr)
	else:
		raise TypeError('search object is not a search tuple')


def _attr_lookup(obj, attr):
	'''For a given object returned by the find/find_all functions,
	return the named attribute of the tags.'''

	if not obj:
		return obj  # obj is None or empty list
	elif isinstance(obj, bs4.element.Tag):
		return obj.get(attr)
	elif isinstance(obj, list):
		return [_attr_lookup(o) for o in obj]
	else:
		raise TypeError(f'unrecognised type: {type(obj)}')


def cleanup_string(my_str):
	'''Strip all unprintable characters from a string and collapse
	them all into a single space.'''

	return re.sub(r'\s+', ' ', my_str)

#!/usr/bin/env python

'''Parse the video listing pages for links to videos and the navigation 
buttons to find the next page of videos.'''

from .parse_utils import Tag, TagClass
from .parse_utils import Page, flatten_html
from .parse_utils import find_dispatch, cleanup_string

from urllib.parse import urlparse
from functools import cached_property


MODEL_NAME = Tag('h1')
MODEL_DESCRIPTION = TagClass('div', 'description')

MODEL_STATS_LABELS = TagClass('div', 'model-stats-table')
MODEL_STATS_LABELS_ITEM = TagClass('span', 'label')

MODEL_STATS_VALUES = TagClass('div', 'model-stats hide show-lg')
MODEL_STATS_VALUES_ITEM = TagClass('span', 'stat-item')


class ModelPage(Page):
	'''A parser for the general video listing page'''

	@cached_property
	def model_name(self):
		'''The model's name.'''

		model_name = self.find(MODEL_NAME)
		return flatten_html(model_name.contents)

	@cached_property
	def description(self):
		'''The model's bio/description.'''

		desc = self.find(MODEL_DESCRIPTION)
		return flatten_html(desc.contents)

	def _get_list_of_items(self, block_obj, item_obj):
		'''Return a list of items parsed from the given block object.'''

		block = self.find(block_obj)
		if not block:
			return []
		else:
			return [cleanup_string(flatten_html(item)) 
				for item in find_dispatch(block.find_all, item_obj)]

	@cached_property
	def stats(self):
		'''The model's stats table.'''

		labels = self._get_list_of_items(MODEL_STATS_LABELS, MODEL_STATS_LABELS_ITEM)
		values = self._get_list_of_items(MODEL_STATS_VALUES, MODEL_STATS_VALUES_ITEM)

		return dict(zip(labels, values))



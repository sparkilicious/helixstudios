#!/usr/bin/env python

'''random utilities that are useful across the application'''

import os
import math
import logging

from urllib.parse import urlparse, urlsplit, urlunsplit

from logging import handlers
from os.path import join, dirname


LOG_FORMAT = '[%(asctime)s]::[%(module)-20.20s]::[%(funcName)-25.25s]::[%(lineno)4d]::[%(levelname)-8s] %(message)s'


def dict_diver(dictionary, *loc, default=None):
	'''Dive into a nested dictionary, returning the value at the end of the dive.'''
	try:
		return dict_diver(dictionary[loc[0]], *loc[1:], default=default)
	except KeyError:
		return default
	except IndexError: # the `loc` tuple is empty, we're done!
		return dictionary


def dict_diver_set(dictionary, *loc, value=None):
	'''Dive into a nested dictionary, set the value at the end of the dive.'''

	if len(loc) == 1:
		dictionary[loc[0]] = value
	else:
		dict_diver_set(dictionary[loc[0]], *loc[1:], value=value)


def configure_logging(path, level=logging.DEBUG, backups=7):
    '''Configure the logger to auto-rotate the logs every so often.'''

    # rotate the log file every 10MB
    rotating_file = handlers.RotatingFileHandler(path, 
        maxBytes=int(10.0e6), backupCount=backups
    )

    logging.basicConfig(level=level, format=LOG_FORMAT, handlers=[rotating_file])
    return logging.getLogger('')


def disable_logging():
	logging.basicConfig(handlers=[logging.NullHandler()])
	return logging.getLogger('')


# taken from https://stackoverflow.com/a/14822210
SIZE_NAMES = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
def bytes_to_string(size_bytes):
   if size_bytes == 0:
       return "0 B"
   i = int(math.floor(math.log(size_bytes, 1024)))
   p = math.pow(1024, i)
   s = round(size_bytes / p, 2)
   return f'{size_bytes / p:.2f} {SIZE_NAMES[i]}'


def base_url(url):
	'''Return the base URL for any link, just the protocol
	and hostname section.'''

	uri = urlparse(url)
	return f'{uri.scheme}://{uri.netloc}/'

def parent_url(url, clean_query=True, clean_fragment=True):
	'''Return the url for 1 directory up from the current'''

	uri = urlparse(url)
	updated = uri._replace(path = os.path.dirname(uri.path))

	if clean_query:
		updated = updated._replace(query='')

	if clean_fragment:
		updated = updated._replace(fragment='')

	return updated.geturl()

def localise_url(url, source_url):
	'''Build a full url to some content harvested on the page
	at source_url. Automatically choose the correct url pieces
	to make the URL complete.'''

	uri = urlparse(url)

	if uri.scheme == '' and uri.netloc == '':
		# this is either host level or relative
		if url.startswith('/'):
			# host level
			return base_url(source_url) + url[1:]
		else:
			# relative to source level
			return parent_url(source_url) + '/' + url
	else:
		# this is already a full URL with a hostname at least - no edits
		return uri.geturl()
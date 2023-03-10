#!/usr/bin/env python

'''Keeps track of all cookies and other tokens required to maintain 
a session across different runs of the application'''

import os
import sys
import time
import pprint
import pickle
import logging
import threading

import requests
import requests.utils
from requests.exceptions import ChunkedEncodingError
from requests.exceptions import ConnectionError
from requests.exceptions import ReadTimeout

# parent class to all requests exceptions
from requests.exceptions import RequestException

from .utils import bytes_to_string

CHUNK_SIZE = 32 * 1024  # 32kB


log = logging.getLogger(__name__)


class LoggedOut(RuntimeError):
	pass


class HelixSession:
	'''Provides all necessary infrastructure to contact HelixStudio
	and hides the session management stuff from the Downloader'''

	def __init__(self, settings, start_session=True):
		self._session = requests.Session()
		self._settings = settings
		self._last_page_downloaded = None
		self._last_url = None

		self._downloaded = None
		self._last_downloaded = None
		self._progress_printing_disabled = False
		self._filesize = None
		self._closing = threading.Event()

		self._prog = threading.Thread(target=self._progress_printer)
		self._prog.daemon = True
		self._prog.start()

		if start_session:
			self.start_session()
		
	def _get_path_from_settings(self, setting_name):
		'''Get the full path to the given file from the settings.
		Create the folder if it doesn't exist.'''

		path = self._settings.get_path(setting_name)
		os.makedirs(os.path.dirname(path), exist_ok=True)
		return path

	@property
	def session_file(self):
		'''Get the path to the session file.'''
		return self._get_path_from_settings('session')

	@property
	def cookies(self):
		return requests.utils.dict_from_cookiejar(self._session.cookies)

	def _store_session(self):
		'''Pickle the session to disk.'''

		with open(self.session_file, 'wb') as f:
			pickle.dump(self._session, f)
		
		log.info('Successfully stored session to disk')

	def _load_session(self):
		'''Load session from disk'''

		if not os.path.exists(self.session_file):
			log.error('No session to restore')
			return False

		with open(self.session_file, 'rb') as f:
			self._session = pickle.load(f)
			log.info('Successfully restored session from disk')
			return True

	@property
	def auth(self):
		'''The auth details, as required by requests'''
		username = self._settings.get('username')
		password = self._settings.get('password')

		return (username, password)
	
	@property
	def user_logged_in(self):
		'''Return true if the session is valid, false otherwise'''
		
		url = self._settings['links']['members']
		status_code, _ = self.get(url)
		if status_code == 200:
			log.debug('User is logged in')
			return True
		else:
			log.warning(f'User is not logged in, status code: {resp.status_code}')

	@property
	def last_page_content(self):
		'''The content of the last downloaded page.'''
		return self._last_page_downloaded

	@property
	def last_url(self):
		'''The final URL of the last request after all redirects.'''
		return self._last_url

	def _log_headers(self, headers, level=logging.DEBUG):
		'''Dump the response headers to the log.'''

		log.log(level, '  Headers:')
		for l in pprint.pformat(dict(headers.items())).splitlines():
			log.log(level, '    {}'.format(l))
		log.log(level, '')

	def _log_cookies(self, level=logging.DEBUG):
		'''Dump the response headers to the log.'''

		log.log(level, 'Cookies:')
		for l in pprint.pformat(dict(self.cookies.items())).splitlines():
			log.log(level, '  {}'.format(l))
		log.log(level, '')

	def login(self):
		'''Attempt the login flow'''

		username, _ = self.auth
		members_url = self._settings['links']['members']

		log.info(f'Attempting login for user "{username}"')
		
		# reset the current session
		self._session = requests.Session()

		# login
		resp = self._session.get(members_url, auth=self.auth,
								 timeout=self._settings.get('timeout', default=10))

		if resp.status_code == 200:
			log.info('Successful login!')
			self._store_session()
			self._log_headers(resp.headers)
		else:
			log.error(u'Unsuccessful login, HTTP code {} was returned.'.format(resp.status_code))
			self._log_headers(resp.headers, level=logging.ERROR)
			raise RuntimeError('login failed')

	def start_session(self):
		'''Begin the session with Helix Studios. Load session from disk, and test
		the whether it's still logged in. If not, log in again.'''

		if self._load_session():
			# there was a cookie file loaded, test the members landing page
			if self.user_logged_in:
				return
		
		self.login()

	def _cleanup(self):
		'''Cleanup the session between requests'''

		if 'Range' in self._session.headers:
			del(self._session.headers['Range'])

		self._last_page_downloaded = None

	def set_start_byte_offset(self, byte_offset):
		'''Set the "Range" header to begin the download at the given byte offset'''
		self._session.headers.update({'Range': f'bytes={byte_offset}-'})

	def get(self, url, retries=10):
		'''Takes a URL and returns a tuple of (code, response).'''

		for i in range(retries):
			try:
				self._cleanup() 
				resp = self._session.get(url, stream=False, auth=self.auth,
										 timeout=self._settings.get('timeout', default=10))

				self._last_page_downloaded = resp.text
				self._last_url = resp.url
				
				if 400 <= resp.status_code <= 499:
					raise LoggedOut()
				
				return resp.status_code, self._last_page_downloaded	

			except LoggedOut:
				log.error(f'HTTP Code {resp.status_code} while requesting: {url}, re-attempting login')

				try:
					self.login()
				except RuntimeError:
					log.error('Login failed!')
					log.error('Retrying page request again, and we\'ll reattempt login next time around!')

			except RequestException as e:
				sleep_time = min([2 ** i, 60])    # double sleep time with each failed request, max 60 secs.

				log.error(f'{e.__class__.__name__} while requesting GET: {url}')
				log.error(f' ---> {str(e)}')
				log.error(f'Sleeping for {sleep_time} seconds for connection to recover...')
				time.sleep(sleep_time)

		else:
			log.error(f'All GET request attempts have failed for url: {url}')
			raise RuntimeError('all GET request attempts failed')

	def head(self, url, retries=10):
		'''Perform a HTTP HEAD request and return the status code, final url, and headers'''

		for i in range(retries):
			try:
				self._cleanup() 
				resp = self._session.head(url, allow_redirects=True, auth=self.auth,
										  timeout=self._settings.get('timeout', default=10))
				
				return resp.status_code, resp.url, resp.headers

			except RequestException as e:
				sleep_time = min([2 ** i, 60])    # double sleep time with each failed request, max 60 secs.

				log.error(f'{e.__class__.__name__} while requesting HEAD: {url}')
				log.error(f' ---> {str(e)}')
				log.error(f'Sleeping for {sleep_time} seconds for connection to recover...')
				time.sleep(sleep_time)

		else:
			log.error(f'All HEAD request attempts have failed for url: {url}')
			raise RuntimeError('all HEAD request attempts failed')

	def _print_progress(self, progress, speed=''):
		'''Print a progress message to the terminal'''

		sys.stderr.write(f'   {progress:.1f}%  {speed}                    \r')
		sys.stderr.flush()

	def _progress_printer(self):
		'''Periodically print the '''

		PRINT_PROGRESS_EVERY = 3   # seconds

		while True:
			if self._closing.is_set():
				break

			if self._progress_printing_disabled:
				pass

			elif self._downloaded is not None:
				if self._last_downloaded is not None:
					# calculate the download speed
					bytes_downloaded = self._downloaded - self._last_downloaded
					speed_b_per_s = bytes_downloaded / PRINT_PROGRESS_EVERY
					speed = f'[{bytes_to_string(speed_b_per_s)}/s]'
				else:
					speed = ''

				# important to record this variable before the print, so we don't 
				# give up the GIL and introduce a timing bug
				self._last_downloaded = self._downloaded

				progress = (100.0 * self._downloaded) / self._filesize
				self._print_progress(progress, speed=speed)

			self._closing.wait(PRINT_PROGRESS_EVERY)

	def download(self, url, destination_path, download_in_place=False, retries=20):
		'''Download a large file in chunks and write it to disk at the given destination.
		Resume partially downloaded files where possible. Return True if the download was
		successful, False if the file wasn't downloaded because it was already complete.'''

		for i in range(retries):
			try:
				self._cleanup()   # remove any wayward request headers

				if not download_in_place:
					dest = destination_path + '.part'
				else:
					dest = destination_path

				# perform a head request on the link to find out how big it is
				status_code, final_url, headers = self.head(url)

				if status_code == 404:
					log.error(f'Received 404 for URL: {url}')
					log.error('  -> this video file will be skipped!')
					return

				self._filesize = int(headers.get('Content-Length'))
				
				if self._filesize == 0:
					log.error(f'Filesize is zero for URL {url}')
					log.error('  -> this video file will be skipped!')
					return

				# check for the destination file on disk
				if os.path.isfile(dest):
					size_on_disk = os.path.getsize(dest)

					if self._filesize > size_on_disk:
						log.info(f'Resuming download from byte {size_on_disk}, {self._filesize - size_on_disk} bytes left')
						self.set_start_byte_offset(size_on_disk)
					else:
						log.info(f'File download was already complete')
						return False
				else:
					log.info(f'Starting fresh file download...')
					
				resp = self._session.get(url, stream=True, auth=self.auth,
										 timeout=self._settings.get('timeout', default=10))
				
				if resp.status_code == 416:
					log.error(u'HTTP Error 416 - "Range" request was not valid')
					log.error(u'This file cannot be downloaded')
					return

				elif 400 <= resp.status_code <= 499:
					raise LoggedOut()

				with open(dest, 'ab') as f:
					for chunk in resp.iter_content(chunk_size=CHUNK_SIZE):
						if len(chunk) > 0:     # filter out keep-alive chunks
							f.write(chunk)
						self._downloaded = f.tell()

				# reset both so progress isn't printed until the next file
				self._downloaded = None
				self._last_downloaded = None
				
				if not download_in_place:
					# move the file into place
					if os.path.isfile(destination_path):
						log.warning('Destination file already exists, deleting now...')
						os.remove(destination_path)

					log.debug('Moving downloaded file into place now...')
					os.rename(dest, destination_path)

				log.info(f'Download complete!')

				return True

			except LoggedOut:
				log.error(u'HTTP Code 400-499 encountered...')

			except RequestException as e:
				sleep_time = min([2 ** i, 60])    # double sleep time with each failed request, max 60 secs.

				log.error(f'{e.__class__.__name__} while downloading: {url}')
				log.error(f' ---> {str(e)}')
				log.error(f'Sleeping for {sleep_time} seconds for connection to recover...')
				time.sleep(sleep_time)

	def _vod_ts_files_for_playlist(self, playlist_url):
		'''Given a playlist URL, generate the download URLs for all the TS files'''

		status_code, page = self.get(playlist_url)
		if status_code != 200:
			raise ValueError('unable to download playlist file')

		

	def download_vod(self, url, destination_path, download_in_place=False, retries=20):
		'''Given a URL to a streaming video M3U8 file, download all the TS files 
		for the highest resolution version of the video.'''

		# during VOD downloads, disable the progress dialog because it's too
		# complicated to manage the dance with the download function
		self._progress_printing_disabled = False

		# streaming videos will never be resumed, delete anything that exists there
		if os.path.isfile(destination_path):
			os.remote(destination_path)




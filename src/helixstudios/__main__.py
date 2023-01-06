#!/usr/bin/env python3

'''A library for maintaining a local library of video from HelixStudios'''

import os
import sys
import json
import logging
import argparse

from .parse_video import VideoPage
from .settings import SettingsYAML
from .utils import configure_logging
from .downloader import HelixDownloader
from .downloader import find_best_quality

from .parse_video import video_page_url_to_video_name

log = None


def main():
	try:
		_main()
	except KeyboardInterrupt:
		log.info('User interrupt, exiting...')
		print('User interrupt, exiting...')
	except:
		log.error('App exiting with exception:\n', exc_info=True)
		raise


def _main():
	global log

	args = cmdline_args()
	settings = SettingsYAML(args.settings)
	log = setup_logging(settings)


	if args.rebuild_nfo:
		build_nfo(args, settings)

	else:
		download(args, settings)


def cmdline_args():
	'''Parse the command line arguments'''

	parser = argparse.ArgumentParser(description=__doc__)
	parser.add_argument('settings', help='path to the settings YAML file')
	parser.add_argument('--page-limit', type=int, help='Max number of video page listings to download')
	parser.add_argument('--video-limit', type=int, help='Max number of videos to download')
	parser.add_argument('--retry-count', type=int, default=10, help='Maximum number of failed connection attempts before exiting')
	parser.add_argument('--force-download-video', default=False, action='store_true', 
		help="If the video file already exists on disk, don't assume the download is complete, try to resume the download anyway")

	action = parser.add_mutually_exclusive_group(required=False)
	action.add_argument('--metadata-only', default=False, action='store_true', help='Only download metadata, no videos')
	action.add_argument('--rebuild-nfo', default=False, action='store_true', help='Rebuild NFO files using only the local video page caches')

	return parser.parse_args()


def setup_logging(settings):
	'''Use the settings to configure the logging infrastructure'''

	# setup logging
	if settings.get('logging', 'enabled'):
		level_name = settings.get('logging', 'level') or 'ERROR'
		if not hasattr(logging, level_name):
			raise ValueError(f'logging level "{level_name}" is not valid')

		return configure_logging(settings.get_path('logging', 'file'), 
								 level=getattr(logging, level_name))
	else:
		return disable_logging()


def download(args, settings):
	'''Create a connection to HelixStudios and begin the download process'''
	
	# create the session/download manager
	downloader = HelixDownloader(settings)

	video_count = 0
	for video_url in downloader.all_video_links(page_limit=args.page_limit, retries=args.retry_count):
		folder, video_full_path, video_library_path = url_to_download_path(video_url, settings)

		if file_already_downloaded(video_full_path, video_library_path, settings) and not args.force_download_video:
			continue

		log.info(f'Starting video #{video_count}: {video_library_path}')

		status, page_text = downloader.session.get(video_url, retries=args.retry_count)
		video_page = VideoPage(page_text, downloader.session.last_url)

		os.makedirs(folder, exist_ok=True)
	
		# dump the metadata to disk
		handle_video_page(video_page, settings, folder)

		# now manage the downloads
		if not args.metadata_only:
			download_successful = download_video(video_page, settings, folder, downloader, retries=args.retry_count)
			if download_successful:
				video_count += 1
		else:
			video_count += 1

		# exit if the video limit was exceeded
		if args.video_limit is not None and video_count >= args.video_limit:
			log.info(f'Video download limit of {args.video_limit} has been reached!')
			return


def url_to_download_path(url, settings):
	'''Take the video page url and convert it to the download folder 
	and the video path for the downloaded video.'''

	root = settings.get_path('library', 'download_root')
	video_name_stem = video_page_url_to_video_name(url)
	video_library_path = os.path.join(video_name_stem, f'{video_name_stem}.mp4')
	folder = os.path.join(root, video_name_stem)
	video_full_path = os.path.join(root, video_library_path)
	return folder, video_full_path, video_library_path


def file_already_downloaded(video_full_path, video_library_path, settings):
	'''Return True if this video file has already been downloaded'''

	if os.path.isfile(video_full_path):
		log.info(f'Video file "{video_library_path}" already exists in download root folder')
		return True

	# loop over all additional folders and check there too
	for folder in settings.get_path_list('library', 'additional_library_folders', default=[]):
		video_path = os.path.join(folder, video_library_path)
		if os.path.isfile(video_path):
			log.info(f'Video file "{video_library_path}" already exists in additional library folder "{folder}"')
			return True

	return False


def handle_video_page(video_page, settings, path):
	'''Handle the download of a single video page, and all associated metadata'''

	dump_metadata(video_page, settings, path)


def dump_metadata(video_page, settings, folder):
	'''Dump all the metadata to disk if the user wanted it'''

	# write the page text
	if settings.get('library', 'save_video_page_to_library'):
		with open(os.path.join(folder, settings.get('library', 'video_page_filename')), 'w') as f:
			f.write(video_page.page_text)

	# write the json data
	if settings.get('library', 'save_json_data_to_library'):
		with open(os.path.join(folder, settings.get('library', 'json_data_filename')), 'w') as f:
			f.write(json.dumps(video_page.details_dictionary(), indent=4))


def download_video(video_page, settings, folder, downloader, retries=10):
	'''Download the highest quality video to the given folder in the library'''

	if not video_page.downloads:
		log.warning('No download links found for this video, skipping!')
		return False
	
	best = find_best_quality(video_page.downloads)
	video_path = os.path.join(folder, f'{os.path.basename(folder)}.mp4')

	sys.stderr.write(f'{os.path.basename(video_path)}.mp4 - "{video_page.title}"\n')
	sys.stderr.flush()

	status = downloader.session.download(best['link'], video_path, retries=retries)
	if status:
		downloader.session._print_progress(100.0)

	return status


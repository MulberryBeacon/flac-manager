#!/usr/bin/python -tt
# -*- coding: utf8 -*-

"""
Encodes WAV files into the FLAC format with the maximum compression level.

Author: Eduardo Ferreira
License: MIT (see LICENSE for details)
"""

# Module import
# -------------------------------------------------------------------------------------------------
from audio import EXTENSIONS, encode_wav_flac
from interface import parse_options

# Constants
# -------------------------------------------------------------------------------------------------
PROGRAM = "wav2flac"
DESCRIPTION = "Encodes WAV files into the FLAC format with the maximum compression level"

# Methods :: Execution and boilerplate
# -------------------------------------------------------------------------------------------------
if __name__ == '__main__':
	try:
		(files, destination, cover, tags, playlist) = parse_options(PROGRAM, DESCRIPTION, EXTENSIONS["wav"])
		for item in files:
			encode_wav_flac(item, destination, cover, (tags[item] if tags else tags))

		if playlist:
			from audio import create_playlist
			create_playlist(destination, "artist", "album")

	except KeyboardInterrupt:
		from interface import ERROR_INTERRUPTED
		print "\n" + ERROR_INTERRUPTED + "\n"

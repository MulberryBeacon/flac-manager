#!/usr/bin/python -tt
# -*- coding: utf8 -*-

"""
Audio library with conversion methods.

Author: Eduardo Ferreira
License: MIT (see LICENSE for details)
"""

# Module import
# ----------------------------------------------------------------------------------------------------------------------
from general import is_string_empty
from os.path import basename, join, splitext
from subprocess import call, PIPE, Popen


# Constants :: Lists and file extensions
# ----------------------------------------------------------------------------------------------------------------------
PLAYLIST = "00. {0} - {1}.m3u"
TAGS_FILE = "tags.txt"

"""
TITLE       : Track/Work name
ARTIST      : The artist generally considered responsible for the work. In popular music this is usually the performing
			  band or singer. For classical music it would be the composer. For an audio book it would be the author of
			  the original text
ALBUM       : The collection name to which this track belongs
TRACKNUMBER : The track number of this piece if part of a specific larger collection or album
ALBUMARTIST : The artist(s) who performed the work. In classical music this would be the conductor, orchestra, soloists.
			  In an audio book it would be the actor who did the reading. In popular music this is typically the same as
			  the ARTIST and is omitted
GENRE       : A short text indication of music genre
DATE        : Date the track was recorded
DISCTOTAL   : Number of discs that compose the set ("DISCTOTAL" : ["--tv", "TPOS="],)
TRACKTOTAL  : Number of tracks in the album
"""
TAGS = {
	"TITLE"      : "--tt",
	"ARTIST"     : "--ta",
	"ALBUM"      : "--tl",
	"TRACKNUMBER": "--tn",
	"ALBUMARTIST": ["--tv", "TPE2="],
	"GENRE"      : "--tg",
	"DATE"       : "--ty",
	"TRACKTOTAL" : ""
}

EXTENSIONS = {
	"flac": ".flac",
	"mp3" : ".mp3",
	"wav" : ".wav"
}


# Methods :: File encoding and decoding
# ----------------------------------------------------------------------------------------------------------------------
def decode_flac_wav(filename, destination, cover=False, tags=False):
	"""
	Decodes a FLAC audio file, generating the corresponding WAV audio file.
	Also retrieves the list of its ID3 tags and album cover.
	"""
	# Invokes the 'flac' program with the following arguments:
	# -d => Decode (the default behavior is to encode)
	# -f => Force overwriting of output files
	# -o => Force the output file name
	new_filename = update_file(filename, destination, EXTENSIONS["wav"])
	call(["flac", "-df", filename, "-o", new_filename])

	# Checks if both cover and tags should be retrieved
	cover_filename = (get_cover(filename, destination) if cover else None)
	tags_value = get_tags(filename, destination) if tags else None

	return (new_filename, cover_filename, tags_value)


def encode_wav_flac(filename, destination, cover, tags):
	"""
	Encodes a WAV audio file, generating the corresponding FLAC audio file.
	"""
	# Prepares the 'flac' program arguments:
	# -f => Force overwriting of output files
	# -8 => Synonymous with -l 12 -b 4096 -m -e -r 6
	# -V => Verify a correct encoding
	# -o => Force the output file name
	new_filename = update_file(filename, destination, EXTENSIONS["flac"])
	flac = ["flac", "-f8V", "-o", new_filename]

	# Prepares the cover file to be passed as a parameter
	# --picture=SPECIFICATION => Import picture and store in PICTURE block
	if cover:
		flac.extend(["--picture=", "3||" + basename(cover) + "||" + cover])

	# Prepares the FLAC tags to be passed as parameters
	# --T FIELD=VALUE => Add a FLAC tag; may appear multiple times
	if tags:
		for tag in TAGS:
			flac.extend(["-T", tag + "=" + tags[tag]])

	# Invokes the 'flac' program
	call(flac.append(filename))

	return new_filename


def encode_wav_mp3(filename, destination, cover, tags):
	"""
	Encodes a WAV audio file, generating the corresponding MP3 audio file.
	"""
	# Prepares the 'lame' program arguments:
	# -b 320          => Set the bitrate to 320 kbps
	# -q 0            => Highest quality, very slow
	# --preset insane => Type of the quality settings
	# --id3v2-only    => Add only a version 2 tag
	new_filename = update_file(filename, destination, EXTENSIONS["mp3"])
	lame = ["lame", "-b", "320", "-q", "0", "--preset", "insane", "--id3v2-only"]

	# Prepares the cover file to be passed as a parameter
	# --ti <file> => Audio/song albumArt (jpeg/png/gif file, v2.3 tag)
	if cover:
		flac.extend(["--ti", cover])

	# Prepares the ID3 tags to be passed as parameters
	# --<tag> <value> => Audio/song specific information
	if tags:
		for flac_tag in TAGS:
			id3_tag = TAGS[flac_tag]
			if not id3_tag:
				continue

			value = tags[flac_tag]
			lame.extend([id3_tag, value] if not id3_tag is list else [id3_tag[0], id3_tag[1] + value])

	# Invokes the 'lame' program
	call(lame.extend([filename, new_filename]))

	return new_filename


def encode_flac_mp3(filename, destination, cover, tags):
	"""
	Decodes a FLAC audio file, generating the corresponding WAV audio file.
	The WAV audio file is then encoded, generating the corresponding MP3 audio file.
	"""
	new_filename = decode_flac_wav(filename, destination, cover, tags)
	encode_wav_mp3(new_filename, destination, cover, tags)


# Methods :: Album cover management
# ----------------------------------------------------------------------------------------------------------------------
def get_cover(filename, destination):
	"""
	Retrieves the front cover art file from a FLAC audio file and stores it in the destination directory.
	"""
	# Prepares the 'metaflac' program arguments:
	# --list       => Lists the full stack of metadata
	# --block-type => Comma-separated list of block types to be included
	metaflac = ["metaflac", "--list", "--block-type=PICTURE", filename]

	# Prepares the 'grep' program arguments (looks for description parameter)
	grep = ["grep", "description:"]

	# Prepares the 'sed' program arguments (the regular expression removes the parameter name)
	sed = ["sed", "s/.*: //"]

	# Invokes the 'metaflac', 'grep' and 'sed' programs to retrieve the cover file name
	p1 = Popen(metaflac, stdout=PIPE)
	p2 = Popen(grep, stdin=p1.stdout, stdout=PIPE)
	p3 = Popen(sed, stdin=p2.stdout, stdout=PIPE)
	cover = p3.communicate()[0].rstrip("\n")

	# Checks if the audio file has a cover
	if is_string_empty(cover):
		return None

	# Prepares the 'metaflac' program arguments:
	# --export-picture-to => Export PICTURE block to a file
	cover = join(destination, cover)
	call(["metaflac", "--export-picture-to=" + cover, filename])

	return cover


# Methods :: Tag management
# ----------------------------------------------------------------------------------------------------------------------
def read_tag_file(filename):
	"""
	Reads the contents of a tag text file.
	"""
	stream = open(filename, 'r')
	result = {}
	for line in stream:
		list_tags = line.rstrip('\n').split('|')
		map_tags = {}
		for tag in list_tags[1:]:
			(flac, value) = tag.split('=')
			map_tags[flac] = value

		result[list_tags[0]] = map_tags

	stream.close()
	return result


def get_tags(filename, destination):
	"""
	Retrieves and stores the tag values of a FLAC audio file.
	"""
	map_tags = {}
	list_tags = [filename]
	for tag in TAGS:

		# Invokes the 'metaflac' program with the following arguments:
		# --show-tag => Shows the value of the given tag
		p = Popen(["metaflac", "--show-tag=" + tag, filename], stdout=PIPE)
		value = p.communicate()[0].rstrip("\n")
		list_tags.append(value)
		map_tags[tag] = value.split("=")[1]

	# Writes the list of tags to the file
	stream = open(join(destination, TAGS_FILE), 'a')
	stream.write('|'.join(list_tags) + '\n')
	stream.close()

	return maps_tags


# Methods :: File management
# ----------------------------------------------------------------------------------------------------------------------
def update_file(filename, directory, extension):
	"""
	Updates the path and extension of the given file.
	"""
	# Measure performance for possible solutions
	#return splitext(join(directory, basename(filename)))[0] + extension
	#return join(directory, basename(splitext(filename)[0] + extension))
	return join(directory, splitext(basename(filename))[0] + extension)


def cleanup(filename):
	"""
	Removes the temporary WAV audio file created during the conversion process.
	"""
	# Prepares the 'rm' program arguments:
	# -r => Remove directories and their contents recursively
	# -f => Ignore nonexistent files, never prompt
	rm = ["rm", "-rf"]

	# Replaces the extension of the input file (from FLAC to WAV)
	rm.append(splitext(filename)[0] + EXTENSIONS["wav"])

	# Invokes the 'rm' program to remove the temporary WAV audio file
	call(rm)


def create_playlist(folder, artist, album):
	"""
	Creates a playlist file (.m3u extension) for the given album.
	"""
	# Prepares the 'ls' program arguments
	ls = ["ls", folder]

	# Creates a new file with the specified name and writes the list of files
	with open(join(folder, PLAYLIST.format(artist, album)), 'w') as output:
		p = Popen(ls, stdout=output)

	output.close()

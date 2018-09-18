# -*- coding: utf8 -*-
"""
Audio encoding operations.

Author: Eduardo Ferreira
License: MIT (see LICENSE for details)
"""
from subprocess import call#, CalledProcessError, check_output, PIPE, Popen
import logging

from anarky.enums.program import Program
from anarky.enums.audio_file import AudioFile

# Logger
# --------------------------------------------------------------------------------------------------
logging.basicConfig(level=logging.INFO)
_logger = logging.getLogger(__name__)

# Methods
# --------------------------------------------------------------------------------------------------
def encode_wav_flac(filename, destination, cover=None, tags=None):
    """
    Encodes a WAV audio file, generating the corresponding FLAC audio file.

    :param filename:
        The input audio file name
    :param destination:
        The destination where the output file will be stored
    :param cover:
        The name of the file with the album art
    :param tags:
        The name of the file with the ID3 tags
    :return:
        The name of the output audio file
    """
    is_program_available(Program.FLAC.value)

    if not is_wav_file(filename):
        return None

    # Prepares the 'flac' program arguments:
    # -f => Force overwriting of output files
    # -8 => Synonymous with -l 12 -b 4096 -m -e -r 6
    # -V => Verify a correct encoding
    # -o => Force the output file name
    output_filename = update_path(filename, destination, AudioFile.FLAC.value)
    flac = [Programs.flac.value, '-f8V', '-o', output_filename]

    # Prepares the cover file to be passed as a parameter
    # --picture=SPECIFICATION => Import picture and store in PICTURE block
    if cover:
        flac.extend(['--picture=3||' + basename(cover) + '||' + cover])

    # Prepares the FLAC tags to be passed as parameters
    # --T FIELD=VALUE => Add a FLAC tag; may appear multiple times
    if tags:
        for tag, value in tags.items():
            flac.extend(['-T', tag + '=' + value])

    # Invokes the 'flac' program
    flac.append(filename)
    call(flac)

    return output_filename


def encode_wav_mp3(filename, destination, cover=None, tags=None):
    """
    Encodes a WAV audio file, generating the corresponding MP3 audio file.
    :param filename: The input audio file name
    :param destination: The destination where the output file will be stored
    :param cover: The name of the file with the album art
    :param tags: The name of the file with the ID3 tags
    :return: The name of the output audio file
    """
    is_program_available(Program.LAME.value)

    if not is_wav_file(filename):
        return None

    # Prepares the 'lame' program arguments:
    # -b 320          => Set the bitrate to 320 kbps
    # -q 0            => Highest quality, very slow
    # --preset insane => Type of the quality settings
    # --id3v2-only    => Add only a version 2 tag
    output_filename = update_path(filename, destination, AudioFile.MP3.value)
    lame = [Program.LAME.value, '-b', '320', '-q', '0', '--preset', 'insane', '--id3v2-only']

    # Prepares the cover file to be passed as a parameter
    # --ti <file> => Audio/song albumArt (jpeg/png/gif file, v2.3 tag)
    if cover:
        lame.extend(['--ti', cover])

    # Prepares the ID3 tags to be passed as parameters
    # --<tag> <value> => Audio/song specific information
    if tags:
        for tag, value in tags.items():
            id3_tag = TAGS[tag]
            if not id3_tag:
                continue

            if tag == 'TRACKNUMBER':
                value += '/' + tags['TRACKTOTAL']

            lame.extend([id3_tag, value]
                if type(id3_tag) is not list
                else [id3_tag[0], id3_tag[1] + value])

    # Invokes the 'lame' program
    lame.extend([filename, output_filename])
    call(lame)

    return output_filename


def encode_flac_mp3(filename, destination, extract_cover=False, extract_tags=False):
    """
    Decodes a FLAC audio file, generating the corresponding WAV audio file.
    The WAV audio file is then encoded, generating the corresponding MP3 audio file.
    :param filename: The input audio file name
    :param destination: The destination where the output file will be stored
    :param extract_cover: Indicates if the album art should be extracted from the audio file
    :param extract_tags: Indicates if the ID3 tags should be extracted from the audio file
    :return: The name of the output audio file
    """
    wav_file = decode_flac_wav(filename, destination, extract_cover, extract_tags)
    if wav_file:
        cover = wav_file[1] if get_cover else None
        tags = wav_file[2] if get_tags else None
        return encode_wav_mp3(wav_file[0], destination, cover, tags)

    return None
# anarky

Encodes and decodes between several types of audio files.

## Programs

* `wav2flac` (lossless => lossless)  
Encodes WAV files into the FLAC format with the maximum compression level.
* `wav2mp3` (lossless => lossy)  
Encodes WAV files into the MP3 format with the maximum compression level.
* `flac2wav` (lossless => lossless)  
Decodes FLAC files into the WAV format.
* `flac2mp3` (lossless => lossy)  
Encodes FLAC files into the MP3 format with the maximum compression level.

## Instructions

The `wav2flac` and `wav2mp3` programs perform an encoding operation and have
the same set of options:

    usage: PROGRAM [-h] [-v] [-p] [-t] [-c IMG] -f FILES [FILES ...] -d DEST

    optional arguments:
      -h, --help            show this help message and exit
      -v, --version         show program's version number and exit
      -p, --playlist        create playlist file
      -t, --tags            add ID3 tags
      -c IMG, --cover IMG   add album art

    options:
      -f FILES [FILES ...], --files FILES [FILES ...]
                            input files to convert
      -d DEST, --dest DEST  output directory for the generated files

The `flac2wav` and `flac2mp3` programs perform a decoding operation (the latter
starts with decoding and then encodes, of course) and have the same set of
options, which is slightly different from the previous two programs due to not
having to provide an album art file:

    usage: PROGRAM [-h] [-v] [-p] [-t] [-c] -f FILES [FILES ...] -d DEST

    optional arguments:
      -h, --help            show this help message and exit
      -v, --version         show program's version number and exit
      -p, --playlist        create playlist file
      -t, --tags            extract ID3 tags
      -c, --cover           extract album art

    options:
      -f FILES [FILES ...], --files FILES [FILES ...]
                            input files to convert
      -d DEST, --dest DEST  output directory for the generated files

The current syntax for the programs requires that the location of both input
and output files be defined explicitly.

## Examples

A specific WAV file is selected and the resulting FLAC file will be stored in
the given folder.

    wav2flac -f lovely_song.wav -d ~/new_songs/

A specific FLAC file is selected and the resulting WAV file will be stored in
the given folder, along with the extracted cover art and ID3 tags file.

    flac2wav -f lovely_song.flac -d ~/new_songs/ -c -t

## Versions

See [CHANGELOG](CHANGELOG.md) for details.

## Dependencies

All development and testing activities are carried out on Ubuntu 18.10 using
Python 3.6.7. The following packages are required:

* `lame`
* `flac`
* `metaflac`

## Code metrics

`CLOC`

    http://cloc.sourceforge.net v 1.60  T=0.01 s (892.6 files/s, 95000.5 lines/s)
    -------------------------------------------------------------------------------
    File                             blank        comment           code
    -------------------------------------------------------------------------------
    audio.py                            64            173            117
    interface.py                        28             51             59
    wav2flac.py                         13             15             23
    wav2mp3.py                          13             15             23
    flac2wav.py                         10             13             19
    flac2mp3.py                         10             13             18
    general.py                          15             41             12
    -------------------------------------------------------------------------------
    SUM:                               153            321            271
    -------------------------------------------------------------------------------

    -------------------------------------------------------------------------------
    Language                     files          blank        comment           code
    -------------------------------------------------------------------------------
    Python                           7            153            321            271
    -------------------------------------------------------------------------------
    SUM:                             7            153            321            271
    -------------------------------------------------------------------------------

## License

Copyright © 2012-2019 Eduardo Ferreira

The code in this repository is MIT licensed, and therefore free to use as you
please for commercial or non-commercial purposes (see [LICENSE](LICENSE) for
details).

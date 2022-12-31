# HelixStudios

`helixstudios` is a command-line tool to create an offline cache of HelixStudios videos. 
It enables paying members to create a JellyFin/Kodi compatible movie library, complete with cover-art, models details, genres and thumbnails.


**NOTE:** This repo is still a work in progress. Currently, only movie downloads are functioning.


# Installation

Clone this repository, `cd` into the repository, and run:

```bash
pip install .
```


# Running

Make your own copy of the `settings.yaml` file. Enter your username & password, and update the other relevant settings as required. 

Begin the download by running:

```bash
helixstudios /path/to/settings.yaml
```

Watch the progress by `tail`ing the log file. This example is for MacOS, check the `settings.yaml` file if you're on Linux.

```bash
tail -f ~/Library/Log/helixstudios.log
```


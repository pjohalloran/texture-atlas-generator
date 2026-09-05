# Texture Atlas & Image Font Generator #

Texture Atlas Generator is a pipeline tool for generating texture atlases, atlas data files and image fonts for use in apps and games.  It was written for my own personal game engine but can be used in any game engine that can read xml or json.

It is written in python and uses the python image library to generate the texture atlases.  It can be installed and used on any platform that supports python and the python imaging library.  It is known to work on Windows and OSX.


##  Dependencies ##
* python 3
* Pillow (https://python-pillow.org/)

Optional:
* pipx (recommended way to install the tool itself, see below)
* venv (part of the python 3 standard library, only needed for development)


## Installation ##

The recommended way to install the tool is with [pipx](https://pipx.pypa.io/),
which installs it into its own isolated environment (so Pillow and friends
never clash with anything else on your system) while still putting the
`texture-atlas-generator` and `texture-image-font-generator` commands directly
on your normal `PATH` - no venv to remember to activate.

* Install pipx, if you don't already have it
  * OSX (Homebrew): `brew install pipx`
  * Other platforms: `python3 -m pip install --user pipx` then `pipx ensurepath`

* Clone the project and install it
```
git clone https://github.com/pjohalloran/texture-atlas-generator
cd texture-atlas-generator
pipx install .
```

* Run the tool from anywhere
```
texture-atlas-generator --help
texture-image-font-generator --help
```

### Updating ###

`pipx upgrade texture-atlas-generator` alone won't notice new commits, since a
local path install has no version number for pipx to compare against. Instead:

```
git pull
pipx install . --force
```

### Uninstalling ###

`pipx uninstall texture-atlas-generator` removes both commands (they're
installed together as a single pipx app).

### Alternative: plain pip install ###

If you'd rather not use pipx, `pip install -e .` (ideally inside a venv you
create yourself) works too and gives you an editable install that picks up
source changes immediately - see "Development" below.


## Directory Structure ##

`AtlasGenerator.py` expects your source images under `<res-path>/<images-dir>`
(`-i/--images-dir` defaults to `textures`). Within that directory, both of these are
supported and can be mixed:

* Images placed inside a named subdirectory are packed into their own atlas, named
  after that subdirectory.
* Images placed directly in `<images-dir>` itself (no subdirectory) are packed into
  one additional atlas, named after `<images-dir>`.

```
<res-path>/
  textures/            <- matches -i/--images-dir (default: textures)
    player.png         <- loose images here are packed into one atlas named "textures"
    sprites/           <- becomes its own atlas named "sprites"
      enemy.png
    ui/                <- becomes its own atlas named "ui"
      button.png
  atlases/             <- output (auto-created and cleared on each run)
    textures.png / textures.xml
    sprites.png / sprites.xml
    ui.png / ui.xml
```

Note: if a subdirectory happens to share `<images-dir>`'s own name (e.g. a
`textures/textures/` subdirectory when using the default `-i textures`), its atlas
output will collide with the loose-images atlas's filename. Avoid naming a
subdirectory the same as your images-dir.


## Development ##

If you're editing the source rather than just using the tool, a venv-based
editable install is more convenient than pipx (source changes take effect
immediately, no reinstalling needed):

* Create the venv and install all the tool's dependencies
`cd texture-atlas-generator`
`./create_virtualenv.sh`
`. env/bin/activate`

* Run the tool straight from source
`cd src`
`python AtlasGenerator.py --help`

### Running Tests ###

* Install the test dependencies (from the repo root, with the venv activated)
`pip install -r requirements-dev.txt` (or `pip install -e ".[dev]"`)

* Run the test suite
`pytest`


## Contributer List ##
* PJ O Halloran


## Help ##
Contact me on twitter @pjohalloran if you need some help or would like to contribute.


## Contribution Guidelines ##
If you have something to contribute, fork the project, make your change and open a pull request when done.
The only guidelines I have is that you ensure the code is PEP-8 compliant.


## Credits  ##

The atlas packing algorithms include the maxrects algorithm (http://clb.demon.fi/files/RectangleBinPack.pdf) and John Ratcliffs packing algorithm (https://code.google.com/p/texture-atlas/).
The maxrects algorithm implemted here is a python implementation of maxrects from https://github.com/juj/RectangleBinPack.

If you would like a project with more features then I would recommend you check out the excellent TexturePacker (http://www.codeandweb.com/texturepacker) by Andreas Low.

## Software License ##

'texture-atlas-generator' is available to all under the MIT license.
Copyright © 2011-2013 PJ O Halloran

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


### Python Imaging Library License ###
    Copyright © 1997-2011 by Secret Labs AB
    Copyright © 1995-2011 by Fredrik Lundh

By obtaining, using, and/or copying this software and/or its associated documentation, you agree that you have read, understood, and will comply with the following terms and conditions:

Permission to use, copy, modify, and distribute this software and its associated documentation for any purpose and without fee is hereby granted, provided that the above copyright notice appears in all copies, and that both that copyright notice and this permission notice appear in supporting documentation, and that the name of Secret Labs AB or the author not be used in advertising or publicity pertaining to distribution of the software without specific, written prior permission.

SECRET LABS AB AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS SOFTWARE, INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL SECRET LABS AB OR THE AUTHOR BE LIABLE FOR ANY SPECIAL, INDIRECT OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

# font-patcher

A tool for patching any TrueType font or TrueType Collection

## Setup

### 1. Install [Font Tools](https://github.com/fonttools/fonttools)

```bash
$ brew install fonttools
```

This will install a bundle of CLI tools used for manipulating fonts. One of them that
will be used is **ttx**.

### 2. Install [Font Forge](https://github.com/fontforge/fontforge)

```bash
$ brew install fontforge
```

This is another CLI tool that helps with editing TrueType Fonts/Collections.

### 3. Download the font patcher script

```bash
$ curl https://raw.githubusercontent.com/waydegg/font-patcher/master/font-patcher -o font-patcher && chmod +x font-patcher
```

## Usage

```bash
$ ./font-patcher [path_to_font]
```

Examples:

```bash
$ ./font-patcher /System/Library/Fonts/Menlo.ttc

$ ./font-patcher --skip-downloads /System/Library/Fonts/Geneva.ttf
```

For more details:

```bash
$ ./font-patcher --help

usage: font-patcher [-h] [--skip-downloads] unpatched_font_fp

Patch a .ttc or .ttf font file

positional arguments:
  unpatched_font_fp  path to a .ttc or .ttf file

options:
  -h, --help         show this help message and exit
  --skip-downloads   skip downloading the helper script and any glyphs
```

## Extra details

This script has been tested on OSX Monterey, probably works on Linux, and might have
issues working on Windows. Please submit an issue if you are having problems running
this script.

Some system TrueType fonts are un-patchable, however the Nerd Font script that this tool
leverages won't raise any exceptions. From manually tests, it seems that a lot of these
un-patchable fonts are non-english.

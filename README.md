# photo-pre-process
### (`pthree` or $p^3$)

#### Utility scripts to assist in renaming and generating metadata files for digital photos.

I created this utility to suit my own personal digital photography workflow. It probably won't work for you. Feel free to fork and modify to suit your needs.

## Requirements

This script requires Python 3.9.

This script depends on [`exiftool`](https://exiftool.org/), [`typer`](https://typer.tiangolo.com/), and [`rich`](https://github.com/Textualize/rich).

`exiftool` must be installed manually prior to using this script. Please follow the instructions [here](https://exiftool.org/install.html).

## Installation

This utility can only be installed from source.

1. Clone this repository.
2. Navigate to the cloned repository.
```
cd [cloned repository directory]
```
3. Use pip to install the package locally.
```
pip install .
```

## Usage

Invoke by running `pthree`.

- `pthree rename` to batch rename photos using EXIF date and time data.
- `pthree texif` to automatically generate human readable text EXIF data in different formats according to presets.
- `pthree exif` to automatically generate binary EXIF sidecar files.
- `pthree process` as a shortcut to do all three above actions at the same time.

For more information, run `pthree --help`.

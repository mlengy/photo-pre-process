import typer

from util import Util
from exiftool import ExifTool


class Exif:
    def __init__(self, directory: str, output_directory: str, level: int, extension: str):
        self.directory = directory
        self.output_directory = output_directory
        self.level = level
        self.extension = extension

    def exif(self):
        Util.verify_directory(self.directory)

        with ExifTool() as exiftool:
            Util.verify_extension_exists(exiftool, self.extension)

            Util.create_directory_or_abort(self.output_directory)

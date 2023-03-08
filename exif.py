import typer

from util import Util


class Exif:
    def __init__(self, directory: str, level: int, extension: str):
        self.directory = directory
        self.level = level
        self.extension = extension

    def exif(self):
        Util.verify_directory(self.directory)

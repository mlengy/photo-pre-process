import typer

from util import Util


class Exif:
    def __init__(self, directory, level):
        self.directory = directory
        self.level = level

    def exif(self):
        Util.verify_directory(self.directory)

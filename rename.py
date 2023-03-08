import typer

from util import Util


class Rename:
    def __init__(self, directory: str, in_place: bool, skip_invalid: bool, extension: str):
        self.directory = directory
        self.in_place = in_place
        self.skip_invalid = skip_invalid
        self.extension = extension

    def rename(self):
        Util.verify_directory(self.directory)



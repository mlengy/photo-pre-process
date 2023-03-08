import typer

from util import Util


class Rename:
    def __init__(self, directory, in_place, skip_invalid):
        self.directory = directory
        self.in_place = in_place
        self.skip_invalid = skip_invalid

    def rename(self):
        Util.verify_directory(self.directory)

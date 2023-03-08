import typer

from util import Util


class Texif:
    def __init__(self, directory, level):
        self.directory = directory
        self.level = level

    def texif(self):
        Util.verify_directory(self.directory)

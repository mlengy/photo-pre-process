import typer

from util import Util


class Texif:
    def __init__(self, directory, type, level):
        self.directory = directory
        self.type = type
        self.level = level

    def texif(self):
        Util.verify_directory(self.directory)

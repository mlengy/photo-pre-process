import typer

from util import Util


class Texif:
    def __init__(self, directory, type, level, extension):
        self.directory = directory
        self.type = type
        self.level = level
        self.extension = extension

    def texif(self):
        Util.verify_directory(self.directory)

        for level, processor in Texif.level_map.items():
            if self.level >= level:
                processor(self)

    def __process_one(self):
        pass

    def __process_two(self):
        pass

    def __process_three(self):
        pass

    level_map = {
        1: __process_one,
        2: __process_two,
        3: __process_three
    }

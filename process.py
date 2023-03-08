import typer

from util import Util


class Process:
    def __init__(self, directory, output_directory, level):
        self.directory = directory
        self.output_directory = output_directory
        self.level = level

    def process(self):
        Util.verify_directory(self.directory)

        for level, processor in Process.level_map.items():
            if self.level >= level:
                # noinspection PyArgumentList
                processor(self)

    def __process_one(self):
        Util.verify_or_create_directory(self.output_directory)

    def __process_two(self):
        pass

    def __process_three(self):
        pass

    level_map = {
        1: __process_one,
        2: __process_two,
        3: __process_three
    }

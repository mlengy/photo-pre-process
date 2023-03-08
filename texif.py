import typer

from util import Util
from exiftool import ExifTool


class Texif:
    def __init__(self, directory: str, output_directory: str, type: str, level: int, extension: str):
        self.directory = directory
        self.output_directory = output_directory
        self.type = type
        self.level = level
        self.extension = extension

    def texif(self):
        Util.verify_directory(self.directory)

        with ExifTool() as exiftool:
            Util.verify_extension_exists(exiftool, self.extension)

            Util.create_directory_or_abort(self.output_directory)

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

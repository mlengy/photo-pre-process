import typer

from util import Util
from exiftool import ExifTool


class Process:
    meta_destination_name = "meta"

    def __init__(self, directory, output_directory, extension):
        self.directory = directory
        self.output_directory = output_directory
        self.extension = extension

    def process(self):
        Util.verify_directory(self.directory)
        Util.create_directory_or_abort(self.output_directory)

        image_destination = f"{self.output_directory}/{self.extension.lower()}"
        meta_destination = f"{image_destination}/{Process.meta_destination_name}"
        Util.create_directory_or_abort(image_destination)
        Util.create_directory_or_abort(f"{meta_destination}/simple")
        Util.create_directory_or_abort(f"{meta_destination}/full")
        Util.create_directory_or_abort(f"{meta_destination}/mie")

        with ExifTool() as et:
            pass

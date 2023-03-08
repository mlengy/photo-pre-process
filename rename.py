import shutil
import json
import typer

from util import Util
from constants import Tags
from exiftool import ExifTool


class Rename:
    def __init__(self, initials: str, directory: str, output_directory: str, keep_original: bool, extension: str):
        self.initials = initials
        self.directory = directory
        self.output_directory = output_directory
        self.keep_original = keep_original
        self.extension = extension

    def rename(self):
        Util.verify_directory(self.directory)

        with ExifTool() as exiftool:
            Util.verify_extension_exists(exiftool, self.extension)

            Util.create_directory_or_abort(self.output_directory)

            if self.keep_original:
                self.do_rename(exiftool, Rename.do_rename_copy)
            else:
                self.do_rename(exiftool, Rename.do_rename_move)

    def do_rename(self, exiftool: ExifTool, file_modification_closure):
        formatted_date_times = self.__get_formatted_date_time(exiftool)

        previous_filename = ""
        sequence_number = 0

        for image_metadata in formatted_date_times:
            original_filename = image_metadata[Tags.FileName]
            formatted_date_time = image_metadata[Tags.DateTimeOriginal]

            new_filename = f"{self.initials.upper()}-{formatted_date_time}-"

            if new_filename == previous_filename:
                sequence_number += 1
            else:
                previous_filename = new_filename
                sequence_number = 0

            full_filename = new_filename + f"{sequence_number:02d}-{original_filename}"

            full_path = f"{self.output_directory}/{full_filename}"
            file_modification_closure(original_filename, full_path)

        print("Done!")

    @staticmethod
    def do_rename_copy(from_path: str, to_path: str):
        print(f"Copying [{from_path}] to [{to_path}]...")
        shutil.copy2(from_path, to_path)

    @staticmethod
    def do_rename_move(from_path: str, to_path: str):
        print(f"Moving [{from_path}] to [{to_path}]...")
        shutil.move(from_path, to_path)

    def __get_formatted_date_time(self, exiftool: ExifTool):
        return json.loads(
            exiftool.execute_with_extension(
                self.extension,
                "-J",
                f"-{Tags.FileName}",
                f"-{Tags.DateTimeOriginal}",
                "-d",
                "%Y%m%d-%H%M%S%z",
                "."
            )
        )

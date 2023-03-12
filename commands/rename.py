import json
import shutil

from rich.progress import Progress

from util.config import Config
from util.constants import Tags
from util.exiftool import ExifTool
from util.helpers import Util, Printer


class Rename:
    def __init__(
            self,
            initials: str,
            directory: str,
            output_directory: str,
            keep_original: bool,
            extension: str
    ):
        self.initials = initials
        self.directory = Util.strip_slashes(directory)
        self.output_directory = Util.strip_slashes(output_directory)
        self.keep_original = keep_original
        self.extension = extension
        self.step_count = 1
        self.total_steps = 1

    def rename(self):
        Rename.start_message()

        Rename.verify_initials(self.initials)
        Rename.verify_possible_directory(self.initials)
        Util.verify_directory(self.directory)

        with ExifTool() as exiftool:
            num_images = len(Util.verify_extensions_in_directory(exiftool, self.extension, self.directory))

            Util.create_directory_or_abort(self.output_directory)

            if self.keep_original:
                self.do_rename(exiftool, Rename.do_rename_copy, num_images)
            else:
                self.do_rename(exiftool, Rename.do_rename_move, num_images)

        Printer.done_all()

    def do_rename(self, exiftool: ExifTool, file_modification_closure, num_images: int):
        new_file_names = []

        with Printer.progress_spinner() as progress:
            progress.add_task(f"Getting date and time metadata for files...\n")
            formatted_date_times = self.__get_formatted_date_time(exiftool)

        previous_filename = ""
        sequence_number = 0

        with Progress(console=Printer.console) as progress:
            progress_task = progress.add_task(
                Printer.progress_label(
                    "Rename",
                    self.step_count,
                    self.total_steps
                ),
                total=num_images
            )

            for count, image_metadata in enumerate(formatted_date_times):
                original_filename = image_metadata[Tags.FileName]
                formatted_date_time = image_metadata[Tags.DateTimeOriginal]

                new_filename = f"{self.initials.upper()}-{formatted_date_time}-"

                if new_filename == previous_filename:
                    sequence_number += 1
                else:
                    previous_filename = new_filename
                    sequence_number = 0

                full_filename = new_filename + f"{sequence_number:02d}-{original_filename}"

                new_file_names.append(full_filename)

                full_path_from = f"{self.directory}/{original_filename}"
                full_path_to = f"{self.output_directory}/{full_filename}"
                file_modification_closure(full_path_from, full_path_to)

                progress.update(progress_task, completed=count + 1)

        Printer.done()

        Util.set_valid_file_names(new_file_names)

    @staticmethod
    def do_rename_copy(from_path: str, to_path: str):
        Printer.waiting(f"Copying \[{from_path}] to \[{to_path}]...")
        shutil.copy2(from_path, to_path)

    @staticmethod
    def do_rename_move(from_path: str, to_path: str):
        Printer.waiting(f"Moving \[{from_path}] to \[{to_path}]...")
        shutil.move(from_path, to_path)

    def __get_formatted_date_time(self, exiftool: ExifTool):
        return json.loads(
            exiftool.execute_with_extension(
                self.extension,
                f"-{Tags.JSONFormat}",
                f"-{Tags.FileName}",
                f"-{Tags.DateTimeOriginal}",
                "-d",
                Config.rename_date_format,
                self.directory
            )
        )

    @staticmethod
    def verify_initials(initials: str):
        if not (initials.isalnum() and 1 < len(initials) <= 10):
            Printer.error_and_abort(f"Initials \[{initials}] is not valid!")

    @staticmethod
    def verify_possible_directory(directory: str):
        if Util.is_directory_valid(directory):
            Printer.warning(f"It looks like your initials \[{directory}] is a directory.")
            Printer.prompt_continue(f"Is this correct?")

    @staticmethod
    def start_message():
        Printer.divider()
        Printer.console.print("[bright_magenta]🖋️  Starting rename! 🖋️")
        Printer.divider()

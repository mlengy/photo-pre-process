import os.path
import shutil

from rich.progress import Progress

from entities.filename import FileName
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
            num_files = len(Util.verify_extensions_in_directory(exiftool, self.extension, self.directory))

            Util.create_directory_or_abort(self.output_directory)

            if self.keep_original:
                self.do_rename(exiftool, Rename.do_rename_copy, num_files)
            else:
                self.do_rename(exiftool, Rename.do_rename_move, num_files)

        Printer.done_all()

    def do_rename(self, exiftool: ExifTool, file_modification_closure, num_files: int):
        new_file_names = []

        file_names = Util.get_valid_file_names(exiftool, self.extension, self.directory)

        with Progress(console=Printer.console) as progress:
            progress_task = progress.add_task(
                Printer.progress_label(
                    "Rename",
                    self.step_count,
                    self.total_steps
                ),
                total=num_files
            )

            previous_datetime = ""
            sequence_number = 0
            num_files_skipped = 0

            for count, file_name in enumerate(file_names):
                file_path = os.path.join(self.directory, file_name)

                Printer.waiting(f"Generating formatted datetime for \[{file_path}]...")

                file_tags = Util.deserialize_data(
                    exiftool.execute_with_extension(
                        self.extension,
                        f"-{Tags.JSONFormat}",
                        f"-{Tags.DateTimeOriginal}",
                        "-d",
                        Config.rename_date_format,
                        file_path
                    )
                )

                if not file_tags:
                    Printer.warning(f"Skipping \[{file_path}] due to error!")
                    num_files_skipped += 1
                    continue

                formatted_date_time = file_tags[0][Tags.DateTimeOriginal]

                if formatted_date_time == previous_datetime:
                    sequence_number += 1
                else:
                    previous_datetime = formatted_date_time
                    sequence_number = 0

                full_filename = str(
                    FileName(
                        initials=self.initials,
                        datetime=formatted_date_time,
                        sequence=sequence_number,
                        original=file_name
                    )
                )

                new_file_names.append(full_filename)

                full_path_from = os.path.join(self.directory, file_name)
                full_path_to = os.path.join(self.output_directory, full_filename)
                file_modification_closure(full_path_from, full_path_to)

                progress.update(progress_task, completed=count + 1)

        Printer.print_files_skipped(num_files_skipped)

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
        Printer.console.print(f"{Printer.color_divider}🖋️  Starting rename! 🖋️")
        Printer.divider()

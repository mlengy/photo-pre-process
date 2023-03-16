import os

from rich.progress import Progress

from commands.rename import Rename
from util.exiftool import ExifTool
from util.helpers import Util, Printer


class Yank:
    def __init__(
            self,
            directory: str,
            output_directory: str,
            keep_original: bool,
            extension: str
    ):
        self.directory = Util.strip_slashes(directory)
        self.output_directory = Util.strip_slashes(output_directory)
        self.keep_original = keep_original
        self.extension = extension
        self.step_count = 1
        self.total_steps = 1

    def yank(self):
        Yank.start_message()

        Util.verify_directory(self.directory)

        with ExifTool() as exiftool:
            Util.verify_extensions_in_directory(exiftool, self.extension, self.directory)

            Util.create_directory_or_abort(self.output_directory, self.directory)

            if self.keep_original:
                self.__do_yank(exiftool, Rename.do_rename_copy)
            else:
                self.__do_yank(exiftool, Rename.do_rename_move)

        Printer.done_all()

    def __do_yank(self, exiftool: ExifTool, file_modification_closure):
        file_names = Util.get_valid_file_names(exiftool, self.extension, self.directory)
        num_files = len(file_names)

        Printer.console.print(f"\n{Printer.color_title}📥 Starting yank! 📥\n")

        with Progress(console=Printer.console, auto_refresh=False) as progress:
            progress_task = progress.add_task(
                Printer.progress_label_with_steps(
                    "Yank",
                    self.step_count,
                    self.total_steps
                ),
                total=num_files
            )

            for count, file_name in enumerate(file_names):
                file_path = os.path.join(self.directory, file_name)

                Printer.waiting(f"Yanking \[{file_path}]...")

                full_path_to = os.path.join(self.output_directory, file_name)
                file_modification_closure(file_path, full_path_to)

            progress.update(progress_task, completed=count + 1)

        num_files_in_directory = Util.num_files_in_directory(self.output_directory)
        Printer.print_files_skipped(num_files - num_files_in_directory)

        Printer.done()

    @staticmethod
    def start_message():
        Printer.divider()
        Printer.console.print(f"{Printer.color_divider}📥 Starting yank! 📥")
        Printer.divider()

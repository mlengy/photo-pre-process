import os

from rich.progress import Progress

from entities.filter import Filter
from util.exiftool import ExifTool
from util.helpers import Util, Printer


class Exif:
    def __init__(
            self,
            directory: str,
            output_directory: str,
            filter_files: bool,
            extension: str
    ):
        self.directory = Util.strip_slashes(directory)
        self.output_directory = Util.strip_slashes(output_directory)
        self.filter_files = filter_files
        self.extension = extension
        self.step_count = 1
        self.total_steps = 2

    def exif(self):
        Exif.start_message()

        Util.verify_directory(self.directory)

        with ExifTool() as exiftool:
            Util.verify_extensions_in_directory(exiftool, self.extension, self.directory)

            Util.create_directory_or_abort(self.output_directory, self.directory)

            file_names = Util.get_valid_file_names(exiftool, self.extension, self.directory)

            formatted_filter = Filter.build_filter(self.filter_files, self.total_steps)
            filtered_file_names = formatted_filter.filter(file_names)
            self.step_count += 1

            if not filtered_file_names:
                Printer.error_and_abort("There are no valid files to generate EXIFs for!")

            self.do_exif(exiftool, filtered_file_names)

        Printer.done_all()

    def do_exif(self, exiftool: ExifTool, file_names: list[str]):
        Printer.console.print("")
        num_files = len(file_names)

        with Progress(console=Printer.console, auto_refresh=False) as progress:
            progress_task = progress.add_task(
                Printer.progress_label_with_steps(
                    "EXIF sidecar",
                    self.step_count,
                    self.total_steps
                ),
                total=num_files
            )

            for count, file_name in enumerate(file_names):
                progress.update(progress_task, completed=count)
                progress.refresh()

                file_name_extensionless = os.path.splitext(file_name)[0]
                full_path_from = os.path.join(self.directory, file_name)
                full_path_to = f"{os.path.join(self.output_directory, file_name_extensionless)}.mie"

                Printer.waiting(f"Writing MIE binary dump to \[{full_path_to}]...")

                exiftool.execute_with_extension(
                    self.extension,
                    "-o",
                    full_path_to,
                    "-all:all",
                    "-icc_profile",
                    full_path_from
                )

            progress.update(progress_task, completed=num_files)

        num_files_in_directory = Util.num_files_in_directory(self.output_directory)
        Printer.print_files_skipped(num_files - num_files_in_directory)

        Printer.done()

    @staticmethod
    def start_message():
        Printer.divider()
        Printer.console.print(f"{Printer.color_divider}💽 Starting EXIF! 💽")
        Printer.divider()

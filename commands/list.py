import os.path

from entities.filter import Filter
from util.exiftool import ExifTool
from util.helpers import Util, Printer


class List:
    def __init__(
            self,
            directory: str,
            output_directory: str,
            full_path: bool,
            filter_files: bool,
            extension: str
    ):
        self.directory = Util.strip_slashes(directory)
        self.output_directory = None if not output_directory else Util.strip_slashes(output_directory)
        self.full_path = full_path
        self.filter_files = filter_files
        self.extension = extension
        self.step_count = 1
        self.total_steps = 1

    def ls(self):
        List.start_message()

        Util.verify_directory(self.directory)

        with ExifTool() as exiftool:
            Util.verify_extensions_in_directory(exiftool, self.extension, self.directory)

            if self.output_directory:
                Util.create_directory_or_abort(self.output_directory, self.directory)

            file_names = Util.get_valid_file_names(exiftool, self.extension, self.directory)

            formatted_filter = Filter.build_filter(self.filter_files, self.total_steps)
            filtered_file_names = formatted_filter.filter(file_names)
            self.step_count += 1

            if not filtered_file_names:
                Printer.error_and_abort("There are no valid files to list!")

        self.__do_list(filtered_file_names)

        Printer.done_all()

    def __do_list(self, file_names: list[str]):
        if self.output_directory:
            Printer.print("")

        Printer.console.print(f"{Printer.color_title}📖 Starting list! 📖\n")

        if not self.output_directory:
            for file_name in file_names:
                file_name = self.__get_file_name(file_name)

                Printer.print(file_name)
        else:
            full_path_to = os.path.join(self.output_directory, "output.txt")

            with open(full_path_to, "w") as output_file:
                for file_name in file_names:
                    file_name = self.__get_file_name(file_name)

                    Printer.waiting(f"Writing file \[{file_name}] to \[{full_path_to}]...")
                    Util.write_with_newline(output_file, file_name)

        Printer.print("")
        Printer.done()

    def __get_file_name(self, file_name):
        return os.path.join(self.directory, file_name) if self.full_path else file_name

    @staticmethod
    def start_message():
        Printer.divider()
        Printer.console.print(f"{Printer.color_divider}📖 Starting list! 📖")
        Printer.divider()

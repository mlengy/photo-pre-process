from entities.filename import FileName, FileNameTypeError
from entities.filter import Filter
from util.exiftool import ExifTool
from util.helpers import Util, Printer


class Info:
    def __init__(
            self,
            directory: str,
            filter_files: bool,
            extension: str
    ):
        self.directory = Util.strip_slashes(directory)
        self.filter_files = filter_files
        self.extension = extension
        self.step_count = 1
        self.total_steps = 1

    def info(self):
        Info.start_message()

        Util.verify_directory(self.directory)

        with ExifTool() as exiftool:
            Util.verify_extensions_in_directory(exiftool, self.extension, self.directory)

            file_names = Util.get_valid_file_names(exiftool, self.extension, self.directory)

            formatted_filter = Filter.build_filter(self.filter_files, self.total_steps)
            filtered_file_names = formatted_filter.filter(file_names)
            self.step_count += 1

            if not filtered_file_names:
                Printer.error_and_abort("There are no valid files to list information for!")

        self.__do_info(filtered_file_names)

        Printer.done_all()

    def __do_info(self, file_names: list[str]):
        num_files = len(file_names)

        Printer.console.print(f"{Printer.color_title}ℹ️  Starting info! ℹ️\n")

        num_processed = 0

        for file_name in file_names:
            Printer.waiting(f"Information for \[{file_name}]:")

            try:
                file_name_object = FileName.from_string(file_name)
                Info.__do_info_single_file(file_name_object)
                num_processed += 1
            except FileNameTypeError as error:
                Printer.warning(f"Skipping \[{file_name}] as it is malformed!", prefix=Printer.tab)
                Printer.warning(error.message, prefix=Printer.tab)

            Printer.print("")

        Printer.print_files_skipped(num_files - num_processed)

        Printer.done()

    @staticmethod
    def __do_info_single_file(file_name: FileName):
        pretty = file_name.to_pretty()
        Printer.print(f"Original filename: {pretty.original}", prefix=Printer.tab)
        Printer.print(f"Extension: {pretty.extension}", prefix=Printer.tab)
        Printer.print(f"Datetime: {pretty.date_time}", prefix=Printer.tab)
        Printer.print(f"Sequence number: {pretty.sequence}", prefix=Printer.tab)
        Printer.print(f"Media style: {pretty.style}", prefix=Printer.tab)
        Printer.print(f"Media rating: {pretty.rating}", prefix=Printer.tab)
        Printer.print(f"Initials: {pretty.initials}", prefix=Printer.tab)

    @staticmethod
    def start_message():
        Printer.divider()
        Printer.console.print(f"{Printer.color_divider}ℹ️  Starting info! ℹ️")
        Printer.divider()

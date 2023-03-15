from entities.filename import FileName, FileNameTypeError
from util.exiftool import ExifTool
from util.helpers import Util, Printer


class Info:
    def __init__(
            self,
            directory: str,
            extension: str
    ):
        self.directory = Util.strip_slashes(directory)
        self.extension = extension

    def info(self):
        Info.start_message()

        Util.verify_directory(self.directory)

        with ExifTool() as exiftool:
            Util.verify_extensions_in_directory(exiftool, self.extension, self.directory)

            self.__do_info(exiftool)

        Printer.done_all()

    def __do_info(self, exiftool: ExifTool):
        file_names = Util.get_valid_file_names(exiftool, self.extension, self.directory)

        Printer.console.print(f"{Printer.color_title}📥 Starting info! 📥\n")

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

        Printer.print_files_skipped(len(file_names) - num_processed)

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

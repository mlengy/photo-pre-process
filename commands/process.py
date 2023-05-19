import os.path

from commands.exif import Exif
from commands.rename import Rename
from commands.texif import Texif, Preset, TexifType, TexifLevel
from entities.filter import Filter
from util.exiftool import ExifTool
from util.helpers import Util, Printer


class Process:
    meta_destination_name = "meta"

    total_steps = 6

    def __init__(
            self,
            directory: str,
            output_directory: str,
            keep_original: bool,
            reprocess: bool,
            preset: Preset,
            filter_files: bool,
            extension: str
    ):
        self.directory = Util.strip_slashes(directory)
        self.output_directory = Util.strip_slashes(output_directory)
        self.keep_original = keep_original
        self.reprocess = reprocess
        self.preset = preset
        self.filter_files = filter_files
        self.extension = extension
        self.step_count = 1

    def process(self):
        Process.start_message()

        Util.verify_directory(self.directory)

        with ExifTool() as exiftool:
            Util.verify_extensions_in_directory(exiftool, self.extension, self.directory)

            if self.reprocess:
                media_destination = self.directory
                meta_destination = os.path.join(self.directory, Process.meta_destination_name)
            else:
                Util.create_directory_or_abort(self.output_directory, self.directory)

                media_destination = os.path.join(self.output_directory, self.extension.lower())
                meta_destination = os.path.join(media_destination, Process.meta_destination_name)

                Util.create_directory_or_abort(media_destination, self.directory)

            file_names = Util.get_valid_file_names(exiftool, self.extension, self.directory)

            formatted_filter = Filter.build_filter(self.filter_files, self.total_steps)
            filtered_file_names = formatted_filter.filter(file_names)
            self.step_count += 1

            if not filtered_file_names:
                Printer.error_and_abort("There are no valid files to process!")

            if not self.reprocess:
                self.__rename(exiftool, media_destination, filtered_file_names)

            self.__texif(exiftool, media_destination, meta_destination, filtered_file_names)
            self.__exif(exiftool, media_destination, meta_destination, filtered_file_names)

        Printer.done_all()

    def __rename(self, exiftool: ExifTool, media_destination: str, file_names: list[str]):
        Rename.start_message()

        rename = Rename(
            directory=self.directory,
            output_directory=media_destination,
            keep_original=self.keep_original,
            edit_types=[],
            filter_files=False,
            extension=self.extension
        )

        rename.step_count = self.step_count
        rename.total_steps = Process.total_steps

        if self.keep_original:
            rename.do_rename(exiftool, file_names, Rename.do_rename_copy)
        else:
            rename.do_rename(exiftool, file_names, Rename.do_rename_move)

        self.step_count += 2
        Printer.done(prefix="\n", suffix=" rename")

    def __texif(self, exiftool: ExifTool, media_destination: str, meta_destination: str, file_names: list[str]):
        Texif.start_message()

        meta_simple_destination = os.path.join(meta_destination, "simple")
        meta_full_destination = os.path.join(meta_destination, "full")

        Util.create_directory_or_abort(meta_simple_destination, self.directory)
        Util.create_directory_or_abort(meta_full_destination, self.directory)

        texif = Texif(
            directory=media_destination,
            output_directory=meta_destination,
            type=TexifType.full,
            level=TexifLevel.high,
            preset=self.preset,
            filter_files=False,
            extension=self.extension
        )

        texif.step_count = self.step_count
        texif.total_steps = Process.total_steps

        texif.do_texif_simple(exiftool, file_names, meta_simple_destination)

        self.step_count += 1
        texif.step_count = self.step_count
        texif.do_texif_full(exiftool, file_names, meta_full_destination)

        self.step_count += 1
        Printer.done(prefix="\n", suffix=" TEXIF")

    def __exif(self, exiftool: ExifTool, media_destination: str, meta_destination: str, file_names: list[str]):
        Exif.start_message()

        meta_mie_destination = os.path.join(meta_destination, "mie")

        Util.create_directory_or_abort(meta_mie_destination, self.directory)

        exif = Exif(
            directory=media_destination,
            output_directory=meta_mie_destination,
            filter_files=False,
            extension=self.extension
        )

        exif.step_count = self.step_count
        exif.total_steps = Process.total_steps

        exif.do_exif(exiftool, file_names)

        Printer.done(prefix="\n", suffix=" EXIF")

    @staticmethod
    def start_message():
        Printer.divider()
        Printer.console.print(f"{Printer.color_divider}🔄 Starting process! 🔄")
        Printer.divider()

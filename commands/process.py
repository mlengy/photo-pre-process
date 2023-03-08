from util.helpers import Util, Printer
from commands.rename import Rename
from commands.texif import Texif
from commands.exif import Exif
from util.exiftool import ExifTool


class Process:
    meta_destination_name = "meta"

    def __init__(self, initials: str, directory: str, output_directory: str, keep_original: bool, preset: str, extension: str):
        self.initials = initials
        self.directory = directory
        self.output_directory = output_directory
        self.keep_original = keep_original
        self.preset = preset
        self.extension = extension

    def process(self):
        Process.start_message()

        Util.verify_directory(self.directory)

        with ExifTool() as exiftool:
            Util.verify_extension_exists(exiftool, self.extension, self.directory)

            Util.create_directory_or_abort(self.output_directory)

            image_destination = f"{self.output_directory}/{self.extension.lower()}"
            meta_destination = f"{image_destination}/{Process.meta_destination_name}"

            Util.create_directory_or_abort(image_destination)

            self.__rename(exiftool, image_destination)
            self.__texif(exiftool, image_destination, meta_destination)
            self.__exif(exiftool, image_destination, meta_destination)

        Printer.done_all()

    def __rename(self, exiftool: ExifTool, image_destination: str):
        Rename.start_message()

        rename = Rename(
            initials=self.initials,
            directory=self.directory,
            output_directory=image_destination,
            keep_original=self.keep_original,
            extension=self.extension
        )

        if self.keep_original:
            rename.do_rename(exiftool, Rename.do_rename_copy)
        else:
            rename.do_rename(exiftool, Rename.do_rename_move)

        Printer.done(suffix=" rename")

    def __texif(self, exiftool: ExifTool, image_destination: str, meta_destination: str):
        Texif.start_message()

        meta_simple_destination = f"{meta_destination}/simple"
        meta_full_destination = f"{meta_destination}/full"

        Util.create_directory_or_abort(meta_simple_destination)
        Util.create_directory_or_abort(meta_full_destination)

        texif = Texif(
            directory=image_destination,
            output_directory=meta_destination,
            type="full",
            level=3,
            preset=self.preset,
            extension=self.extension
        )

        texif.do_texif_simple(exiftool, meta_simple_destination)
        texif.do_texif_full(exiftool, meta_full_destination)

        Printer.done(suffix=" TEXIF")

    def __exif(self, exiftool: ExifTool, image_destination: str, meta_destination: str):
        Exif.start_message()

        meta_mie_destination = f"{meta_destination}/mie"

        Util.create_directory_or_abort(meta_mie_destination)

        exif = Exif(
            directory=image_destination,
            output_directory=meta_mie_destination,
            extension=self.extension
        )

        exif.do_exif(exiftool)

        Printer.done(suffix=" EXIF")

    @staticmethod
    def start_message():
        Printer.divider()
        print("🔄 Starting process! 🔄")
        Printer.divider()

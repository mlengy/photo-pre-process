from commands.exif import Exif
from commands.rename import Rename
from commands.texif import Texif, Preset, TexifType, TexifLevel
from util.exiftool import ExifTool
from util.helpers import Util, Printer


class Process:
    meta_destination_name = "meta"

    total_steps = 4

    def __init__(
            self,
            initials: str,
            directory: str,
            output_directory: str,
            keep_original: bool,
            preset: Preset,
            extension: str
    ):
        self.initials = initials
        self.directory = Util.strip_slashes(directory)
        self.output_directory = Util.strip_slashes(output_directory)
        self.keep_original = keep_original
        self.preset = preset
        self.extension = extension
        self.step_count = 1

    def process(self):
        Process.start_message()

        Rename.verify_initials(self.initials)
        Rename.verify_possible_directory(self.initials)
        Util.verify_directory(self.directory)

        with ExifTool() as exiftool:
            num_images = Util.verify_extension_exists(exiftool, self.extension, self.directory)

            Util.create_directory_or_abort(self.output_directory)

            image_destination = f"{self.output_directory}/{self.extension.lower()}"
            meta_destination = f"{image_destination}/{Process.meta_destination_name}"

            Util.create_directory_or_abort(image_destination)

            self.__rename(exiftool, image_destination, num_images)
            self.__texif(exiftool, image_destination, meta_destination, num_images)
            self.__exif(exiftool, image_destination, meta_destination, num_images)

        Printer.done_all()

    def __rename(self, exiftool: ExifTool, image_destination: str, num_images: int):
        Rename.start_message()

        rename = Rename(
            initials=self.initials,
            directory=self.directory,
            output_directory=image_destination,
            keep_original=self.keep_original,
            extension=self.extension
        )

        rename.step_count = self.step_count
        rename.total_steps = Process.total_steps

        if self.keep_original:
            rename.do_rename(exiftool, Rename.do_rename_copy, num_images)
        else:
            rename.do_rename(exiftool, Rename.do_rename_move, num_images)

        self.step_count += 1
        Printer.done(suffix=" rename")

    def __texif(self, exiftool: ExifTool, image_destination: str, meta_destination: str, num_images: int):
        Texif.start_message()

        meta_simple_destination = f"{meta_destination}/simple"
        meta_full_destination = f"{meta_destination}/full"

        Util.create_directory_or_abort(meta_simple_destination)
        Util.create_directory_or_abort(meta_full_destination)

        texif = Texif(
            directory=image_destination,
            output_directory=meta_destination,
            type=TexifType.full,
            level=TexifLevel.high,
            preset=self.preset,
            extension=self.extension
        )

        texif.step_count = self.step_count
        texif.total_steps = Process.total_steps

        texif.do_texif_simple(exiftool, num_images, meta_simple_destination)

        self.step_count += 1
        texif.step_count = self.step_count
        texif.do_texif_full(exiftool, num_images, meta_full_destination)

        self.step_count += 1
        Printer.done(suffix=" TEXIF")

    def __exif(self, exiftool: ExifTool, image_destination: str, meta_destination: str, num_images: int):
        Exif.start_message()

        meta_mie_destination = f"{meta_destination}/mie"

        Util.create_directory_or_abort(meta_mie_destination)

        exif = Exif(
            directory=image_destination,
            output_directory=meta_mie_destination,
            extension=self.extension
        )

        exif.step_count = self.step_count
        exif.total_steps = Process.total_steps

        exif.do_exif(exiftool, num_images)

        Printer.done(suffix=" EXIF")

    @staticmethod
    def start_message():
        Printer.divider()
        print("🔄 Starting process! 🔄")
        Printer.divider()

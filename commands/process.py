from util.helpers import Util
from commands.rename import Rename
from util.exiftool import ExifTool


class Process:
    meta_destination_name = "meta"

    def __init__(self, initials: str, directory: str, output_directory: str, keep_original: bool, extension: str):
        self.initials = initials
        self.directory = directory
        self.output_directory = output_directory
        self.keep_original = keep_original
        self.extension = extension

    def process(self):
        Util.verify_directory(self.directory)

        with ExifTool() as exiftool:
            Util.verify_extension_exists(exiftool, self.extension, self.directory)

            Util.create_directory_or_abort(self.output_directory)

            image_destination = f"{self.output_directory}/{self.extension.lower()}"
            meta_destination = f"{image_destination}/{Process.meta_destination_name}"

            Util.create_directory_or_abort(image_destination)

            self.__rename(exiftool, image_destination)
            self.__texif(exiftool, meta_destination)
            self.__exif(exiftool, meta_destination)

    def __rename(self, exiftool, image_destination):
        print("\nRenaming...\n")
        rename = Rename(
            self.initials,
            self.directory,
            image_destination,
            self.keep_original,
            self.extension
        )

        if self.keep_original:
            rename.do_rename(exiftool, Rename.do_rename_copy)
        else:
            rename.do_rename(exiftool, Rename.do_rename_move)

    def __texif(self, exiftool, meta_destination):
        meta_simple_destination = f"{meta_destination}/simple"
        meta_full_destination = f"{meta_destination}/full"

        Util.create_directory_or_abort(meta_simple_destination)
        Util.create_directory_or_abort(meta_full_destination)

        print("\nGenerating TEXIF files...\n")

    def __exif(self, exiftool, meta_destination):
        meta_mie_destination = f"{meta_destination}/mie"

        Util.create_directory_or_abort(meta_mie_destination)

        print("\nGenerating MIE files...\n")

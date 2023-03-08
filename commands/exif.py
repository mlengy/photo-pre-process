import os

from util.helpers import Util
from util.exiftool import ExifTool


class Exif:
    def __init__(self, directory: str, output_directory: str, extension: str):
        self.directory = directory
        self.output_directory = output_directory
        self.extension = extension

    def exif(self):
        Util.verify_directory(self.directory)

        with ExifTool() as exiftool:
            Util.verify_extension_exists(exiftool, self.extension, self.directory)

            Util.create_directory_or_abort(self.output_directory)

            self.do_exif(exiftool)

    def do_exif(self, exiftool: ExifTool):
        file_names = Util.get_valid_file_names(exiftool, self.extension, self.directory)

        for file_name in file_names:
            file_name_extensionless = os.path.splitext(file_name)[0]
            full_path_to = f"{self.output_directory}/{file_name_extensionless}.mie"

            print(f"Writing MIE binary dump to [{full_path_to}]...")

            exiftool.execute_with_extension(
                self.extension,
                "-o",
                full_path_to,
                "-all:all",
                "-icc_profile",
                f"{self.directory}/{file_name}"
            )

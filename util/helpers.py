import json
import os
import shutil
from typing import TextIO

import typer

from util.constants import Tags
from util.exiftool import ExifTool


class Util:
    @staticmethod
    def strip_slashes(directory: str):
        return directory.strip("/")

    @staticmethod
    def verify_directory(directory: str):
        print(f"📁 Using [{directory}] as working directory...")
        if not Util.is_directory_valid(directory):
            Printer.error_and_abort(f"Directory [{directory}] does not exist!")

    @staticmethod
    def is_directory_valid(directory: str):
        return os.path.isdir(directory)

    @staticmethod
    def create_directory_or_abort(directory: str):
        if not os.path.isdir(directory):
            Printer.waiting(f"Creating directory [{directory}] since it does not exist.")
            os.makedirs(directory)
        else:
            Printer.warning(f"Directory [{directory}] already exists!")
            Printer.prompt_continue("This will overwrite [{directory}]! Continue?")
            shutil.rmtree(directory)
            Util.create_directory_or_abort(directory)

    @staticmethod
    def verify_extension_exists(exiftool: ExifTool, extension: str, directory: str = "./"):
        if not Util._get_valid_file_names(exiftool, extension, directory):
            Printer.error_and_abort(f"There are no files with extension [{extension}] in directory [{directory}]!")

    @staticmethod
    def get_valid_file_names(exiftool: ExifTool, extension: str, directory: str = "./"):
        file_names = json.loads(Util._get_valid_file_names(exiftool, extension, directory))
        return list(map(lambda file_name: file_name[Tags.FileName], file_names))

    @staticmethod
    def _get_valid_file_names(exiftool: ExifTool, extension: str, directory):
        return exiftool.execute_with_extension(
            extension,
            f"-{Tags.JSONFormat}",
            f"-{Tags.FileName}",
            directory
        )

    @staticmethod
    def write_with_newline(file: TextIO, string: str = ""):
        file.write(f"{string}\n")


class Printer:
    @staticmethod
    def prompt_continue(text: str):
        typer.confirm(f"⁉️  {text}", abort=True)

    @staticmethod
    def divider():
        print(f"\n================================================================\n")

    @staticmethod
    def done_all(prefix: str = ""):
        Printer.divider()
        print(f"{prefix}🎉🎊🥳 Done! 🥳🎊🎉")
        Printer.divider()

    @staticmethod
    def done(prefix: str = "", suffix: str = ""):
        print(f"{prefix}👍 Done{suffix}!")

    @staticmethod
    def waiting(string: str, prefix: str = ""):
        print(f"{prefix}⏳ {string}")

    @staticmethod
    def warning(string: str, prefix: str = ""):
        print(f"{prefix}❗ {string}")

    @staticmethod
    def error_and_abort(string: str, prefix: str = ""):
        print(f"{prefix}‼️  {string}")
        raise typer.Abort()

    @staticmethod
    def error(string: str, prefix: str = ""):
        print(f"{prefix}‼️  {string}")

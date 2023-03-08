import os
import shutil
import json
from typing import TextIO
import typer

from util.constants import Tags
from util.exiftool import ExifTool


class Util:
    @staticmethod
    def verify_directory(directory: str):
        if not os.path.isdir(directory):
            print(f"Directory [{directory}] does not exist!")
            raise typer.Abort()

    @staticmethod
    def create_directory_or_abort(directory: str):
        if not os.path.isdir(directory):
            print(f"Creating directory [{directory}] since it does not exist.")
            os.makedirs(directory)
        else:
            print(f"Directory [{directory}] already exists!")
            user_continue = typer.prompt(f"This will overwrite [{directory}]! Continue? (y/n)")
            if user_continue.lower() == "y":
                shutil.rmtree(directory)
                Util.create_directory_or_abort(directory)
            else:
                raise typer.Abort()

    @staticmethod
    def verify_extension_exists(exiftool: ExifTool, extension: str, directory: str = "."):
        if not Util._get_valid_file_names(exiftool, extension, directory):
            print(f"There are no files with extension [{extension}] in directory [{directory}]!")
            raise typer.Abort()

    @staticmethod
    def get_valid_file_names(exiftool: ExifTool, extension: str, directory: str = "."):
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

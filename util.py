import os
import shutil
import json
import typer

from constants import Tags
from exiftool import ExifTool


class Util:
    @staticmethod
    def verify_directory(directory: str):
        if not os.path.isdir(directory):
            print(f"Directory [{directory}] does not exist!")
            raise typer.Exit(code=1)

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
                raise typer.Exit(code=1)

    @staticmethod
    def verify_extension_exists(exiftool: ExifTool, extension: str, directory: str = "."):
        if not Util._get_valid_file_names(exiftool, extension, directory):
            print(f"There are no files with extension [{extension}] in the current directory!")
            raise typer.Exit(code=1)

    @staticmethod
    def get_valid_file_names(exiftool: ExifTool, extension: str, directory: str = "."):
        file_names = json.loads(Util._get_valid_file_names(exiftool, extension, directory))
        return list(map(lambda file_name: file_name[Tags.FileName], file_names))

    @staticmethod
    def _get_valid_file_names(exiftool: ExifTool, extension: str, directory):
        return exiftool.execute_with_extension(extension, "-J", "-FileName", directory)

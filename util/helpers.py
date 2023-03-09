import json
import os
import shutil
from typing import TextIO

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from util.constants import Tags
from util.exiftool import ExifTool


class Util:
    @staticmethod
    def strip_slashes(directory: str):
        return directory.strip("/")

    @staticmethod
    def verify_directory(directory: str):
        Printer.console.print(f"[bright_black]📁 Using \[{directory}] as working directory...")
        if not Util.is_directory_valid(directory):
            Printer.error_and_abort(f"Directory \[{directory}] does not exist!")

    @staticmethod
    def is_directory_valid(directory: str):
        return os.path.isdir(directory)

    @staticmethod
    def create_directory_or_abort(directory: str):
        if not os.path.isdir(directory):
            Printer.waiting(f"Creating directory \[{directory}] since it does not exist.")
            os.makedirs(directory)
        else:
            Printer.warning(f"Directory \[{directory}] already exists!")
            Printer.prompt_continue(f"This will overwrite [{directory}]! Continue?")
            shutil.rmtree(directory)
            Util.create_directory_or_abort(directory)

    @staticmethod
    def verify_extension_exists(exiftool: ExifTool, extension: str, directory: str = "./"):
        with Printer.progress_spinner() as progress:
            progress.add_task(f"Verifying files with extension \[{extension}] exist in directory \[{directory}]...\n")
            valid_file_names = Util._get_valid_file_names(exiftool, extension, directory)
        if not valid_file_names:
            Printer.error_and_abort(f"There are no files with extension \[{extension}] in directory \[{directory}]!")
        else:
            return len(json.loads(valid_file_names))

    @staticmethod
    def get_valid_file_names(exiftool: ExifTool, extension: str, directory: str = "./"):
        with Printer.progress_spinner() as progress:
            progress.add_task(
                f"Getting files with extension \[{extension}] in directory \[{directory}]...\n"
            )
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
    console = Console()

    @staticmethod
    def prompt_continue(text: str):
        typer.confirm(f"⁉️  {text}", abort=True)

    @staticmethod
    def progress_label(label: str, step: int, total: int):
        return f"[magenta]{label} [cyan](step {step} of {total})\n"

    @staticmethod
    def progress_spinner():
        return Progress(
            SpinnerColumn(),
            TextColumn(" [progress.description]{task.description}"),
            console=Printer.console
        )

    @staticmethod
    def divider():
        Printer.console.print(f"\n[bright_magenta]================================================================\n")

    @staticmethod
    def done_all(prefix: str = ""):
        Printer.divider()
        Printer.console.print(f"[bright_green]{prefix}🎉🎊🥳 Done! 🥳🎊🎉")
        Printer.divider()

    @staticmethod
    def done(prefix: str = "", suffix: str = ""):
        Printer.console.print(f"[green]{prefix}👍 Done{suffix}!")

    @staticmethod
    def waiting(string: str, prefix: str = ""):
        Printer.console.print(f"[bright_black]{prefix}⏳ {string}")

    @staticmethod
    def warning(string: str, prefix: str = ""):
        Printer.console.print(f"[bright_yellow]{prefix}❗ {string}")

    @staticmethod
    def error_and_abort(string: str, prefix: str = ""):
        Printer.console.print(f"[bright_red]{prefix}‼️  {string}")
        raise typer.Abort()

    @staticmethod
    def error(string: str, prefix: str = ""):
        Printer.console.print(f"[bright_red]{prefix}‼️  {string}")

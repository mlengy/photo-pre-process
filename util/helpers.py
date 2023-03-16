import json
import os
import shutil
import traceback
from typing import TextIO

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from entities.filename import FileNameTypeError
from util.constants import Tags
from util.exiftool import ExifTool


class Util:
    __valid_file_names: list[str] = []

    @staticmethod
    def strip_slashes(directory: str):
        return directory.strip("/")

    @staticmethod
    def verify_directory(directory: str):
        Printer.console.print(f"{Printer.color_waiting}📁 Using \[{directory}] as working directory...")
        if not Util.is_directory_valid(directory):
            Printer.error_and_abort(f"Directory \[{directory}] does not exist!")

    @staticmethod
    def is_directory_valid(directory: str):
        return os.path.isdir(directory)

    @staticmethod
    def create_directory_or_abort(directory: str, input_directory: str):
        if not os.path.isdir(directory):
            Printer.waiting(f"Creating directory \[{directory}] since it does not exist.")
            os.makedirs(directory)
        else:
            if Util.strip_slashes(directory) == Util.strip_slashes(input_directory):
                Printer.waiting(f"Using input directory \[{directory}] as output directory...")
            else:
                Printer.warning(f"Directory \[{directory}] already exists!")
                Printer.prompt_continue_or_abort(f"This will overwrite [{directory}]! Continue?")
                shutil.rmtree(directory)
                Util.create_directory_or_abort(directory, input_directory)

    @staticmethod
    def verify_extensions_in_directory(exiftool: ExifTool, extension: str, directory: str = "./"):
        task_name = f"Verifying files with extension \[{extension}] in directory \[{directory}]...\n"
        valid_file_names = Util.get_valid_file_names(exiftool, extension, directory, task_name)
        if not valid_file_names:
            Printer.error_and_abort(f"There are no files with extension \[{extension}] in directory \[{directory}]!")
        else:
            return valid_file_names

    @staticmethod
    def num_files_in_directory(path: str):
        return len([name for name in os.listdir(path) if os.path.isfile(os.path.join(path, name))])

    @staticmethod
    def get_valid_file_names(exiftool: ExifTool, extension: str, directory: str = "./", task_name: str = None):
        if not Util.__valid_file_names:
            with Printer.progress_spinner() as progress:
                message = f"Getting files with extension \[{extension}] in directory \[{directory}]...\n" \
                    if not task_name else task_name
                progress.add_task(message)
                try:
                    file_names = Util.deserialize_data(
                        Util._get_valid_file_names(exiftool, extension, directory),
                        soft_error=False
                    )
                    Util.__valid_file_names = list(map(lambda file_name: file_name[Tags.FileName], file_names))
                except TypeError:
                    Util.__valid_file_names = []
        return Util.__valid_file_names

    @staticmethod
    def set_valid_file_names(valid_file_names: list[str]):
        Util.__valid_file_names = valid_file_names

    @staticmethod
    def write_with_newline(file: TextIO, string: str = ""):
        file.write(f"{string}\n")

    @staticmethod
    def deserialize_data(data: str, soft_error: bool = True):
        try:
            if not data:
                error_function = Printer.error if soft_error else Printer.error_and_abort
                error_function("Could not process data since it was empty!")
            else:
                return json.loads(data)
        except Exception:
            Printer.error(f"Error while deserializing JSON data!")
            traceback.print_exc()
            if not soft_error:
                raise TypeError()

    @staticmethod
    def _get_valid_file_names(exiftool: ExifTool, extension: str, directory):
        return exiftool.execute_with_extension(
            extension,
            f"-{Tags.JSONFormat}",
            f"-{Tags.FileName}",
            directory
        )


class Printer:
    console = Console(highlight=False)

    color_title = "[magenta]"
    color_subtitle = "[cyan]"
    color_divider = "[bright_magenta]"
    color_done_all = "[bright_green]"
    color_done = "[green]"
    color_waiting = "[bright_black]"
    color_warning = "[bright_yellow]"
    color_error = "[bright_red]"

    tab = "    "

    @staticmethod
    def prompt_continue(text: str, prefix: str = ""):
        return typer.confirm(f"{prefix}⁉️  {text}")

    @staticmethod
    def prompt_continue_or_abort(text: str):
        typer.confirm(f"⁉️  {text}", abort=True)

    @staticmethod
    def prompt(text: str, default: str, prefix: str = ""):
        return typer.prompt(f"{prefix}⁉️  {text}", default=default)

    @staticmethod
    def prompt_choices(text: str, choices: dict[int, str], default: str, prefix: str = ""):
        choice_set = set(choices.values())
        choice_int_set = set(choices.keys())

        while True:
            response = Printer.prompt(text, default, prefix)
            if response.isdigit() and int(response) in choice_int_set:
                response = choices[int(response)]
                Printer.waiting(f"Using \[{response}].", prefix=prefix)
                break
            elif response in choice_set:
                Printer.waiting(f"Using \[{response}].", prefix=prefix)
                break
            else:
                Printer.warning(f"\[{response}] is not a valid choice!", prefix=prefix)
                Printer.__prompt_choices_print(choices, prefix)
        return response.lower()

    @staticmethod
    def prompt_valid(text: str, valid_closure, default: str, prefix: str = ""):
        while True:
            response = str(Printer.prompt(text, default, prefix))
            try:
                valid_closure(response)
                break
            except FileNameTypeError as error:
                Printer.warning(f"\[{response}] is not a valid choice!", prefix=prefix)
                Printer.warning(error.message, prefix=prefix)
        return response

    @staticmethod
    def __prompt_choices_print(choices: dict[int, str], prefix: str = ""):
        Printer.waiting("Valid choices are one of the following:", prefix=prefix)
        for key, value in choices.items():
            Printer.print(f"{key}: {value}", prefix=f"{Printer.tab}{prefix}")

    @staticmethod
    def progress_label_with_steps(label: str, step: int, total: int):
        return f"{Printer.color_title}{label} {Printer.color_subtitle}(step {step} of {total})\n"

    @staticmethod
    def progress_label(label: str):
        return f"{Printer.color_title}{label}\n"

    @staticmethod
    def progress_spinner():
        return Progress(
            SpinnerColumn(),
            TextColumn(" [progress.description]{task.description}"),
            console=Printer.console
        )

    @staticmethod
    def print_files_skipped(num_files_skipped: int, warning: bool = False):
        if num_files_skipped == 0:
            Printer.waiting("All files processed successfully!\n")
        else:
            if warning:
                Printer.warning(f"Skipped processing for {num_files_skipped} file(s)!\n")
            else:
                Printer.error(f"Skipped processing for {num_files_skipped} file(s)!\n")

    @staticmethod
    def divider():
        Printer.console.print(
            f"\n{Printer.color_divider}================================================================\n"
        )

    @staticmethod
    def done_all(prefix: str = ""):
        Printer.divider()
        Printer.console.print(f"{Printer.color_done_all}{prefix}🎉🎊🥳 Done! 🥳🎊🎉")
        Printer.divider()

    @staticmethod
    def done(prefix: str = "", suffix: str = ""):
        Printer.console.print(f"{Printer.color_done}{prefix}👍 Done{suffix}!")

    @staticmethod
    def print(string: str, prefix: str = ""):
        Printer.console.print(f"{Printer.color_waiting}{prefix}{string}")

    @staticmethod
    def waiting(string: str, prefix: str = ""):
        Printer.console.print(f"{Printer.color_waiting}{prefix}⏳ {string}")

    @staticmethod
    def warning(string: str, prefix: str = ""):
        Printer.console.print(f"{Printer.color_warning}{prefix}❗ {string}")

    @staticmethod
    def error_and_abort(string: str, prefix: str = ""):
        Printer.error(string, prefix)
        raise typer.Abort()

    @staticmethod
    def error(string: str, prefix: str = ""):
        Printer.console.print(f"{Printer.color_error}{prefix}‼️  {string}")

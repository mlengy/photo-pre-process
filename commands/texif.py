import json
import os
import traceback
from enum import Enum
from typing import TextIO

import typer
from rich.progress import Progress

from util.constants import Tags
from util.exiftool import ExifTool
from util.helpers import Util, Printer


class Preset(str, Enum):
    fujifilmxt5 = "fujifilmxt5"


class TexifType(str, Enum):
    simple = "simple"
    full = "full"
    both = "both"


class TexifLevel(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class Texif:
    json_level_map = {TexifLevel.low.value: 1, TexifLevel.medium.value: 2, TexifLevel.high.value: 3}
    json_level_required_tags = "0"
    json_level_highest = 3

    json_key_tag = "tag"
    json_key_name = "name"
    json_key_prefix = "prefix"
    json_key_suffix = "suffix"
    json_key_delimiter = "delimiter"

    file_break_begin_level = "================ BEGIN LEVEL {} ================"
    file_break_end_level = "================= END LEVEL {} ================="

    def __init__(
            self,
            directory: str,
            output_directory: str,
            type: TexifType,
            level: TexifLevel,
            preset: Preset,
            extension: str
    ):
        self.directory = Util.strip_slashes(directory)
        self.output_directory = Util.strip_slashes(output_directory)
        self.type = type.value.lower()
        self.level = Texif.json_level_map[level.value]
        self.preset = preset.value
        self.extension = extension
        self.compiled_presets: list[list[tuple[str, list[str]]]] = []
        self.step_count = 1
        self.total_steps = 2 if self.type == "both" else 1

    def texif(self):
        Texif.start_message()

        Util.verify_directory(self.directory)

        with ExifTool() as exiftool:
            num_images = len(Util.verify_extensions_in_directory(exiftool, self.extension, self.directory))

            Util.create_directory_or_abort(self.output_directory)

            type_caught = False
            if self.type == "simple" or self.type == "both":
                type_caught = True
                self.do_texif_simple(exiftool, num_images)
                self.step_count += 1
            if self.type == "full" or self.type == "both":
                type_caught = True
                self.do_texif_full(exiftool, num_images)

            if not type_caught:
                Printer.error_and_abort(f"Type \[{self.type}] is not a valid type!")

        Printer.done_all()

    def do_texif_full(self, exiftool: ExifTool, num_images: int, output_directory: str = None):
        Printer.console.print("\n[magenta]🌐 Starting TEXIF full (HTML)! 🌐\n")

        output_directory_override = self.output_directory if not output_directory else output_directory
        file_names = Util.get_valid_file_names(exiftool, self.extension, self.directory)

        with Progress(console=Printer.console) as progress:
            progress_task = progress.add_task(
                Printer.progress_label(
                    "TEXIF full",
                    self.step_count,
                    self.total_steps
                ),
                total=num_images
            )

            for count, file_name in enumerate(file_names):
                file_path = f"{self.directory}/{file_name}"

                Printer.waiting(f"Generating full HTML dump for \[{file_path}]...")

                full_html_dump = exiftool.execute_with_extension(
                    self.extension,
                    f"-{Tags.HTMLDump}",
                    file_path
                )

                file_name_extensionless = os.path.splitext(file_name)[0]
                full_path_to = f"{output_directory_override}/{file_name_extensionless}.html"

                Printer.waiting(f"Writing full HTML dump to \[{full_path_to}]...", prefix="    ")

                with open(full_path_to, "w") as texif_file:
                    texif_file.write(full_html_dump)

                Printer.done(prefix="    ")

                progress.update(progress_task, completed=count + 1)

        Printer.done()

    def do_texif_simple(self, exiftool: ExifTool, num_images: int, output_directory: str = None):
        Printer.console.print("\n[magenta]📋 Starting TEXIF simple (TXT)! 📋\n")

        output_directory_override = self.output_directory if not output_directory else output_directory
        preset_directory = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'presets'))
        presets = {os.path.splitext(preset_path)[0] for preset_path in os.listdir(preset_directory)}

        if self.preset not in presets:
            Printer.error_and_abort(f"Cannot find preset \[{self.preset}]!")

        required_tags = self.__compile_preset(preset_directory)
        required_tags_formatted = [f"-{tag}" for tag in required_tags]
        required_tags_formatted.append(f"-{Tags.FileName}")

        file_names = Util.get_valid_file_names(exiftool, self.extension, self.directory)

        with Progress(console=Printer.console) as progress:
            progress_task = progress.add_task(
                Printer.progress_label(
                    "TEXIF simple",
                    self.step_count,
                    self.total_steps
                ),
                total=num_images
            )

            for count, file_name in enumerate(file_names):
                file_path = f"{self.directory}/{file_name}"

                Printer.waiting(f"Generating simple TEXIF for \[{file_path}]...")

                Printer.waiting(f"Building tag JSON...", prefix="    ")
                file_tags = json.loads(
                    exiftool.execute_with_extension(
                        self.extension,
                        f"-{Tags.JSONFormat}",
                        file_path,
                        *required_tags_formatted
                    )
                )[0]

                for required_tag in required_tags:
                    if required_tag not in file_tags:
                        Printer.warning(f"Warning: could not find tag \[{required_tag}]!", prefix="    ")

                file_name_extensionless = os.path.splitext(file_name)[0]
                full_path_to = f"{output_directory_override}/{file_name_extensionless}.txt"

                Printer.waiting(f"Writing TEXIF to \[{full_path_to}]...", prefix="    ")

                with open(full_path_to, "w") as texif_file:
                    Util.write_with_newline(texif_file, file_tags[Tags.FileName])
                    Util.write_with_newline(texif_file, file_tags[Tags.DateTimeOriginal])
                    Util.write_with_newline(texif_file)

                    for level in range(1, Texif.json_level_highest + 1):
                        if self.level >= level:
                            self.__process_level(level, file_tags, texif_file)

                Printer.done(prefix="    ")

                progress.update(progress_task, completed=count + 1)

        Printer.done()

    def __process_level(self, level: int, file_tags: dict, texif_file: TextIO):
        compiled_preset = self.compiled_presets[level - 1]

        Util.write_with_newline(texif_file, Texif.file_break_begin_level.format(level))
        Util.write_with_newline(texif_file, file_tags[Tags.FileName])

        for format_string, argument_order in compiled_preset:
            arguments = [file_tags.get(argument, "") for argument in argument_order]
            Util.write_with_newline(texif_file, format_string.format(*arguments))

        Util.write_with_newline(texif_file, Texif.file_break_end_level.format(level))
        Util.write_with_newline(texif_file)

    def __compile_preset(self, preset_directory: str):
        try:
            Printer.waiting(f"Compiling preset \[{self.preset}]...")
            with open(f"{preset_directory}/{self.preset}.json") as preset_file:
                preset_json = json.load(preset_file)
                required_tags = set()

                for level in range(1, Texif.json_level_highest + 1):
                    required_tags |= self.__compile_preset_level(level, preset_json[str(level)])

                Printer.waiting("Requiring the following tags:")
                Printer.console.print(f"[bright_black]{required_tags}\n")
                return required_tags
        except Exception:
            Printer.error(f"Error while compiling preset \[{self.preset}]!")
            traceback.print_exc()
            raise typer.Abort()

    def __compile_preset_level(self, level, preset_level: list[list[dict]]):
        required_tags = set()

        self.compiled_presets.append([])
        for preset_line in preset_level:
            required_tags |= self.__compile_preset_line(level, preset_line)

        return required_tags

    def __compile_preset_line(self, level, preset_line: list[dict]):
        required_tags = []

        if not preset_line:
            return set()

        first_tag = preset_line[0]
        delimiter = first_tag[Texif.json_key_delimiter] if Texif.json_key_delimiter in first_tag else ""
        compiled_tags = []

        for tag in preset_line:
            required_tags.append(tag[Texif.json_key_tag])
            name = tag.get(Texif.json_key_name, "")
            name = "" if not name else f"{name}: "
            prefix = tag.get(Texif.json_key_prefix, "")
            suffix = tag.get(Texif.json_key_suffix, "")

            compiled_tags.append(f"{prefix}{name}{{}}{suffix}")

        self.compiled_presets[level - 1].append(
            (delimiter.join(compiled_tags), required_tags)
        )

        return set(required_tags)

    @staticmethod
    def start_message():
        Printer.divider()
        Printer.console.print("[bright_magenta]📃 Starting TEXIF! 📃")
        Printer.divider()

import json
import os
import traceback
from datetime import datetime
from enum import Enum
from typing import TextIO

import typer
from rich.progress import Progress

from entities.filter import Filter
from util.constants import Tags
from util.exiftool import ExifTool
from util.helpers import Util, Printer


class Preset(str, Enum):
    auto = "auto"
    fujifilm_xt5_still = "fujifilm_xt5_still"
    fujifilm_xt5_video = "fujifilm_xt5_video"


class FileType(str, Enum):
    still = "still"
    video = "video"


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

    preset_make_map = {
        "FUJIFILM": "fujifilm"
    }

    preset_model_map = {
        "X-T5": "xt5"
    }

    preset_file_type_map = {
        "JPEG": FileType.still.value,
        "RAF": FileType.still.value,
        "MOV": FileType.video.value
    }

    def __init__(
            self,
            directory: str,
            output_directory: str,
            type: TexifType,
            level: TexifLevel,
            preset: Preset,
            filter_files: bool,
            extension: str
    ):
        self.directory = Util.strip_slashes(directory)
        self.output_directory = Util.strip_slashes(output_directory)
        self.type = type.value.lower()
        self.level = Texif.json_level_map[level.value]
        self.preset = preset.value
        self.filter_files = filter_files
        self.extension = extension
        self.compiled_presets: list[list[tuple[str, list[str]]]] = []
        self.step_count = 1
        self.total_steps = 3 if self.type == "both" else 2

    def texif(self):
        Texif.start_message()

        Util.verify_directory(self.directory)

        with ExifTool() as exiftool:
            Util.verify_extensions_in_directory(exiftool, self.extension, self.directory)

            Util.create_directory_or_abort(self.output_directory, self.directory)

            file_names = Util.get_valid_file_names(exiftool, self.extension, self.directory)

            formatted_filter = Filter.build_filter(self.filter_files, self.total_steps)
            filtered_file_names = formatted_filter.filter(file_names)
            self.step_count += 1

            if not filtered_file_names:
                Printer.error_and_abort("There are no valid files to generate TEXIFs for!")

            type_caught = False
            if self.type == "simple" or self.type == "both":
                type_caught = True
                self.do_texif_simple(exiftool, filtered_file_names)
                self.step_count += 1
            if self.type == "full" or self.type == "both":
                type_caught = True
                self.do_texif_full(exiftool, filtered_file_names)

            if not type_caught:
                Printer.error_and_abort(f"Type \[{self.type}] is not a valid type!")

        Printer.done_all()

    def do_texif_full(self, exiftool: ExifTool, file_names: list[str], output_directory: str = None):
        Printer.console.print(f"\n{Printer.color_title}🌐 Starting TEXIF full (HTML)! 🌐\n")

        num_files = len(file_names)

        output_directory_override = self.output_directory if not output_directory else output_directory

        with Progress(console=Printer.console, auto_refresh=False) as progress:
            progress_task = progress.add_task(
                Printer.progress_label_with_steps(
                    "TEXIF full",
                    self.step_count,
                    self.total_steps
                ),
                total=num_files
            )

            num_files_skipped = 0

            for count, file_name in enumerate(file_names):
                progress.update(progress_task, completed=count)
                progress.refresh()

                file_path = os.path.join(self.directory, file_name)

                Printer.waiting(f"Generating full HTML dump for \[{file_path}]...")

                full_html_dump = exiftool.execute_with_extension(
                    self.extension,
                    f"-{Tags.HTMLDump}",
                    file_path
                )

                if not full_html_dump:
                    Printer.warning(f"Skipping \[{file_path}] as no data was found!")
                    num_files_skipped += 1
                    continue

                file_name_extensionless = os.path.splitext(file_name)[0]
                full_path_to = f"{os.path.join(output_directory_override, file_name_extensionless)}.html"

                Printer.waiting(f"Writing full HTML dump to \[{full_path_to}]...", prefix=Printer.tab)

                with open(full_path_to, "w") as texif_file:
                    texif_file.write(full_html_dump)

                Printer.done(prefix=Printer.tab)

            progress.update(progress_task, completed=num_files)

        Printer.print_files_skipped(num_files_skipped)

        Printer.done()

    def do_texif_simple(self, exiftool: ExifTool, file_names: list[str], output_directory: str = None):
        Printer.console.print(f"\n{Printer.color_title}📋 Starting TEXIF simple (TXT)! 📋\n")

        num_files = len(file_names)

        output_directory_override = self.output_directory if not output_directory else output_directory
        preset_directory = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'presets'))
        presets = {os.path.splitext(preset_path)[0] for preset_path in os.listdir(preset_directory)}

        if self.preset == Preset.auto.value:
            self.__automatically_select_preset(exiftool, file_names)

        if self.preset not in presets:
            Printer.error_and_abort(f"Cannot find preset \[{self.preset}]!")

        required_tags = self.__compile_preset(preset_directory)
        required_tags_formatted = {f"-{tag}" for tag in required_tags}
        required_tags_formatted.add(f"-{Tags.FileName}")
        required_tags_formatted.add(f"-{Tags.DateTimeOriginal}")
        required_tags_formatted.add(f"-{Tags.OffsetTimeOriginal}")
        required_tags_formatted = list(required_tags_formatted)

        with Progress(console=Printer.console, auto_refresh=False) as progress:
            progress_task = progress.add_task(
                Printer.progress_label_with_steps(
                    "TEXIF simple",
                    self.step_count,
                    self.total_steps
                ),
                total=num_files
            )

            num_files_skipped = 0

            for count, file_name in enumerate(file_names):
                progress.update(progress_task, completed=count)
                progress.refresh()

                file_path = os.path.join(self.directory, file_name)

                Printer.waiting(f"Generating simple TEXIF for \[{file_path}]...")

                Printer.waiting(f"Building tag JSON...", prefix=Printer.tab)
                file_tags = Util.deserialize_data(
                    exiftool.execute_with_extension(
                        self.extension,
                        f"-{Tags.JSONFormat}",
                        file_path,
                        *required_tags_formatted
                    )
                )

                if not file_tags:
                    Printer.warning(f"Skipping \[{file_path}] due to error!")
                    num_files_skipped += 1
                    continue

                file_tags = file_tags[0]

                for required_tag in required_tags:
                    if required_tag not in file_tags:
                        Printer.warning(f"Warning: could not find tag \[{required_tag}]!", prefix=Printer.tab)

                file_name_extensionless = os.path.splitext(file_name)[0]
                full_path_to = f"{os.path.join(output_directory_override, file_name_extensionless)}.txt"

                Printer.waiting(f"Writing TEXIF to \[{full_path_to}]...", prefix=Printer.tab)

                with open(full_path_to, "w") as texif_file:
                    Util.write_with_newline(texif_file, f"Media filename: {file_tags[Tags.FileName]}")
                    Util.write_with_newline(
                        texif_file,
                        f"Media created: {file_tags[Tags.DateTimeOriginal]}{file_tags[Tags.OffsetTimeOriginal]}"
                    )

                    generation_date_time = datetime.now().astimezone()
                    generation_offset = generation_date_time.strftime("%z")
                    generation_offset_formatted = f"{generation_offset[:3]}:{generation_offset[3:]}"
                    generation_date_time_formatted = \
                        generation_date_time.strftime("%Y:%m:%d %H:%M:%S") + generation_offset_formatted
                    Util.write_with_newline(texif_file, f"TEXIF created: {generation_date_time_formatted}")
                    Util.write_with_newline(texif_file, f"TEXIF preset: {self.preset}")
                    Util.write_with_newline(texif_file)

                    for level in range(1, Texif.json_level_highest + 1):
                        if self.level >= level:
                            self.__process_level(level, file_tags, texif_file)

                Printer.done(prefix=Printer.tab)

            progress.update(progress_task, completed=num_files)

        Printer.print_files_skipped(num_files_skipped)

        Printer.done()

    def __automatically_select_preset(self, exiftool: ExifTool, file_names: list[str]):
        file_path = os.path.join(self.directory, file_names[0])

        try:
            file_tags = Util.deserialize_data(
                exiftool.execute_with_extension(
                    self.extension,
                    f"-{Tags.JSONFormat}",
                    f"-{Tags.Make}",
                    f"-{Tags.Model}",
                    f"-{Tags.FileType}",
                    file_path
                ),
                soft_error=False
            )
        except TypeError:
            file_tags = []

        if not file_tags:
            Printer.error_and_abort("Failed to automatically select preset to use!")

        file_tags = file_tags[0]

        decoded_chunks = [Texif.__decode_preset_chunk(Texif.preset_make_map, file_tags.get(Tags.Make)),
                          Texif.__decode_preset_chunk(Texif.preset_model_map, file_tags.get(Tags.Model)),
                          Texif.__decode_preset_chunk(Texif.preset_file_type_map, file_tags.get(Tags.FileType))]
        generated_preset = "_".join(decoded_chunks)

        Printer.prompt_continue_or_abort(f"Use automatically selected preset [{generated_preset}]?")

        self.preset = generated_preset

    @staticmethod
    def __decode_preset_chunk(chunk_map: dict[str, str], decode_from: str):
        if not decode_from:
            Texif.__decode_preset_chunk_error(decode_from)

        decode_result = chunk_map.get(decode_from)

        if not decode_result:
            Texif.__decode_preset_chunk_error(decode_from)

        return decode_result

    @staticmethod
    def __decode_preset_chunk_error(decode_from: str):
        Printer.error_and_abort(f"Failed to decode preset chunk \[{decode_from}]!")

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
            with open(f"{os.path.join(preset_directory, self.preset)}.json") as preset_file:
                preset_json = json.load(preset_file)
                required_tags = set()

                for level in range(1, Texif.json_level_highest + 1):
                    required_tags |= self.__compile_preset_level(level, preset_json[str(level)])

                Printer.waiting("Requiring the following tags:")
                Printer.console.print(f"{Printer.color_waiting}{required_tags}\n")
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
        Printer.console.print(f"{Printer.color_divider}📃 Starting TEXIF! 📃")
        Printer.divider()

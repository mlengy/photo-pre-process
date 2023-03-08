import os
import traceback
import json
from typing import TextIO
import typer

from util.helpers import Util
from util.constants import Tags
from util.exiftool import ExifTool


class Texif:
    json_level_required_tags = "0"
    json_level_highest = 3

    json_key_tag = "tag"
    json_key_name = "name"
    json_key_prefix = "prefix"
    json_key_suffix = "suffix"
    json_key_delimiter = "delimiter"

    file_break_begin_level = "================ BEGIN LEVEL {} ================"
    file_break_end_level = "================= END LEVEL {} ================="

    def __init__(self, directory: str, output_directory: str, type: str, level: int, preset: str, extension: str):
        self.directory = directory
        self.output_directory = output_directory
        self.type = type
        self.level = level
        self.preset = preset
        self.extension = extension
        self.compiled_presets: list[list[tuple[str, list[str]]]] = []

    def texif(self):
        Util.verify_directory(self.directory)

        with ExifTool() as exiftool:
            Util.verify_extension_exists(exiftool, self.extension, self.directory)

            Util.create_directory_or_abort(self.output_directory)

            type_cleaned = self.type.lower()

            type_caught = False
            if type_cleaned == "simple" or type_cleaned == "both":
                type_caught = True
                self.do_texif_simple(exiftool)
            if type_cleaned == "full" or type_cleaned == "both":
                type_caught = True
                self.do_texif_full(exiftool)

            if not type_caught:
                print(f"Type [{self.type}] is not a valid type!")

    def do_texif_full(self, exiftool: ExifTool, output_directory: str = None):
        output_directory_override = self.output_directory if not output_directory else output_directory
        file_names = Util.get_valid_file_names(exiftool, self.extension, self.directory)

        for file_name in file_names:
            print(f"Generating full HTML dump for [{file_name}]...")
            full_html_dump = exiftool.execute_with_extension(
                self.extension,
                f"-{Tags.HTMLDump}",
                f"{self.directory}/{file_name}"
            )

            file_name_extensionless = os.path.splitext(file_name)[0]
            full_path_to = f"{output_directory_override}/{file_name_extensionless}.html"

            print(f"    Writing full HTML dump to [{full_path_to}]...")

            with open(full_path_to, "a") as texif_file:
                texif_file.write(full_html_dump)

            print("    Done!")
        print("Done!")

    def do_texif_simple(self, exiftool: ExifTool, output_directory: str = None):
        output_directory_override = self.output_directory if not output_directory else output_directory
        preset_directory = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'presets'))
        presets = {os.path.splitext(preset_path)[0] for preset_path in os.listdir(preset_directory)}

        if self.preset not in presets:
            print(f"Cannot find preset [{self.preset}]!")
            raise typer.Abort()

        required_tags = self.__compile_preset(preset_directory)
        required_tags_formatted = [f"-{tag}" for tag in required_tags]
        required_tags_formatted.append(f"-{Tags.FileName}")

        file_names = Util.get_valid_file_names(exiftool, self.extension, self.directory)

        for file_name in file_names:
            print(f"Generating simple TEXIF for [{file_name}]...")

            print("    Building tag JSON...")
            file_tags = json.loads(
                exiftool.execute_with_extension(
                    self.extension,
                    f"-{Tags.JSONFormat}",
                    f"{self.directory}/{file_name}",
                    *required_tags_formatted
                )
            )[0]

            for required_tag in required_tags:
                if required_tag not in file_tags:
                    print(f"    Warning: could not find tag [{required_tag}]!")

            file_name_extensionless = os.path.splitext(file_name)[0]
            full_path_to = f"{output_directory_override}/{file_name_extensionless}.txt"

            print(f"    Writing TEXIF to [{full_path_to}]...")

            with open(full_path_to, "a") as texif_file:
                Util.write_with_newline(texif_file, file_tags[Tags.FileName])
                Util.write_with_newline(texif_file, file_tags[Tags.DateTimeOriginal])
                Util.write_with_newline(texif_file)

                for level in range(1, Texif.json_level_highest + 1):
                    if self.level >= level:
                        self.__process_level(level, file_tags, texif_file)

            print("    Done!")
        print("Done!")

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
            print(f"Compiling preset [{self.preset}]...")
            with open(f"{preset_directory}/{self.preset}.json") as preset_file:
                preset_json = json.load(preset_file)
                required_tags = set()

                for level in range(1, Texif.json_level_highest + 1):
                    required_tags |= self.__compile_preset_level(level, preset_json[str(level)])

                print("Requiring the following tags:")
                print(required_tags)
                return required_tags
        except Exception:
            print(f"Error while compiling preset [{self.preset}]!")
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

import os.path
import shutil
from enum import Enum

from rich.progress import Progress

from entities.filename import FileName, FileNameTypeError
from entities.rating import Rating
from entities.style import Style
from util.config import Config
from util.constants import Tags
from util.exiftool import ExifTool
from util.helpers import Util, Printer


class EditType(str, Enum):
    none = "none"
    initials = "initials"
    datetime = "datetime",
    sequence = "sequence",
    style = "style"
    rating = "rating"
    style_rating = "style_rating"
    original = "original"


class Rename:
    styles = {style.value: style.name for style in Style}
    ratings = {rating.value: rating.name for rating in Rating}

    def __init__(
            self,
            initials: str,
            directory: str,
            output_directory: str,
            keep_original: bool,
            edit_type: EditType,
            extension: str
    ):
        self.initials = initials
        self.directory = Util.strip_slashes(directory)
        self.output_directory = Util.strip_slashes(output_directory)
        self.keep_original = keep_original
        self.edit_type = edit_type
        self.extension = extension
        self.step_count = 1
        self.total_steps = 2

    def rename(self):
        Rename.start_message()

        try:
            FileName.validate_initials(self.initials)
        except FileNameTypeError as error:
            Printer.error_and_abort(error.message)

        Rename.verify_possible_directory(self.initials)
        Util.verify_directory(self.directory)

        with ExifTool() as exiftool:
            Util.verify_extensions_in_directory(exiftool, self.extension, self.directory)

            Util.create_directory_or_abort(self.output_directory)

            if self.keep_original:
                self.do_rename(exiftool, Rename.do_rename_copy)
            else:
                self.do_rename(exiftool, Rename.do_rename_move)

        Printer.done_all()

    def do_rename(self, exiftool: ExifTool, file_modification_closure):
        file_names = Util.get_valid_file_names(exiftool, self.extension, self.directory)
        should_full_rename = self.edit_type == EditType.none

        filtered_file_names = self.__filter_file_names(file_names, invalid=should_full_rename)
        self.step_count += 1

        if not filtered_file_names:
            Printer.error_and_abort("There are no valid files to rename!")

        if self.edit_type == EditType.none:
            self.__do_rename(exiftool, file_modification_closure, filtered_file_names)
        else:
            self.__do_edit(file_modification_closure, filtered_file_names)

    def __do_edit(self, file_modification_closure, file_names: list[FileName]):
        new_file_names = []

        num_files = len(file_names)

        Printer.console.print(f"{Printer.color_title}✍️  Starting rename with edit! ✍️\n")

        files_processed = 0

        for count, file_name in enumerate(file_names):
            previous_file_name = str(file_name)
            file_path = os.path.join(self.directory, previous_file_name)

            Printer.waiting(f"Renaming \[{file_path}]...")

            try:
                if self.edit_type == EditType.initials:
                    file_name.update_initials(Rename.__edit_prompt_initials(file_name.initials))

                if self.edit_type == EditType.datetime:
                    file_name.update_date_time(Rename.__edit_prompt_date_time(file_name.date_time))

                if self.edit_type == EditType.sequence:
                    file_name.update_sequence(Rename.__edit_prompt_sequence(file_name.sequence))

                if self.edit_type == EditType.style or self.edit_type == EditType.style_rating:
                    file_name.update_style(Rename.__edit_prompt_style(file_name.style.name))

                if self.edit_type == EditType.rating or self.edit_type == EditType.style_rating:
                    file_name.update_rating(Rename.__edit_prompt_rating(file_name.rating.name))

                if self.edit_type == EditType.original:
                    file_name.update_original(Rename.__edit_prompt_original(file_name.original))
            except FileNameTypeError as error:
                Printer.error("Error while updating filename!")
                Printer.error(error.message)
                continue

            new_file_name = str(file_name)
            new_file_names.append(new_file_name)

            full_path_to = os.path.join(self.output_directory, new_file_name)
            file_modification_closure(file_path, full_path_to)

            files_processed += 1

        Printer.console.print("")

        num_files_in_directory = Util.num_files_in_directory(self.output_directory)

        num_files_skipped = max(
            num_files - num_files_in_directory,
            num_files - files_processed
        )
        Printer.print_files_skipped(num_files_skipped)

        Printer.done()

        Util.set_valid_file_names(new_file_names)

    def __do_rename(self, exiftool: ExifTool, file_modification_closure, file_names: list[str]):
        new_file_names = []

        num_files = len(file_names)

        Printer.console.print(f"{Printer.color_title}✍️  Starting rename! ✍️\n")

        with Progress(console=Printer.console, auto_refresh=False) as progress:
            progress_task = progress.add_task(
                Printer.progress_label_with_steps(
                    "Rename",
                    self.step_count,
                    self.total_steps
                ),
                total=num_files
            )

            previous_date_time = ""
            sequence_number = 0
            num_files_skipped = 0

            for count, file_name in enumerate(file_names):
                file_path = os.path.join(self.directory, file_name)

                Printer.waiting(f"Renaming \[{file_path}]...")
                Printer.waiting(f"Generating formatted datetime for \[{file_path}]...", prefix=Printer.tab)

                file_tags = Util.deserialize_data(
                    exiftool.execute_with_extension(
                        self.extension,
                        f"-{Tags.JSONFormat}",
                        f"-{Tags.DateTimeOriginal}",
                        "-d",
                        Config.file_name_date_format,
                        file_path
                    )
                )

                if not file_tags:
                    Printer.warning(f"Skipping \[{file_path}] due to error!", prefix=Printer.tab)
                    num_files_skipped += 1
                    continue

                formatted_date_time = file_tags[0][Tags.DateTimeOriginal]

                if formatted_date_time == previous_date_time:
                    sequence_number += 1
                else:
                    previous_date_time = formatted_date_time
                    sequence_number = 0

                full_filename = str(
                    FileName(
                        initials=self.initials,
                        date_time=formatted_date_time,
                        sequence=sequence_number,
                        original=file_name
                    )
                )

                new_file_names.append(full_filename)

                full_path_to = os.path.join(self.output_directory, full_filename)
                file_modification_closure(file_path, full_path_to)

                progress.update(progress_task, completed=count + 1)
                progress.refresh()

        Printer.print_files_skipped(num_files_skipped)

        Printer.done()

        Util.set_valid_file_names(new_file_names)

    def __filter_file_names(self, file_names: list[str], invalid: bool):
        num_files = len(file_names)

        filtered_file_names = []

        filter_type = "invalid" if invalid else "valid"
        Printer.console.print(f"\n{Printer.color_title}✂️  Filtering for {filter_type} file names! ✂️\n")

        with Progress(console=Printer.console, auto_refresh=False) as progress:
            progress_task = progress.add_task(
                Printer.progress_label_with_steps(
                    "Filter",
                    self.step_count,
                    self.total_steps
                ),
                total=num_files
            )

            if invalid:
                for count, file_name in enumerate(file_names):
                    try:
                        Printer.waiting(f"Checking file \[{file_name}]...")
                        FileName.from_string(file_name)
                        Printer.warning(f"Skipping \[{file_name}] as it is already renamed!", prefix=Printer.tab)
                    except FileNameTypeError:
                        filtered_file_names.append(file_name)
                    finally:
                        progress.update(progress_task, completed=count + 1)
                        progress.refresh()
            else:
                for count, file_name in enumerate(file_names):
                    try:
                        Printer.waiting(f"Checking file \[{file_name}]...")
                        filtered_file_names.append(FileName.from_string(file_name))
                    except FileNameTypeError as error:
                        Printer.warning(f"Skipping \[{file_name}] as it is malformed!", prefix=Printer.tab)
                        Printer.warning(error.message, prefix=Printer.tab)
                    finally:
                        progress.update(progress_task, completed=count + 1)
                        progress.refresh()

        Printer.print_files_skipped(len(file_names) - len(filtered_file_names), warning=True)

        return filtered_file_names

    @staticmethod
    def do_rename_copy(from_path: str, to_path: str):
        Printer.waiting(f"Copying \[{from_path}] to \[{to_path}]...", prefix=Printer.tab)
        shutil.copy2(from_path, to_path)

    @staticmethod
    def do_rename_move(from_path: str, to_path: str):
        Printer.waiting(f"Moving \[{from_path}] to \[{to_path}]...", prefix=Printer.tab)
        shutil.move(from_path, to_path)

    @staticmethod
    def verify_possible_directory(directory: str):
        if Util.is_directory_valid(directory):
            Printer.warning(f"It looks like your initials \[{directory}] is a directory.")
            Printer.prompt_continue(f"Is this correct?")

    @staticmethod
    def __edit_prompt_initials(default: str):
        return Printer.prompt_valid(
            text="Enter initials",
            valid_closure=FileName.validate_initials,
            default=str(default),
            prefix=Printer.tab
        )

    @staticmethod
    def __edit_prompt_date_time(default: str):
        return Printer.prompt_valid(
            text="Enter datetime",
            valid_closure=FileName.validate_date_time,
            default=str(default),
            prefix=Printer.tab
        )

    @staticmethod
    def __edit_prompt_sequence(default: str):
        return Printer.prompt_valid(
            text="Enter sequence",
            valid_closure=FileName.validate_sequence,
            default=str(default),
            prefix=Printer.tab
        )

    @staticmethod
    def __edit_prompt_style(default: str):
        return Printer.prompt_choices(
            text="Enter style",
            choices=Rename.styles,
            default=default,
            prefix=Printer.tab
        )

    @staticmethod
    def __edit_prompt_rating(default: str):
        return Printer.prompt_choices(
            text="Enter rating",
            choices=Rename.ratings,
            default=default,
            prefix=Printer.tab
        )

    @staticmethod
    def __edit_prompt_original(default: str):
        return Printer.prompt(
            text="Enter original",
            default=default,
            prefix=Printer.tab
        )

    @staticmethod
    def start_message():
        Printer.divider()
        Printer.console.print(f"{Printer.color_divider}🖋️  Starting rename! 🖋️")
        Printer.divider()

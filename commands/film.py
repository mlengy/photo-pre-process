import os

from rich.progress import Progress

from entities.filename import FileName
from entities.filmroll import FilmRoll
from entities.filter import Filter
from util.constants import Tags
from util.exiftool import ExifTool
from util.helpers import Util, Printer


class Film:
    output_file_name = "description"
    output_file_placeholder = [
        "description",
        "",
        "-"
    ]

    user_comment_film_make_key = "Film Make: "
    user_comment_film_type_key = "Film Type: "

    def __init__(
            self,
            directory: str,
            output_directory: str,
            filter_files: bool,
            extension: str
    ):
        self.directory = Util.strip_slashes(directory)
        self.output_directory = Util.strip_slashes(output_directory)
        self.filter_files = filter_files
        self.extension = extension
        self.step_count = 1
        self.total_steps = 2

    def film(self):
        Film.start_message()

        Util.verify_directory(self.directory)

        with ExifTool() as exiftool:
            Util.verify_extensions_in_directory(exiftool, self.extension, self.directory)

            Util.create_directory_or_abort(self.output_directory, self.directory)

            file_names = Util.get_valid_file_names(exiftool, self.extension, self.directory)

            formatted_filter = Filter.build_filter(self.filter_files, self.total_steps)
            filtered_file_names = formatted_filter.filter(file_names)
            self.step_count += 1

            if not filtered_file_names:
                Printer.error_and_abort("There are no valid files to generate metadata for!")

            self.do_film(exiftool, filtered_file_names)

        Printer.done_all()

    def do_film(self, exiftool: ExifTool, file_names: list[str]):
        Printer.console.print(f"\n{Printer.color_title}📋 Starting film metadata collection! 📋\n")

        num_files = len(file_names)

        required_tags = {
            Tags.Make,
            Tags.Model,
            Tags.Lens,
            Tags.UserComment
        }
        required_tags_formatted = {f"-{tag}" for tag in required_tags}

        with Progress(console=Printer.console, auto_refresh=False) as progress:
            progress_task = progress.add_task(
                Printer.progress_label_with_steps(
                    "Film metadata",
                    self.step_count,
                    self.total_steps
                ),
                total=num_files
            )

            num_files_skipped = 0

            film_rolls = {}

            for count, file_name in enumerate(file_names):
                progress.update(progress_task, completed=count)
                progress.refresh()

                file_path = os.path.join(self.directory, file_name)

                Printer.waiting(f"Collecting metadata for \[{file_path}]...")

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

                if not required_tags.issubset(file_tags):
                    Printer.warning(f"Skipping \[{file_path}] since could not find tag(s) {list(required_tags.difference(file_tags))}!")
                    num_files_skipped += 1
                    continue

                file_name_object = FileName.from_string(file_name)

                film_roll = film_rolls.get(
                    file_name_object.date_time,
                    FilmRoll(file_name_object)
                )

                tag_parsing_success = self.__update_film_roll_from_tags(film_roll, file_tags)

                if not tag_parsing_success:
                    Printer.warning(f"Skipping \[{file_path}] since could not parse user comment tag(s)!")
                    num_files_skipped += 1
                    continue

                film_rolls[file_name_object.date_time] = film_roll

            progress.update(progress_task, completed=num_files)

            full_path_to = f"{os.path.join(self.output_directory, Film.output_file_name)}.txt"

            film_roll_list = list(film_rolls.values())
            film_roll_list.sort(key=lambda x: x.full_date)

            Printer.print("")
            Printer.waiting(f"Writing combined metadata to \[{full_path_to}]...")

            with open(full_path_to, "w") as output_file:
                for placeholder in Film.output_file_placeholder:
                    Util.write_with_newline(output_file, placeholder)

                for film_roll in film_roll_list:
                    Util.write_with_newline(output_file, "")
                    Util.write_with_newline(output_file, film_roll.date)

                    for film_type in film_roll.pretty_film_types:
                        Util.write_with_newline(output_file, film_type)

                    for camera in film_roll.pretty_cameras:
                        Util.write_with_newline(output_file, camera)

                    for lens in film_roll.pretty_lenses:
                        Util.write_with_newline(output_file, lens)

            Printer.done(prefix=Printer.tab)

        Printer.print_files_skipped(num_files_skipped)

        Printer.done()

    @staticmethod
    def __update_film_roll_from_tags(film_roll: FilmRoll, file_tags: dict):
        user_comment = file_tags[Tags.UserComment].split("\n")
        film_make = ""
        film_type = ""

        for line in user_comment:
            if Film.user_comment_film_make_key in line:
                film_make = line.replace(Film.user_comment_film_make_key, "").strip()
            elif Film.user_comment_film_type_key in line:
                film_type = line.replace(Film.user_comment_film_type_key, "").strip()

        if not film_make or not film_type:
            return False

        film_roll.film_types.add(
            (film_make, film_type)
        )
        film_roll.cameras.add(
            (file_tags[Tags.Make], file_tags[Tags.Model])
        )
        film_roll.lenses.add(
            file_tags[Tags.Lens]
        )

        return True

    @staticmethod
    def start_message():
        Printer.divider()
        Printer.console.print(f"{Printer.color_divider}🎞️  Starting film! 🎞️")
        Printer.divider()

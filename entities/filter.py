from enum import Enum

from rich.progress import Progress

from entities.checker import HiddenChecker, Checker
from entities.filename import FileName, FileNameTypeError
from util.helpers import Printer, Util


class FilterType(Enum):
    FormattedFilter = 10
    MirrorFormattedFilter = 15
    UnformattedFilter = 20


class Filter:
    def __init__(self):
        self.checkers: list[Checker] = [
            HiddenChecker()
        ]
        self.filtered_file_names = []
        self.step_count = 1
        self.total_steps = 1

    def filter(self, file_names: list[str]):
        sorted_file_names = sorted(file_names)
        num_files = len(sorted_file_names)
        self.filtered_file_names = []

        Printer.console.print(f"\n{Printer.color_title}✂️  Filtering file names! ✂️\n")

        with Progress(console=Printer.console, auto_refresh=False) as progress:
            progress_task = progress.add_task(
                Printer.progress_label_with_steps(
                    "Filter",
                    self.step_count,
                    self.total_steps
                ),
                total=num_files
            )

            for count, file_name in enumerate(sorted_file_names):
                progress.update(progress_task, completed=count)
                progress.refresh()

                checks_pass, message = self._check_string_name(file_name)

                if not checks_pass:
                    Filter.print_skip(file_name, message)
                    continue

                self.filtered_file_names.append(file_name)

            progress.update(progress_task, completed=num_files)

        Printer.print_files_skipped(len(sorted_file_names) - len(self.filtered_file_names), warning=True)

        Util.set_valid_file_names(self.filtered_file_names)

        return self.filtered_file_names

    def _check_string_name(self, file_name: str):
        for checker in self.checkers:
            if checker.checks_strings and not checker.check_string(file_name):
                return False, checker.message
            return True, ""

    @staticmethod
    def build_filter(filter_files: bool, total_steps: int):
        return FormattedFilter.build(filter_files, total_steps) if filter_files else Filter()

    @staticmethod
    def build_filter_by_type(filter_type: FilterType):
        if filter_type == FilterType.FormattedFilter:
            return FormattedFilter()
        elif filter_type == FilterType.MirrorFormattedFilter:
            return MirrorFormattedFilter()
        else:
            return UnformattedFilter()

    @staticmethod
    def print_skip(file_name: str, message: str):
        Printer.warning(f"Skipping \[{file_name}] due to \[{message}]!", prefix=Printer.tab)


class FormattedFilter(Filter):
    def __init__(self):
        super().__init__()
        self.filtered_file_name_objects = []

    @staticmethod
    def build(build_checkers: bool = False, total_steps: int = 1):
        formatted_filter = FormattedFilter()
        formatted_filter.total_steps = total_steps

        if build_checkers:
            formatted_filter.prompt_build_checkers()

        return formatted_filter

    def filter(self, file_names: list[str]):
        sorted_file_names = sorted(file_names)
        num_files = len(sorted_file_names)
        self.filtered_file_names = []
        self.filtered_file_name_objects = []

        Printer.console.print(f"\n{Printer.color_title}✂️  Filtering for formatted file names! ✂️\n")

        with Progress(console=Printer.console, auto_refresh=False) as progress:
            progress_task = progress.add_task(
                Printer.progress_label_with_steps(
                    "Filter",
                    self.step_count,
                    self.total_steps
                ),
                total=num_files
            )

            for count, file_name in enumerate(sorted_file_names):
                progress.update(progress_task, completed=count)
                progress.refresh()
                try:
                    Printer.waiting(f"Checking file \[{file_name}]...")
                    file_name_object = FileName.from_string(file_name)

                    checks_pass, message = self.__check_formatted_name(file_name_object)

                    if not checks_pass:
                        Filter.print_skip(file_name, message)
                        continue

                    self.filtered_file_names.append(file_name)
                    self.filtered_file_name_objects.append(file_name_object)
                except FileNameTypeError as error:
                    Printer.warning(f"Skipping \[{file_name}] as it is unformatted!", prefix=Printer.tab)
                    Printer.warning(error.message, prefix=Printer.tab)

            progress.update(progress_task, completed=num_files)

        Printer.print_files_skipped(len(sorted_file_names) - len(self.filtered_file_name_objects), warning=True)

        Util.set_valid_file_names(self.filtered_file_names)

        return self.filtered_file_name_objects

    def __check_formatted_name(self, file_name_object: FileName):
        for checker in self.checkers:
            if not checker.check(file_name_object):
                return False, checker.message
        return True, ""

    def prompt_build_checkers(self):
        while True:
            filters_response = Printer.prompt("Which filters would you like to apply?", "none", prefix="\n")
            checkers = filters_response.split(' ')
            checkers_set = set(checkers)

            if filters_response == "none":
                Printer.warning("Cancelling filtering!")
                return

            if checkers_set.issubset(Checker.checkers):
                break
            else:
                Printer.error("Filters must be separated by a single space [ ] and be one of the following:")
                Printer.waiting(str(Checker.checkers_list_pretty))

        for checker in checkers:
            self.checkers.append(Checker.build(checker))


class MirrorFormattedFilter(Filter):
    def __init__(self):
        super().__init__()

    def filter(self, file_names: list[str]):
        pass


class UnformattedFilter(Filter):
    def __init__(self):
        super().__init__()

    def filter(self, file_names: list[str]):
        sorted_file_names = sorted(file_names)
        num_files = len(sorted_file_names)
        self.filtered_file_names = []

        Printer.console.print(f"\n{Printer.color_title}✂️  Filtering for unformatted file names! ✂️\n")

        with Progress(console=Printer.console, auto_refresh=False) as progress:
            progress_task = progress.add_task(
                Printer.progress_label_with_steps(
                    "Filter",
                    self.step_count,
                    self.total_steps
                ),
                total=num_files
            )

            for count, file_name in enumerate(sorted_file_names):
                progress.update(progress_task, completed=count)
                progress.refresh()

                checks_pass, message = self._check_string_name(file_name)

                if not checks_pass:
                    Filter.print_skip(file_name, message)
                    continue

                try:
                    Printer.waiting(f"Checking file \[{file_name}]...")
                    FileName.from_string(file_name)
                    Printer.warning(f"Skipping \[{file_name}] as it is formatted!", prefix=Printer.tab)
                except FileNameTypeError:
                    self.filtered_file_names.append(file_name)

            progress.update(progress_task, completed=num_files)

        Printer.print_files_skipped(len(sorted_file_names) - len(self.filtered_file_names), warning=True)

        Util.set_valid_file_names(self.filtered_file_names)

        return self.filtered_file_names

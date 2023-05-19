from entities.filename import FileName, FileNameChunk
from entities.rating import Rating
from entities.style import Style
from util.config import Config
from util.helpers import Printer


class Checker:
    checkers_list: list[FileNameChunk] = [checker for checker in FileNameChunk]
    checkers_list_pretty: list[str] = [checker.name for checker in checkers_list]
    checkers = set(checkers_list)

    __checker_to_builder = None

    def __init__(self, message: str):
        self.checks_strings = True
        self.message = message

    def check(self, file_name: FileName):
        pass

    def check_string(self, file_name: str):
        pass

    @staticmethod
    def build(checker: str):
        if not Checker.__checker_to_builder:
            Checker.__checker_to_builder = {
                FileNameChunk.initials.name: InitialsChecker.prompt_build,
                FileNameChunk.datetime.name: DateTimeChecker.prompt_build,
                FileNameChunk.sequence.name: SequenceChecker.prompt_build,
                FileNameChunk.style.name: StyleChecker.prompt_build,
                FileNameChunk.rating.name: RatingChecker.prompt_build,
                FileNameChunk.original.name: OriginalChecker.prompt_build
            }

        return Checker.__checker_to_builder[checker]()

    @staticmethod
    def prompt_build():
        pass

    @staticmethod
    def prompt(default: str):
        pass


class HiddenChecker(Checker):
    def __init__(self):
        super().__init__("hidden file")
        self.checks_strings = True

    def check(self, file_name: FileName):
        return not str(file_name).startswith('.')

    def check_string(self, file_name: str):
        return not file_name.startswith('.')


class InitialsChecker(Checker):
    def __init__(self, initials: str):
        super().__init__("initials did not match")
        self.checks_strings = False
        self.initials = initials

    def check(self, file_name: FileName):
        return file_name.initials.lower() == self.initials.lower()

    def check_string(self, file_name: str):
        pass

    @staticmethod
    def prompt_build():
        initials = InitialsChecker.prompt(Config.file_name_initials_default)
        return InitialsChecker(initials)

    @staticmethod
    def prompt(default: str):
        return Printer.prompt_valid(
            text="Enter initials",
            valid_closure=FileName.validate_initials,
            default=str(default),
            prefix=Printer.tab
        )


class DateTimeChecker(Checker):
    def __init__(self, date_time: str):
        super().__init__("datetime did not match")
        self.checks_strings = False
        self.date_time = date_time

    def check(self, file_name: FileName):
        return file_name.date_time == self.date_time

    def check_string(self, file_name: str):
        pass

    @staticmethod
    def prompt_build():
        date_time = DateTimeChecker.prompt(Config.file_name_date_default)
        return DateTimeChecker(date_time)

    @staticmethod
    def prompt(default: str):
        return Printer.prompt_valid(
            text="Enter datetime",
            valid_closure=FileName.validate_date_time,
            default=str(default),
            prefix=Printer.tab
        )


class SequenceChecker(Checker):
    def __init__(self, sequence: int):
        super().__init__("sequence did not match")
        self.checks_strings = False
        self.sequence = sequence

    def check(self, file_name: FileName):
        return file_name.sequence == self.sequence

    def check_string(self, file_name: str):
        pass

    @staticmethod
    def prompt_build():
        sequence = SequenceChecker.prompt(Config.file_name_sequence_default)
        return SequenceChecker(int(sequence))

    @staticmethod
    def prompt(default: str):
        return Printer.prompt_valid(
            text="Enter sequence",
            valid_closure=FileName.validate_sequence,
            default=str(default),
            prefix=Printer.tab
        )


class StyleChecker(Checker):
    styles = {style.value: style.name for style in Style}

    def __init__(self, style: Style):
        super().__init__("style did not match")
        self.checks_strings = False
        self.style = style

    def check(self, file_name: FileName):
        return file_name.style == self.style

    def check_string(self, file_name: str):
        pass

    @staticmethod
    def prompt_build():
        style = StyleChecker.prompt(Config.file_name_style_default)
        return StyleChecker(Style[style])

    @staticmethod
    def prompt(default: str):
        return Printer.prompt_choices(
            text="Enter style",
            choices=StyleChecker.styles,
            default=default,
            prefix=Printer.tab
        )


class RatingChecker(Checker):
    ratings = {rating.value: rating.name for rating in Rating}

    def __init__(self, rating: Rating):
        super().__init__("rating did not match")
        self.checks_strings = False
        self.rating = rating

    def check(self, file_name: FileName):
        return file_name.rating == self.rating

    def check_string(self, file_name: str):
        pass

    @staticmethod
    def prompt_build():
        rating = RatingChecker.prompt(Config.file_name_rating_default)
        return RatingChecker(Rating[rating])

    @staticmethod
    def prompt(default: str):
        return Printer.prompt_choices(
            text="Enter rating",
            choices=RatingChecker.ratings,
            default=default,
            prefix=Printer.tab
        )


class OriginalChecker(Checker):
    def __init__(self, original: str):
        super().__init__("original did not match")
        self.checks_strings = False
        self.original = original

    def check(self, file_name: FileName):
        return file_name.original == self.original

    def check_string(self, file_name: str):
        pass

    @staticmethod
    def prompt_build():
        original = OriginalChecker.prompt(Config.file_name_original_default)
        return OriginalChecker(original)

    @staticmethod
    def prompt(default: str):
        return Printer.prompt(
            text="Enter original",
            default=default,
            prefix=Printer.tab
        )

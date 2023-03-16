from entities.filename import FileName, FileNameChunk
from entities.rating import Rating
from entities.style import Style
from util.config import Config
from util.helpers import Printer


class Checker:
    checkers_list = [checker for checker in FileNameChunk]
    checkers = set(checkers_list)

    __checker_to_builder = None

    def __init__(self, message: str):
        self.message = message

    def check(self, file_name: FileName):
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

    def prompt_build(self):
        pass

    @staticmethod
    def prompt(default: str):
        pass


class HiddenChecker(Checker):
    def __init__(self):
        super().__init__("hidden file")

    def check(self, file_name: FileName):
        return not str(file_name).startswith('.')


class InitialsChecker(Checker):
    def __init__(self, initials: str):
        super().__init__("initials did not match")
        self.initials = initials

    def check(self, file_name: FileName):
        return file_name.initials == self.initials

    def prompt_build(self):
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
        super().__init__("")
        self.date_time = date_time

    def check(self, file_name: FileName):
        return file_name.date_time == self.date_time

    def prompt_build(self):
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
        super().__init__("")
        self.sequence = sequence

    def check(self, file_name: FileName):
        return file_name.sequence == self.sequence

    def prompt_build(self):
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
        super().__init__("")
        self.style = style

    def check(self, file_name: FileName):
        return file_name.style == self.style

    def prompt_build(self):
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
        super().__init__("")
        self.rating = rating

    def check(self, file_name: FileName):
        return file_name.rating == self.rating

    def prompt_build(self):
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
        super().__init__("")
        self.original = original

    def check(self, file_name: FileName):
        return file_name.original == self.original

    def prompt_build(self):
        original = OriginalChecker.prompt(Config.file_name_original_default)
        return OriginalChecker(original)

    @staticmethod
    def prompt(default: str):
        return Printer.prompt(
            text="Enter original",
            default=default,
            prefix=Printer.tab
        )

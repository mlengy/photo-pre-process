from datetime import datetime

from entities.rating import Rating
from entities.style import Style
from util.config import Config


class FileNameTypeError(TypeError):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class FileName:
    style_tag = 'S'
    rating_tag = 'R'

    initials_index = 0
    date_time_index = 1
    date_time_length = 2
    sequence_index = 2
    style_index = 3
    rating_index = 4
    original_index = 5

    expected_lengths = [
        # initials
        0,
        # date time
        Config.file_name_date_length,
        # sequence
        2,
        # style
        3,
        # rating
        2,
        # original
        0
    ]

    def __init__(
            self,
            initials: str,
            date_time: str,
            sequence: int,
            original: str,
            style: Style = Style.none,
            rating: Rating = Rating.none
    ):
        self.__initials = initials
        self.__date_time = date_time
        self.__sequence = sequence
        self.__style = style
        self.__rating = rating
        original_split = original.split('.')
        self.__original = original_split[0]
        self.__extension = original_split[1]
        self.__changed = False
        self.__formatted = self.__format()

    def __str__(self):
        if self.__changed:
            self.__formatted = self.__format()
            self.__changed = False

        return self.__formatted

    class PrettyFileName:
        def __init__(
                self,
                initials: str,
                date_time: str,
                sequence: int,
                original: str,
                extension: str,
                style: Style = Style.none,
                rating: Rating = Rating.none
        ):
            self.original = original
            self.extension = f".{extension}".upper()
            self.initials = initials.upper()
            date_time_object = datetime.strptime(date_time, Config.file_name_date_format)
            self.date_time = date_time_object.strftime("%Y-%m-%d %H:%M:%S")
            self.sequence = str(sequence)
            self.style = FileName.PrettyFileName.__enum_name_to_pretty(style.name)
            self.rating = FileName.PrettyFileName.__enum_name_to_pretty(rating.name)

        @staticmethod
        def __enum_name_to_pretty(enum_name: str):
            return enum_name.replace('_', ' ').capitalize()

    def to_pretty(self):
        return FileName.PrettyFileName(
            initials=self.__initials,
            date_time=self.__date_time,
            sequence=self.__sequence,
            original=self.__original,
            extension=self.__extension,
            style=self.__style,
            rating=self.__rating
        )

    @property
    def initials(self):
        return self.__initials

    @property
    def date_time(self):
        return self.__date_time

    @property
    def sequence(self):
        return self.__sequence

    @property
    def style(self):
        return self.__style

    @property
    def rating(self):
        return self.__rating

    @property
    def original(self):
        return self.__original

    def update_initials(self, initials: str):
        self.__changed = True
        self.__initials = FileName.validate_initials(initials)

    def update_date_time(self, date_time: str):
        self.__changed = True
        self.__date_time = FileName.validate_date_time(date_time)

    def update_sequence(self, sequence: str):
        self.__changed = True
        self.__sequence = FileName.validate_sequence(sequence)

    def update_style(self, style: str):
        self.__changed = True
        self.__style = FileName.__validate_style_name(style)

    def update_rating(self, rating: str):
        self.__changed = True
        self.__rating = FileName.__validate_rating_name(rating)

    def update_original(self, original: str):
        self.__changed = True
        self.__original = original

    @staticmethod
    def from_string(string: str):
        chunks = FileName.__chunk_filename(string)

        initials = FileName.validate_initials(chunks[FileName.initials_index])
        date_time = FileName.validate_date_time(chunks[FileName.date_time_index])
        sequence = FileName.validate_sequence(chunks[FileName.sequence_index])
        style = FileName.validate_style(chunks[FileName.style_index])
        rating = FileName.validate_rating(chunks[FileName.rating_index])

        return FileName(
            initials=initials,
            date_time=date_time,
            sequence=sequence,
            style=style,
            rating=rating,
            original=chunks[FileName.original_index]
        )

    @staticmethod
    def __chunk_filename(file_name: str):
        chunks = file_name.split(Config.file_name_delimiter)

        chunks_formatted = [
            chunks[0],
            Config.file_name_delimiter.join(
                chunks[FileName.date_time_index:FileName.date_time_index + FileName.date_time_length]
            )
        ]

        chunks_formatted.extend(chunks[FileName.date_time_index + FileName.date_time_length:])

        for index, chunk_formatted in enumerate(chunks_formatted):
            expected_length = FileName.expected_lengths[index]
            chunk_length = len(chunk_formatted)
            if not expected_length == 0 and not chunk_length == expected_length:
                raise FileNameTypeError(
                    f"Filename chunk \[{chunk_formatted}] is unexpected length! Expected \[{expected_length}] but got \[{chunk_length}]!"
                )

        return chunks_formatted

    @staticmethod
    def check_length(string: str, expected_length: int):
        string_length = len(string)
        if not expected_length == 0 and not expected_length == string_length:
            raise FileNameTypeError(
                f"\[{string}] is unexpected length! Expected \[{expected_length}] but got \[{string_length}]!"
            )

    @staticmethod
    def validate_initials(initials: str):
        FileName.check_length(initials, FileName.expected_lengths[FileName.initials_index])
        if not (initials.isalnum() and 1 < len(initials) <= 10):
            raise FileNameTypeError(f"Initials \[{initials}] is not valid!")
        else:
            return initials

    @staticmethod
    def validate_date_time(date_time: str):
        FileName.check_length(date_time, FileName.expected_lengths[FileName.date_time_index])
        try:
            datetime.strptime(date_time, Config.file_name_date_format)

            return date_time
        except ValueError:
            raise FileNameTypeError(f"Date time \[{date_time}] is not in format [{Config.file_name_date_format}]!")

    @staticmethod
    def validate_sequence(sequence: str):
        FileName.check_length(sequence, FileName.expected_lengths[FileName.sequence_index])
        try:
            return int(sequence)
        except ValueError:
            raise FileNameTypeError(f"Sequence \[{sequence}] is not a two digit number!")

    @staticmethod
    def validate_style(style: str):
        FileName.check_length(style, FileName.expected_lengths[FileName.style_index])
        try:
            style_tag = style[:len(FileName.style_tag)]
            style_id = style[len(FileName.style_tag):]

            if not style_tag == FileName.style_tag:
                raise ValueError()

            return Style(int(style_id))
        except ValueError:
            raise FileNameTypeError(
                f"Style \[{style}] is not a valid style, should be in form \[{FileName.style_tag}##]!"
            )

    @staticmethod
    def __validate_style_name(style: str):
        try:
            return Style[style]
        except ValueError:
            raise FileNameTypeError(
                f"Style \[{style}] is not a valid style!"
            )

    @staticmethod
    def validate_rating(rating: str):
        FileName.check_length(rating, FileName.expected_lengths[FileName.rating_index])
        try:
            rating_tag = rating[:len(FileName.rating_tag)]
            rating_id = rating[len(FileName.rating_tag):]

            if not rating_tag == FileName.rating_tag:
                raise ValueError()

            return Rating(int(rating_id))
        except ValueError:
            raise FileNameTypeError(
                f"Rating \[{rating}] is not a valid rating, should be in form \[{FileName.rating_tag}#]!"
            )

    @staticmethod
    def __validate_rating_name(rating: str):
        try:
            return Rating[rating]
        except ValueError:
            raise FileNameTypeError(
                f"Rating \[{rating}] is not a valid rating!"
            )

    def __format(self):
        return Config.file_name_delimiter.join(
            [
                self.__format_initials(),
                self.__format_date_time(),
                self.__format_sequence(),
                self.__format_style(),
                self.__format_rating(),
                self.__format_original()
            ]
        ) + self.__format_extension()

    def __format_initials(self):
        return self.__initials.upper()

    def __format_date_time(self):
        return self.__date_time

    def __format_sequence(self):
        return f"{self.__sequence:02d}"

    def __format_style(self):
        return f"S{self.__style.value:02d}"

    def __format_rating(self):
        return f"R{self.__rating.value:1d}"

    def __format_original(self):
        return self.__original

    def __format_extension(self):
        return f".{self.__extension}"

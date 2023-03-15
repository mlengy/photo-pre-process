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
        self.__style = style.value
        self.__rating = rating.value
        self.__original = original
        self.__changed = False
        self.__formatted = self.__format()

    def __str__(self):
        if self.__changed:
            self.__formatted = self.__format()
            self.__changed = False

        return self.__formatted

    def update_style(self, style: Style):
        self.__changed = True
        self.__style = style.value

    def update_rating(self, rating: Rating):
        self.__changed = True
        self.__rating = rating.value

    @staticmethod
    def from_string(string: str):
        chunks = FileName.__chunk_filename(string)

        initials = FileName.validate_initials(chunks[FileName.initials_index])
        date_time = FileName.__validate_date_time(chunks[FileName.date_time_index])
        sequence = FileName.__validate_sequence(chunks[FileName.sequence_index])
        style = FileName.__validate_style(chunks[FileName.style_index])
        rating = FileName.__validate_rating(chunks[FileName.rating_index])

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
    def validate_initials(initials: str):
        if not (initials.isalnum() and 1 < len(initials) <= 10):
            raise FileNameTypeError(f"Initials \[{initials}] is not valid!")
        else:
            return initials

    @staticmethod
    def __validate_date_time(date_time: str):
        try:
            datetime.strptime(date_time, Config.file_name_date_format)

            return date_time
        except ValueError:
            raise FileNameTypeError(f"Date time \[{date_time}] is not in format [{Config.file_name_date_format}]!")

    @staticmethod
    def __validate_sequence(sequence: str):
        try:
            return int(sequence)
        except ValueError:
            raise FileNameTypeError(f"Sequence \[{sequence}] is not a two digit number!")

    @staticmethod
    def __validate_style(style: str):
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
    def __validate_rating(rating: str):
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
        )

    def __format_initials(self):
        return self.__initials.upper()

    def __format_date_time(self):
        return self.__date_time

    def __format_sequence(self):
        return f"{self.__sequence:02d}"

    def __format_style(self):
        return f"S{self.__style:02d}"

    def __format_rating(self):
        return f"R{self.__rating:1d}"

    def __format_original(self):
        return self.__original

from entities.rating import Rating
from entities.style import Style


class FileName:
    delimiter = '-'

    def __init__(
            self,
            initials: str,
            datetime: str,
            sequence: int,
            original: str,
            style: Style = Style.none,
            rating: Rating = Rating.none
    ):
        self.__initials = initials
        self.__datetime = datetime
        self.__sequence = sequence
        self.__style = style.value
        self.__rating = rating.value
        self.__original = original
        self.__changed = False
        self.__formatted = self.__format()

    def __str__(self):
        if self.__changed:
            self.__formatted = self.__format()

        return self.__formatted

    def __format(self):
        return FileName.delimiter.join(
            [
                self.__format_initials(),
                self.__format_datetime(),
                self.__format_sequence(),
                self.__format_style(),
                self.__format_rating(),
                self.__format_original()
            ]
        )

    def __format_initials(self):
        return self.__initials.upper()

    def __format_datetime(self):
        return self.__datetime

    def __format_sequence(self):
        return f"{self.__sequence:02d}"

    def __format_style(self):
        return f"S{self.__style:02d}"

    def __format_rating(self):
        return f"R{self.__rating:1d}"

    def __format_original(self):
        return self.__original

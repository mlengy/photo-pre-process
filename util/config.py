from entities.rating import Rating
from entities.style import Style


class Config:
    exiftool_executable_path = "/usr/local/bin/exiftool"
    file_name_delimiter = '-'
    file_name_date_format = f"%Y%m%d{file_name_delimiter}%H%M%S"
    file_name_date_length = 15

    file_name_initials_default = "AA"
    file_name_date_default = "00000000-000000"
    file_name_sequence_default = "00"
    file_name_style_default = Style.none.name
    file_name_rating_default = Rating.none.name
    file_name_original_default = "ORIGINAL"

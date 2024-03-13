from entities.filename import FileName
from util.config import Config


class FilmRoll:
    def __init__(self, file_name_object: FileName):
        self.full_date = file_name_object.date_time,
        self.date = file_name_object.date_time.split(Config.file_name_delimiter)[0]
        self.film_types = set()
        self.cameras = set()
        self.lenses = set()

    def __hash__(self):
        return self.full_date

    def __eq__(self, other):
        if isinstance(other, FilmRoll):
            return self.full_date == other.full_date
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    @property
    def pretty_film_types(self):
        return sorted([f"{film_type[0]} {film_type[1]}".lower() for film_type in self.film_types])

    @property
    def pretty_cameras(self):
        return sorted([f"{camera[0]} {camera[1]}".lower() for camera in self.cameras])

    @property
    def pretty_lenses(self):
        return sorted([lens.lower() for lens in self.lenses])

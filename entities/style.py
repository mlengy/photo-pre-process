from enum import Enum


class Style(Enum):
    none = 00

    # nature
    nature = 10
    landscape = 11
    astro = 12
    flora = 13
    fauna = 14
    water = 15

    # still
    still = 20
    city = 21
    architecture = 22
    road = 23

    # people
    people = 30
    portrait = 31
    street = 32
    environmental = 33
    event = 34

    # other
    other = 90
    food = 91
    product = 92

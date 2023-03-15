from enum import Enum


class Style(Enum):
    none = 00

    # natural
    natural = 10
    landscape = 11
    astro = 12
    flora = 13
    fauna = 14
    water = 15

    # artificial
    artificial = 20
    city = 21
    architecture = 22
    transport = 23
    road = 24

    # people
    people = 30
    portrait = 31
    street = 32
    environmental = 33
    adventure = 34
    event = 35

    # other
    other = 90
    abstract = 91
    food = 92
    product = 93

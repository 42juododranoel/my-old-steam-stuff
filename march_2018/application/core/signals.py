from enum import IntEnum


class ItemSignals(IntEnum):
    OK = 0
    NEXT = 1
    DELETE = 2


class TrendSignals(IntEnum):
    DOWN = -1
    NO = 0
    UP = 1


class ExtremaSignals(IntEnum):
    MIN = -1
    NO = 0
    MAX = 1

from enum import Enum


class Channels(Enum):
    BOT_LOGS: int = 814152479100633128
    BOT_COMMANDS: int = 517651663729852416
    DEVSOC_ROOM: int = 892436503890915438


class Colours(Enum): ...


class Roles(Enum):
    SERVER_MUTE: int = 0
    DEVSOC: int = 0
    BOOSTER: int = 0
    ANNOUNCEMENT: int = 0

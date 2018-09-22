import pyquery as pq
from typing import *

class Platforms(Enum):
    STEAM = 1
    PS4 = 2
    XBOX = 3

class PlayerInfo(NamedTuple):
    name: str
    platform: Enum
    rank: str

class MatchInfo(NamedTuple):
    replay_url: str
    orange: List[PlayerInfo]
    blue: List[PlayerInfo]


def parse_match(div: pq.PyQuery) -> MatchInfo:
    pass 



doc = pq.PyQuery(url='http://ballchasing.org')

matches = doc('ul > li > .main')



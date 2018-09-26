import pyquery as pq
from typing import *
from datetime import datetime
import re
from enum import Enum
import functools

class VersusType(Enum):
    DUEL = 1
    DOUBLES = 2
    STANDARD = 3
    CHAOS = 4

    @staticmethod
    def is_versus(s: str) -> bool:
        regex = re.compile('\dv\d')
        return regex.match(s) is not None

    @staticmethod
    def from_str(s: str) -> bool:
        return VersusType(int(s[0] ))


class Platform(Enum):
    PS4 = 1
    XBOX = 2
    PC = 3

    @staticmethod
    def from_str(s: str):
        if s == "Steam":
            return Platform.PC
        elif s == "PS4":
            return Platform.PS4
        elif s == "XBox":
            return Platform.XBOX
        else:
            return None


class PlayerInfo(NamedTuple):
    id: str
    rank: Optional[str]
    platform: Platform


class MatchInfo(NamedTuple):
    id: str
    title: str
    blue_players: Set[PlayerInfo]
    orange_players: Set[PlayerInfo]
    game_type: str = None
    ranked: bool = None
    season: int = None
    versus_type: VersusType = None


def parse_div(div: pq.PyQuery) -> MatchInfo:
    title_div = div(".replay-title > a")
    tags_divs = div(".replay-meta .tag")
    blue_players_divs = div(".blue.team > .player")
    orange_players_divs = div(".orange.team > .player")
    
    title = title_div.html().strip()
    id = title_div.attr('href').replace('/replay/', '')
    parsed_tags : Dict = parse_tags(tags_divs)
    blue_players = set(blue_players_divs.map(parse_player))
    orange_players = set(orange_players_divs.map(parse_player))

    return MatchInfo(id=id, title=title, 
                     blue_players=blue_players,
                     orange_players=orange_players,
                     **parsed_tags)

def parse_tags(tags: pq.PyQuery):
    'Returns a dictionary with game_type, ranked, season'
    ret_dict = {}
    
    def read_tag(idx: int, tag_elem):
        tag = pq.PyQuery(tag_elem).text()
        if tag.find('Season') >= 0:
            ret_dict['season'] = int(tag.split(' ')[1])
        elif tag.lower().find('ranked') >= 0:
            ret_dict['game_type'] = tag.split(' ')[1]
            ret_dict['ranked'] = tag.find('Ranked') >= 0
        elif VersusType.is_versus(tag):
            ret_dict['versus_type'] = VersusType.from_str(tag)

    tags.map(read_tag)
    return ret_dict


def parse_player(idx: int, player_elem) -> PlayerInfo:
    player_div = pq.PyQuery(player_elem)
    platform = Platform.from_str(player_div(".player-platform").attr('title'))
    rank = player_div(".player-rank").attr("title")
    id = player_div.text()
    return PlayerInfo(id, rank, platform)

import pyquery as pq
import requests
from mypy_extensions import TypedDict
from typing import *
from datetime import datetime
import re
from enum import Enum
import functools
from ballchasing_downloader import ranks

date_fmt = '%Y-%m-%d %H:%M'
upload_date_re = re.compile('.* \(([\d\-: ]*)\)')
ballchasing_url_temp = 'https://ballchasing.com/?after={after_id}'

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
    rank: ranks.RLRank
    platform: Platform


class MatchInfo(NamedTuple):
    id: str
    title: str
    match_date: datetime
    upload_date: datetime
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
    match_date_div = div('.extra-info').children().filter(
        lambda i : pq.PyQuery(this).attr('title') == 'Date')
    upload_date_div = div('.uploader')
    

    match_date = datetime.strptime(match_date_div.text(), date_fmt)
    upload_date = datetime.strptime(
        upload_date_re.match(upload_date_div.text()).groups()[0],
        date_fmt)
    title = title_div.html().strip()
    id = title_div.attr('href').replace('/replay/', '')
    parsed_tags : Dict = parse_tags(tags_divs)
    blue_players = set(blue_players_divs.map(parse_player))
    orange_players = set(orange_players_divs.map(parse_player))

    return MatchInfo(id=id, title=title, 
                     match_date=match_date,
                     upload_date=upload_date,
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
    rank = ranks.RLRank.from_string(player_div(".player-rank").attr("title"))
    id = player_div.text()
    return PlayerInfo(id, rank, platform)


def retreive_infos(after_id='') -> List[MatchInfo]:
    resp = requests.get(ballchasing_url_temp.format(after_id=after_id))
    page = pq.PyQuery(resp.text)
    all_infos = page('.creplays > li').map(
        lambda i, x: parse_div(pq.PyQuery(x)))
    return all_infos

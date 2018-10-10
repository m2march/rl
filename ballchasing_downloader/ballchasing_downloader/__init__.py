import functools
from tinydb import TinyDB
import glob
import os
import re
import tempfile
from datetime import datetime
from enum import Enum
from typing import *

import carball
import pandas as pd
import pyquery as pq
from carball.analysis.analysis_manager import AnalysisManager
from carball.analysis.utils import pandas_manager
from carball.json_parser.game import Game

import requests
from ballchasing_downloader import ranks

date_fmt = '%Y-%m-%d %H:%M'
upload_date_re = re.compile('.* \(([\d\-: ]*)\)')
ballchasing_url_temp = 'https://ballchasing.com/?after={after_id}'
ballchasing_dl_url = 'https://ballchasing.com/dl/replay/{id}'

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
            try:
                ret_dict['season'] = int(tag.split(' ')[1])
            except Exception as e:
                print('Error while parsing season from text: {}'.format(tag))
        elif tag.lower().find('ranked') >= 0:
            try:
                ret_dict['game_type'] = tag.split(' ')[1]
                ret_dict['ranked'] = tag.find('Ranked') >= 0
            except Exception as e:
                print('Error while parsing if ranked from text: {}'.format(tag))
        elif VersusType.is_versus(tag):
            try:
                ret_dict['versus_type'] = VersusType.from_str(tag)
            except Exception as e:
                print('Error while parsing versus from text: {}'.format(tag))

    tags.map(read_tag)
    return ret_dict

def parse_player(idx: int, player_elem) -> PlayerInfo:
    player_div = pq.PyQuery(player_elem)
    platform = Platform.from_str(player_div(".player-platform").attr('title'))
    try:
        rank = ranks.RLRank.from_string(
            player_div(".player-rank").attr("title"))
    except ranks.RankParsingError as rpe:
        print(rpe)
        rank = ranks.Unranked()
    id = player_div.text()
    return PlayerInfo(id, rank, platform)


def retreive_infos(after_id='') -> List[MatchInfo]:
    resp = requests.get(ballchasing_url_temp.format(after_id=after_id))
    page = pq.PyQuery(resp.text)
    all_infos = page('.creplays > li').map(
        lambda i, x: parse_div(pq.PyQuery(x)))
    return all_infos


def download_replay(id: str, out_folder: str) -> str:
    'Downloads the replay and returns the path to the replay file'
    resp = requests.get(ballchasing_dl_url.format(id=id))
    replay_path = os.path.join(out_folder, '{}.replay'.format(id))
    with open(os.path.join(out_folder, '{}.replay'.format(id)), 'wb') as f:
        f.write(resp.content)
    return replay_path


def convert_replay(replay_path: str, out_folder: str) -> Dict:
    '''
    Parses the replay file intro proto and pandas. 
    
    Returns a dictionary with keys ['proto', 'pandas'] with the paths
    to each file.
    '''
    id = os.path.splitext(os.path.basename(replay_path))[0]
    proto_path = os.path.join(out_folder, '{}.pts'.format(id))
    pandas_path = os.path.join(out_folder, '{}.gzip'.format(id))

    temp_path = tempfile.mktemp(suffix='.json')

    _json = carball.decompile_replay(replay_path, temp_path)

    game = Game()
    game.initialize(loaded_json=_json)
    analysis = AnalysisManager(game)
    analysis.create_analysis()

    with open(proto_path, 'wb') as f:
        analysis.write_proto_out_to_file(f)

    with open(pandas_path, 'wb') as f:
        analysis.write_pandas_out_to_file(f)

    return {
        'proto': proto_path,
        'pandas': pandas_path
    }


def open_proto(proto_path: str) -> carball.generated.api.game_pb2.Game:
    with open(proto_path, 'rb') as f:
        game = carball.generated.api.game_pb2.Game()
        game.ParseFromString(f.read())

    return game


def open_pandas(pandas_path: str) -> pd.DataFrame:
    with open(pandas_path, 'rb') as f:
        data_frame = pandas_manager.PandasManager.read_numpy_from_memory(f)
    return data_frame


def downloaded_ids(downloads_path) -> Set[str]:
    dl_ids = {
        os.path.splitext(os.path.basename(filepath))[0]
        for filepath in glob.glob(os.path.join(downloads_path, '*.replay'))
    }
    return dl_ids 


def converted_ids(converted_path) -> Set[str]:
    conv_ids = {
        os.path.splitext(os.path.basename(filepath))[0]
        for filepath in glob.glob(os.path.join(converted_path, '*.gzip'))
        if os.path.isfile(filepath.replace('gzip', 'pts'))
    }
    return conv_ids


def filter_downloaded_ids(downloads_path, db_path) -> List[str]:
    dl_ids = downloaded_ids(downloads_path)

    db = TinyDB(db_path)
    db_ids = {d['id'] for d in db.all()}

    return db_ids - dl_ids 


def filter_converted_ids(replays_path, converted_path) -> List[str]:
    dl_ids = downloaded_ids(replays_path)
    conv_ids = converted_ids(converted_path)

    return dl_ids - conv_ids

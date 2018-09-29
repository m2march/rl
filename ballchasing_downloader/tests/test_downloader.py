import pytest
import os
import json
from ballchasing_downloader import *
from ballchasing_downloader.ranks import * 
from ballchasing_downloader import mapper
import pyquery as pq

class ParsedDiv(NamedTuple):
    div: str
    info: MatchInfo

def full_2v2_div() -> ParsedDiv:
    with open(os.path.join(os.path.dirname(__file__), 
                           'full_2v2_div.html')) as f:
        div = f.read()

    info = MatchInfo(
        id = "83eb6a0f-6729-4ef1-ba89-5576ca876aa1",
        title = "90",
        versus_type = VersusType.DOUBLES,
        game_type = 'Doubles',
        match_date = datetime.strptime('2018-09-21 15:15', date_fmt),
        upload_date = datetime(2018, 9, 26, 23, 40),
        ranked = True,
        season = 8,
        blue_players = {
            PlayerInfo('TankDS', NumericRank(Category.Champion, 1, 3), Platform.PC),
            PlayerInfo('Thorgrim102', Unranked(), Platform.PC),
        },
        orange_players = {
            PlayerInfo('Pasi', NumericRank(Category.Champion, 1, 3), Platform.PC),
            PlayerInfo('Gonzo', NumericRank(Category.Champion, 2, 1), Platform.PC)
        }
    )
    return ParsedDiv(div, info)

def unranked_4v4_div() -> ParsedDiv:
    with open(os.path.join(os.path.dirname(__file__),
                           'unranked_4v4_div.html')) as f:
        div = f.read()

    info = MatchInfo(
        id = '23c4c1a1-659a-453a-9fd8-0948b17d9303',
        title = 'FE25414145E807674CA5C9AA9254AD58',
        versus_type = VersusType.CHAOS,
        game_type = 'Chaos',
        match_date = datetime.strptime('2018-08-31 23:14', date_fmt),
        upload_date = datetime(2018, 9, 27, 2, 51),
        ranked = False,
        season = 8,
        blue_players = {
            PlayerInfo('digger_hero | hellcase.com', Unranked(), Platform.PC),
            PlayerInfo('KK_Ultra_14', Unranked(), Platform.PC),
            PlayerInfo('danny_2604', Unranked(), Platform.PC),
            PlayerInfo('basti_2411', Unranked(), Platform.PC)
        },
        orange_players = {
            PlayerInfo('Element', Unranked(), Platform.PC),
            PlayerInfo('To Wcale Nie Kenny', Unranked(), Platform.PC),
            PlayerInfo('Koov1', Unranked(), Platform.PC),
            PlayerInfo('Locowsky', Unranked(), Platform.PC)
        }
    )
    return ParsedDiv(div, info)

parsed_divs = [full_2v2_div(), unranked_4v4_div()]
parsed_divs_ids = ['full', 'unranked']

@pytest.mark.parametrize('pd', parsed_divs, ids=parsed_divs_ids)
def test_parse_div(pd: ParsedDiv):
    assert parse_div(pq.PyQuery(pd.div)) == pd.info


def test_match_info_to_json():
    mi = MatchInfo(id='id', title='title', 
                   versus_type=VersusType.DOUBLES,
                   game_type='type',
                   match_date = datetime.now(),
                   upload_date = datetime.now(),
                   ranked=True, season=8,
                   blue_players={PlayerInfo('p1', None, Platform.PS4)},
                   orange_players={PlayerInfo('p2', None, Platform.PS4)})
    d = mapper.named_tuple_to_dict(mi) 
    assert mi == mapper.parse_nt(d, MatchInfo)

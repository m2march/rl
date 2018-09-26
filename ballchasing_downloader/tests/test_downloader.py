import pytest
import os
from ballchasing_downloader import *
import pyquery as pq

class ParsedDiv(NamedTuple):
    div: str
    info: MatchInfo

@pytest.fixture
def full_2v2_div() -> ParsedDiv:
    with open(os.path.join(os.path.dirname(__file__), 
                           'full_2v2_div.html')) as f:
        div = f.read()

    info = MatchInfo(
        id = "83eb6a0f-6729-4ef1-ba89-5576ca876aa1",
        title = "90",
        versus_type = VersusType.DOUBLES,
        game_type = 'Doubles',
        ranked = True,
        season = 8,
        blue_players = {
            PlayerInfo('TankDS', 'Champion I Division 3', Platform.PC),
            PlayerInfo('Thorgrim102', 'Unranked', Platform.PC),
        },
        orange_players = {
            PlayerInfo('Pasi', 'Champion I Division 3', Platform.PC),
            PlayerInfo('Gonzo', 'Champion II Division 1', Platform.PC)
        }
    )
    return ParsedDiv(div, info)


def test_parse_div(full_2v2_div: ParsedDiv):
    assert parse_div(pq.PyQuery(full_2v2_div.div)) == full_2v2_div.info

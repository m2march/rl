import enum
from typing import *
import re

cat_inverse = {
    'Bronze': 1,
    'Silver': 2,
    'Gold': 3,
    'Platinum': 4,
    'Diamond': 5,
    'Champion': 6,
    'Grand Champion': 7,
}

class Category(enum.Enum):
    Bronze = 1
    Silver = 2
    Gold = 3
    Platinum = 4
    Diamond = 5
    Champion = 6
    GrandChampion = 7
        

    @staticmethod
    def from_string(text: str):
        return Category(cat_inverse[text])


class RLRank:

    @staticmethod
    def from_string(text: Optional[str]):
        if text is None or text.lower() == 'unranked':
            return Unranked()
        else:
            return NumericRank.from_string(text)

    def __lt__(self, o):
        return self.__cmp__(o) < 0
    
    def __le__(self, o):
        return self.__cmp__(o) <= 0

    def __gt__(self, o):
        return self.__cmp__(o) > 0
    
    def __ge__(self, o):
        return self.__cmp__(o) >= 0

    def __hash__(self):
        return self.__repr__()


class Unranked(RLRank):

    def __cmp__(self, o):
        raise UnrankedComparisonError()

    def __eq__(self, o):
        if isinstance(o, Unranked):
            return True
        else:
            return False
    
    def __nq__(self, o):
        return not self.__eq_(o)

    def __hash__(self):
        return self.__repr__().__hash__()

    def __repr__(self):
        return 'Unranked'

class NumericRank(RLRank):

    def __init__(self, category, subcategory, division):
        self.category = Category(category)
        self.subcategory = subcategory
        self.division = division

    @staticmethod
    def __count_i(text: str, ):
        if (re.match('I+', text) is None):
            raise RankParsingError('Invalid I+ text: {}'.format(text))
        if (len(text) not in [1, 2, 3]):
            raise RankParsingError('Invalid I count: {}'.format(text))
        return len(text)

    @staticmethod
    def from_string(text: str):
        if text == 'Grand Champion':
            return NumericRank(Category.GrandChampion, 1, 1)

        cat_text, sub_text, _, div_text = text.split(' ')
        category = Category.from_string(cat_text)
        subcategory = NumericRank.__count_i(sub_text)
        division = int(div_text)
        return NumericRank(category, subcategory, division)


    def __repr__(self):
        return '<RLRank: {} {} div {}>'.format(self.category.name,
                                               self.subcategory,
                                               self.division)

    def __as_tuple(self) -> List[int]:
        return (self.category.value, self.subcategory, self.division)

    def __cmp__(self, o):
        if isinstance(o, Unranked):
            raise UnrankedComparisonError()

        if (self.__as_tuple() < o.__as_tuple()):
            return -1
        elif (self.__as_tuple() == o.__as_tuple()):
            return 0
        else:
            return 1

    def __hash__(self):
        return self.__repr__().__hash__()

    def __eq__(self, o):
        if isinstance(o, Unranked):
            return False
        return self.__cmp__(o) == 0
    
    def __nq__(self, o):
        if isinstance(o, Unranked):
            return False
        return self.__cmp__(o) != 0


class RankParsingError(ValueError):
    pass


class UnrankedComparisonError(TypeError):

    def __init__(self):
        TypeError.__init__(self, 'Unranked rank cannot be compared')

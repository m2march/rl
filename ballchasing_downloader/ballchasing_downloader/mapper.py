import typing as ty
from ballchasing_downloader import ranks
import datetime
import collections
import enum
import json

def named_tuple_to_dict(obj):
        # Proxy to isinstance(obj, NamedTuple)
        if '__annotations__' in dir(obj): 
            obj = dict(zip(obj.__annotations__.keys(), obj))
            for key, val in obj.items():
                obj[key] = named_tuple_to_dict(val)
            return obj
        if isinstance(obj, datetime.datetime):
            return obj.timestamp()
        if isinstance(obj, str):
            return obj
        if isinstance(obj, collections.Iterable):
            return list([named_tuple_to_dict(x) for x in obj])
        if isinstance(obj, enum.Enum):
            return obj.value
        if isinstance(obj, ranks.RLRank):
            return obj.__repr__()
        return obj

class NamedTupleEncoder(json.JSONEncoder):

    def encode(self, obj):
        return json.JSONEncoder.encode(self, self.named_tuple_to_dict(obj))


def parse_nt(d, cls):
    if cls in [int, float, str, bool]:
        return d
    elif '__origin__' in dir(cls):
        if cls.__origin__ is ty.Union:
            return parse_nt(d, cls.__args__[0])
        elif issubclass(cls, ty.Set):
            return set([parse_nt(x, cls.__args__[0]) for x in d])
        elif issubclass(cls, collections.Iterable):
            return [parse_nt(x, cls.__args__[0]) for x in d]
    elif issubclass(cls, enum.Enum):
        return cls(d)
    elif cls is datetime.datetime:
        return datetime.datetime.fromtimestamp(d)
    elif '__annotations__' in dir(cls):
        if not isinstance(d, dict):
            raise TupleDecodingError(('Required attribute {} not found in '
                                      'object {}').format(key, obj))
        hints = ty.get_type_hints(cls)
        return cls(**{key: parse_nt(d[key], sub_cls)
                      for key, sub_cls in hints.items()})
    elif issubclass(cls, ranks.RLRank):
        return ranks.RLRank.from_string(d)
    return d

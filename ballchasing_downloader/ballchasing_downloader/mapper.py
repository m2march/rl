import typing as ty
import datetime
import collections
import enum
import json

class TupleDecodingError(TypeError):
    pass

class NamedTupleEncoder(json.JSONEncoder):

    def named_tuple_to_dict(self, nt):
        return dict(zip(nt.__annotations__.keys(), nt))

    def to_dict(self, obj):
        # Proxy to isinstance(obj, NamedTuple)
        if '__annotations__' in dir(obj): 
            obj = self.named_tuple_to_dict(obj)
            for key, val in obj.items():
                obj[key] = self.to_dict(val)
            return obj
        if isinstance(obj, datetime.datetime):
            return obj.timestamp()
        if isinstance(obj, str):
            return obj
        if isinstance(obj, collections.Iterable):
            return list([self.to_dict(x) for x in obj])
        if isinstance(obj, enum.Enum):
            return obj.value
        return obj

    def encode(self, obj):
        return json.JSONEncoder.encode(self, self.to_dict(obj))


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
    return d

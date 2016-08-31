import unittest
import collections

from pypeg2 import parse, Symbol

def recursive_to_dict(obj):
    if issubclass(type(obj), Symbol):
        return obj

    if type(obj) is collections.OrderedDict:
        obj = list(dict(obj).values())

    if type(obj) is list:
        return [recursive_to_dict(o) for o in obj]
    
    if not hasattr(obj, '__dict__'):
        return obj

    obj = obj.__dict__
    for key, value in obj.items():
        obj[key] = recursive_to_dict(value)

    return obj


def recursive_del(obj, attr, condition=None):
    if type(obj) is list:
        return [recursive_del(o, attr) for o in obj]
    if type(obj) not in [dict, collections.OrderedDict]:
        return obj

    if attr in obj:
        if condition is None or condition(obj[attr]):
            del obj[attr]

    for key, value in obj.items():
        obj[key] = recursive_del(value, attr)

    return obj


class ParserTest(unittest.TestCase):
    maxDiff = None

    def assert_parse_equal(self, code, expected, obj=None):
        if obj is None:
            obj = self.test_obj

        actual = parse(code, obj)
        actual = recursive_to_dict(actual)
        actual = recursive_del(actual, 'position_in_text')
        actual = recursive_del(actual, 'data')

        self.assertDictEqual(actual, expected)


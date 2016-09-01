import unittest
import collections

from pypeg2 import parse, Symbol, Namespace
from grammar import *

def recursive_to_dict(obj):
    if issubclass(type(obj), Symbol):
        return obj

    if type(obj) is Definitions:
        return [recursive_to_dict(o) for o in obj]

    elif type(obj) in [ExternalEnum, InternalEnum]:
        res = obj.__dict__
        res['enum_entries'] = list(map(recursive_to_dict, obj.data.values()))
        del res['data']
        del res['position_in_text']

    elif type(obj) in [ExternalEnumEntry, InternalEnumEntry]:
        res = obj.__dict__
        del res['namespace']
        del res['position_in_text']

    elif type(obj) is ScalarField:
        res = obj.__dict__
        del res['position_in_text']

    elif type(obj) is NamedStructure:
        res = obj.__dict__
        res['fields'] = list(map(recursive_to_dict, list(obj.data.values())[0]))
        del res['data']
        del res['position_in_text']

        if 'structure_variant' in res:
            res['structure_variant'] = recursive_to_dict(res['structure_variant'])

    elif type(obj) is UnnamedStructure:
        res = obj.__dict__

        if 'cryptographic_attribute' in res:
            res['fields'] = list(map(recursive_to_dict, list(obj.data.values())[0]))
        else:
            res['fields'] = list(map(recursive_to_dict, list(obj.data.values())))
        del res['data']
        del res['position_in_text']

        if 'structure_variant' in res:
            res['structure_variant'] = recursive_to_dict(res['structure_variant'])

        for i, o in enumerate(res['fields']):
            if type(o) is dict and 'namespace' in o:
                o.pop('namespace')
            elif type(o) is list:
                res[i] = recursive_to_dict(o)

    elif type(obj) is VariableVectorField:
        res = obj.__dict__
        res['vector_bounds'] = recursive_to_dict(res['vector_bounds'])
        del res['position_in_text']


    elif type(obj) is Variant:
        res = obj.__dict__
        res['variant_cases'] = list(map(recursive_to_dict, res['variant_cases']))
        del res['data']
        del res['position_in_text']

    else:
        res = obj.__dict__
        del res['position_in_text']

    return res


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

        if type(expected) is list:
            self.assertListEqual(actual, expected)
        else:
            self.assertDictEqual(actual, expected)


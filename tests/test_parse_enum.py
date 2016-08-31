from pypeg2 import Symbol

from grammar import InternalEnum, ExternalEnum, Int
from tests.parser_test import ParserTest

class ParseExternalEnumTest(ParserTest):
    test_obj = ExternalEnum

    def test_external_enum_without_width(self):
        'Section 4.5.  Enumerateds'
        expected = {
            'name':        Symbol('Color'),
            'enum_entries': [{'name': Symbol('red'),   'value': Int('3')},
                             {'name': Symbol('blue'),  'value': Int('5')},
                             {'name': Symbol('white'), 'value': Int('7')}],
        }
        code = 'enum { red(3), blue(5), white(7) } Color;'

        self.assert_parse_equal(code, expected)


    def test_external_enum_with_width(self):
        'Section 4.5.  Enumerateds'
        expected = {
            'name':        Symbol('Taste'),
            'enum_entries': [{'name': Symbol('sweet'),  'value': Int('1')},
                             {'name': Symbol('sour'),   'value': Int('2')},
                             {'name': Symbol('bitter'), 'value': Int('4')}],
            'enum_width': Int('32000'),
        }
        code = 'enum { sweet(1), sour(2), bitter(4), (32000) } Taste;'

        self.assert_parse_equal(code, expected)


class ParseInternalEnumTest(ParserTest):
    test_obj = InternalEnum

    def test_internal_enum(self):
        'Section 4.5.  Enumerateds'
        expected = {
            'name':        Symbol('Amount'),
            'enum_entries': [{'name': Symbol('low')},
                             {'name': Symbol('medium')},
                             {'name': Symbol('high')}],
        }
        code = 'enum { low, medium, high } Amount;'

        self.assert_parse_equal(code, expected)


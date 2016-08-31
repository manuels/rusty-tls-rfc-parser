from pypeg2 import Symbol

from grammar import NamedStructure, UnnamedStructure, Type, Int
from tests.parser_test import ParserTest

class ParseNamedStructureTest(ParserTest):
    test_obj = NamedStructure

    def test_named_struct(self):
        '4.6.  Constructed Types'
        expected = {
            'name':        Symbol('T'),
            'structure_fields': [
                {'name': 'f1', 'type': 'T1'},
                {'name': 'f2', 'type': 'T2'},
                {'name': 'fn', 'type': 'Tn'},
            ]
        }
        code = '''struct {
          T1 f1;
          T2 f2;
          Tn fn;
        } T;'''

        self.assert_parse_equal(code, expected)


class ParseUnnamedStructureTest(ParserTest):
    test_obj = UnnamedStructure

    def test_anonymous_struct(self):
        '4.6.  Constructed Types'
        expected = {
            'structure_fields': [
                {'name': 'f1', 'type': 'T1'},
                {'name': 'f2', 'type': 'T2'},
                {'name': 'fn', 'type': 'Tn'},
            ]
        }
        code = '''struct {
          T1 f1;
          T2 f2;
          Tn fn;
        };'''

        self.assert_parse_equal(code, expected)


    def test_empty_anonymous_struct(self):
        'A.4.1.  Hello Messages'
        expected = {
            'structure_fields': []
        }
        code = 'struct {};'

        self.assert_parse_equal(code, expected)


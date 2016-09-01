from pypeg2 import Symbol

from grammar import NamedStructure, UnnamedStructure, Type, Int, CryptographicAttribute
from tests.parser_test import ParserTest

class ParseCryptographicAttributesTest(ParserTest):
    def test_unnamed_struct(self):
        '4.7.  Cryptographic Attributes'
        expected = {
            'cryptographic_attribute': CryptographicAttribute('digitally-signed'),
            'fields': [
                {'name': Symbol('field3'),
                 'vector_bounds': {'floor': Int('0'), 'ceiling': Int('255')},
                 'vector_type': Type('uint8')},
                {'name': Symbol('field4'), 'type': Type('uint8')},
            ]
        }
        code = '''
              digitally-signed struct {
                uint8 field3<0..255>;
                uint8 field4;
              };
        '''
        # TODO was 'digitally-signed opaque' but is probably an erratum and
        # should be 'digitally-signed struct'

        self.assert_parse_equal(code, expected, UnnamedStructure)

    def test_named_struct(self):
        '4.7.  Cryptographic Attributes'
        expected = {
            'name':                    Symbol('UserType'),
            'cryptographic_attribute': CryptographicAttribute('stream-ciphered'),
            'fields': [
                {'name': Symbol('field1'), 'type': Type('uint8')},
                {'name': Symbol('field2'), 'type': Type('uint8')},
                {
                    'cryptographic_attribute': CryptographicAttribute('digitally-signed'),
                    'fields': [
                        {'name': Symbol('field3'),
                         'vector_bounds': {'floor': Int('0'), 'ceiling': Int('255')},
                         'vector_type': Type('uint8')},
                        {'name': Symbol('field4'), 'type': Type('uint8')},
                    ]
                }
            ]
        }
        code = '''
          stream-ciphered struct {
              uint8 field1;
              uint8 field2;
              digitally-signed struct {
                uint8 field3<0..255>;
                uint8 field4;
              };
          } UserType;
        '''
        # TODO was 'digitally-signed opaque' but is probably an erratum and
        # should be 'digitally-signed struct'

        self.assert_parse_equal(code, expected, NamedStructure)


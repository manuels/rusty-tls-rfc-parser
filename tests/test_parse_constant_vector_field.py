from pypeg2 import Symbol

from grammar import ConstantVectorField, Type, Int
from tests.parser_test import ParserTest

class ParseConstantVectorFieldTest(ParserTest):
    test_obj = ConstantVectorField

    def test_constant_uint8_vector(self):
        expected = {
            'name':        Symbol('Data'),
            'vector_size': Int('3'),
            'vector_type': Type('uint8')
        }
        code = 'uint8 Data[3];'

        self.assert_parse_equal(code, expected)


    def test_constant_custom_type_vector(self):
        '''Section 4.3 Vectors'''
        expected = {
            'name':        Symbol('Data'),
            'vector_size': Int('9'),
            'vector_type': Type('Datum')
        }
        code = 'Datum Data[9];'
        self.assert_parse_equal(code, expected)


    def test_constant_opaque_vector(self):
        '''Section 4.3 Vectors'''
        expected = {
            'name':        Symbol('Datum'),
            'vector_size': Int('3'),
            'vector_type': Type('opaque')
        }
        code = 'opaque Datum[3];'
        self.assert_parse_equal(code, expected)


    def test_constant_ints_vector(self):
        '''
        Section 4.4. Numbers
        uint8 uint16[2];
        uint8 uint24[3];
        uint8 uint32[4];
        uint8 uint64[8];
        '''
        for i, name in zip([2,3,4,8], ['uint16', 'uint24', 'uint32', 'uint64']):
            expected = {
                'name':        Symbol(name),
                'vector_size': Int(str(i)),
                'vector_type': Type('uint8')
            }
            code = 'uint8 {}[{}];'.format(name, i)
            self.assert_parse_equal(code, expected)


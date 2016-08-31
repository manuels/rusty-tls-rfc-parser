from pypeg2 import Symbol

from grammar import VariableVectorField, VariableVectorBounds, Type, Int
from tests.parser_test import ParserTest

class ParseVariableVectorFieldTest(ParserTest):
    test_obj = VariableVectorField

    def test_variable_uint8_vector(self):
        expected = {
            'name':        Symbol('Data'),
            'vector_type': Type('uint8'),
            'vector_bounds': {
                'floor':       Int('3'),
                'ceiling':     Int('10'),
            },
        }
        code = 'uint8 Data<3..10>;'

        self.assert_parse_equal(code, expected)


    def test_variable_opaque_vector(self):
        'Section 4.3. Vectors'
        expected = {
            'name':        Symbol('mandatory'),
            'vector_type': Type('opaque'),
            'vector_bounds': {
                'floor':       Int('300'),
                'ceiling':     Int('400'),
            },
        }
        code = 'opaque mandatory<300..400>;'

        self.assert_parse_equal(code, expected)


    def test_variable_int16_vector(self):
        'Section 4.3. Vectors'
        expected = {
            'name':        Symbol('longer'),
            'vector_type': Type('uint16'),
            'vector_bounds': {
                'floor':       Int('0'),
                'ceiling':     Int('800'),
            },
        }
        code = 'uint16 longer<0..800>;'

        self.assert_parse_equal(code, expected)


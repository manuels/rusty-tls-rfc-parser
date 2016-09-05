import unittest

import pypeg2

from tests.parser_test import recursive_to_dict

from grammar import Definitions
from rust_compiler import compile_packet_representation

class RustCompilerTest(unittest.TestCase):
    maxDiff = None

    def test_named_struct(self):
        '4.6.  Constructed Types'
        input_code = '''struct {
          T1 f1;
          T2 f2;
          Tn fn;
        } T;'''

        expected_code = '''struct T {
    f1: T1,
    f2: T2,
    fn: Tn,
}'''

        ast = pypeg2.parse(input_code, Definitions)
        actual_code = compile_packet_representation(ast)

        self.assertEqual(expected_code, actual_code)


    def test_external_enum(self):
        'Section 4.5.  Enumerateds'
        input_code = 'enum { red(3), blue(5), white(7) } Color;'

        expected_code = '''enum Color {
    red = 3,
    blue = 5,
    white = 7,
}'''

        ast = pypeg2.parse(input_code, Definitions)
        actual_code = compile_packet_representation(ast)

        self.assertEqual(expected_code, actual_code)


    def test_internal_enum(self):
        'Section 4.5.  Enumerateds'
        input_code = 'enum { low, medium, high } Amount;'

        expected_code = '''enum Amount {
    low,
    medium,
    high,
}'''

        ast = pypeg2.parse(input_code, Definitions)
        actual_code = compile_packet_representation(ast)

        self.assertEqual(expected_code, actual_code)

    def test_opaque_constant_vector_field(self):
        '''Section 4.3 Vectors'''
        input_code = 'opaque Datum[3];'
        expected_code = 'Datum: u8[3]'

        ast = pypeg2.parse(input_code, Definitions)
        actual_code = compile_packet_representation(ast)

        self.assertEqual(expected_code, actual_code)


    def test_constant_vector_field(self):
        '''Section 4.3 Vectors (see errata)'''
        input_code = 'Datum Data[3];'
        expected_code = 'Data: Datum[3]'

        ast = pypeg2.parse(input_code, Definitions)
        actual_code = compile_packet_representation(ast)

        self.assertEqual(expected_code, actual_code)


    def test_variable_uint8_vector(self):
        input_code = 'uint8 Data<3..10>;'
        expected_code = 'Data: Vec<u8>'

        ast = pypeg2.parse(input_code, Definitions)
        actual_code = compile_packet_representation(ast)

        self.assertEqual(expected_code, actual_code)


    def test_variable_opaque_vector(self):
        'Section 4.3. Vectors'
        input_code = 'opaque mandatory<300..400>;'
        expected_code = 'mandatory: Vec<u8>'

        ast = pypeg2.parse(input_code, Definitions)
        actual_code = compile_packet_representation(ast)

        self.assertEqual(expected_code, actual_code)


    def test_variable_int16_vector(self):
        'Section 4.3. Vectors'
        input_code = 'uint16 longer<0..800>;'
        expected_code = 'longer: Vec<u16>'

        ast = pypeg2.parse(input_code, Definitions)
        actual_code = compile_packet_representation(ast)

        self.assertEqual(expected_code, actual_code)


    def test_variant_empty_struct(self):
        '4.6.1.  Variants'
        input_code = '''struct {
          select (VariantTag) {
              case apple:
                V1;
              case orange:
              case banana:
                V2;
          } variant_body;
        } VariantRecord;'''
        expected_code = '''enum VariantRecordVariant {
    apple(V1),
    orange(V2),
    banana(V2),
}

struct VariantRecord {
    variant_body: VariantRecordVariant,
}'''

        ast = pypeg2.parse(input_code, Definitions)
        actual_code = compile_packet_representation(ast)

        self.assertEqual(expected_code, actual_code)


    def test_variant_struct(self):
        '7.4.  Handshake Protocol'
        input_code = '''
          struct {
              HandshakeType msg_type;
              uint24 length;
              select (HandshakeType) {
                  case hello_request:       HelloRequest;
                  case client_hello:        ClientHello;
                  case server_hello:        ServerHello;
                  case certificate:         Certificate;
                  case server_key_exchange: ServerKeyExchange;
                  case certificate_request: CertificateRequest;
                  case server_hello_done:   ServerHelloDone;
                  case certificate_verify:  CertificateVerify;
                  case client_key_exchange: ClientKeyExchange;
                  case finished:            Finished;
              } body;
          } Handshake;
        '''
        expected_code = '''enum HandshakeVariant {
    hello_request(HelloRequest),
    client_hello(ClientHello),
    server_hello(ServerHello),
    certificate(Certificate),
    server_key_exchange(ServerKeyExchange),
    certificate_request(CertificateRequest),
    server_hello_done(ServerHelloDone),
    certificate_verify(CertificateVerify),
    client_key_exchange(ClientKeyExchange),
    finished(Finished),
}

struct Handshake {
    msg_type: HandshakeType,
    length: u24,
    body: HandshakeVariant,
}'''

        ast = pypeg2.parse(input_code, Definitions)
        actual_code = compile_packet_representation(ast)

        self.assertEqual(expected_code, actual_code)


    def test_unnamed_crypto_struct(self):
        '4.7.  Cryptographic Attributes'
        input_code = '''
              digitally-signed struct {
                uint8 field3<0..255>;
                uint8 field4;
              };
        '''
        # TODO was 'digitally-signed opaque' but is probably an erratum and
        # should be 'digitally-signed struct'
        expected_code = '''struct Signed {
    field3: Vec<u8>,
    field4: u8,
}'''

        ast = pypeg2.parse(input_code, Definitions)
        actual_code = compile_packet_representation(ast, in_named_structure=True)

        self.assertEqual(expected_code, actual_code)


    def test_named_crypto_struct(self):
        '4.7.  Cryptographic Attributes'
        input_code = '''
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
        expected_code = '''struct UserTypeSigned {
    field3: Vec<u8>,
    field4: u8,
}

struct UserType {
    field1: u8,
    field2: u8,
    signed: DigitallySigned<UserTypeSigned>,
}'''

        ast = pypeg2.parse(input_code, Definitions)
        actual_code = compile_packet_representation(ast)

        self.assertEqual(expected_code, actual_code)


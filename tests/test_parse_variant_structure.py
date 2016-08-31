from pypeg2 import Symbol

from grammar import NamedStructure, Type, Int
from tests.parser_test import ParserTest

class ParseNamedVariantStructureTest(ParserTest):
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


    def test_variant_empty_struct(self):
        '4.6.1.  Variants'
        expected = {
            'name':        Symbol('VariantRecord'),
            'structure_variant': {
                'name': Symbol('variant_body'),
                'variant_type': Type('VariantTag'),
                'variant_cases': [
                    {
                      'cases': [Symbol('apple')],
                      'type': Type('V1')
                    },
                    {
                      'cases': [Symbol('orange'), Symbol('banana')],
                      'type':  Type('V2')
                    },
                ]
            }
        }
        code = '''struct {
          select (VariantTag) {
              case apple:
                V1;
              case orange:
              case banana:
                V2;
          } variant_body;
        } VariantRecord;'''

        self.assert_parse_equal(code, expected)


    def test_variant_struct(self):
        '7.4.  Handshake Protocol'
        expected = {
            'name':        Symbol('Handshake'),
            'structure_fields': [{
                'name': 'msg_type',
                'type': 'HandshakeType',
            },{
                'name': 'length',
                'type': 'uint24',
            }
            ],
            'structure_variant': {
                'name': Symbol('body'),
                'variant_type': Type('HandshakeType'),
                'variant_cases': [
                    {
                      'cases': [Symbol('hello_request')],
                      'type': Type('HelloRequest'),
                    }, {
                      'cases': [Symbol('client_hello')],
                      'type':  Type('ClientHello'),
                    }, {
                      'cases': [Symbol('server_hello')],
                      'type':  Type('ServerHello'),
                    }, {
                      'cases': [Symbol('certificate')],
                      'type':  Type('Certificate'),
                    }, {
                      'cases': [Symbol('server_key_exchange')],
                      'type':  Type('ServerKeyExchange'),
                    }, {
                      'cases': [Symbol('certificate_request')],
                      'type':  Type('CertificateRequest'),
                    }, {
                      'cases': [Symbol('server_hello_done')],
                      'type':  Type('ServerHelloDone'),
                    }, {
                      'cases': [Symbol('certificate_verify')],
                      'type':  Type('CertificateVerify'),
                    }, {
                      'cases': [Symbol('client_key_exchange')],
                      'type':  Type('ClientKeyExchange'),
                    }, {
                      'cases': [Symbol('finished')],
                      'type':  Type('Finished'),
                    },
                ]
            }
        }
        code = '''
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

        self.assert_parse_equal(code, expected)


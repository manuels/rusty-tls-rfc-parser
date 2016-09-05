import collections
import itertools

from grammar import *

implicit_types = {
    'uint8': {
        'size': 1,
        'rust_type': 'u8',
    },
    'opaque': {
        'size': 1,
        'rust_type': 'u8',
    },
    'uint16': {
        'size': 2,
        'rust_type': 'u16',
    },
    'uint24': {
        'size': 3,
        'rust_type': 'u24',
    },
    'uint32': {
        'size': 4,
        'rust_type': 'u32',
    },
    'uint64': {
        'size': 8,
        'rust_type': 'u64',
    },
}

def cryptographic_attribute_to_container(cryptographic_attribute):
    if cryptographic_attribute == 'digitally-signed':
        return 'DigitallySigned'
    elif cryptographic_attribute == 'stream-ciphered':
        return 'StreamCiphered'
    elif cryptographic_attribute == 'block-ciphered':
        return 'BlockCiphered'
    elif cryptographic_attribute == 'aead-ciphered':
        return 'AeadCiphered'
    elif cryptographic_attribute == 'public-key-encrypted':
        return 'PublicKeyEncrypted'
    else:
        raise NotImplementedError


def fieldname(ast):
    if hasattr(ast, 'name'):
        return ast.name
    elif not hasattr(ast, 'cryptographic_attribute'):
        return 'container'
    elif ast.cryptographic_attribute == 'digitally-signed':
        return 'signed'
    elif ast.cryptographic_attribute.endswith('-ciphered'):
        return 'ciphered'
    elif ast.cryptographic_attribute == 'public-key-encrypted':
        return 'encrypted'
    else:
        raise NotImplementedError


def typename(ast, parent, with_crypto_attr):
    prefix = '' if parent is None else typename(parent, None, with_crypto_attr) # BUG: we need the parent's parent, too!

    if hasattr(ast, 'name'):
        return ast.name
    elif not hasattr(ast, 'cryptographic_attribute'):
        return prefix+'Container'
    elif ast.cryptographic_attribute == 'digitally-signed':
        typ = '{}Signed'.format(prefix)
        if with_crypto_attr:
            typ = 'DigitallySigned<{}>'.format(typ)
        return typ
    elif ast.cryptographic_attribute == 'stream-ciphered':
        typ = '{}Ciphered'.format(prefix)
        if with_crypto_attr:
            typ = 'StreamCiphered<{}>'.format(typ)
        return typ
    elif ast.cryptographic_attribute == 'block-ciphered':
        typ = '{}Ciphered'.format(prefix)
        if with_crypto_attr:
            typ = 'BlockCiphered<{}>'.format(typ)
        return typ
    elif ast.cryptographic_attribute == 'aead-ciphered':
        typ = '{}Ciphered'.format(prefix)
        if with_crypto_attr:
            typ = 'AeadCiphered<{}>'.format(typ)
        return typ
    elif ast.cryptographic_attribute == 'public-key-encrypted':
        return prefix+'Encrypted'
    else:
        raise NotImplementedError


Pair = collections.namedtuple('Pair', ['decl', 'spec'])
def merge_pairs(decl, *pairs, spec_delimiter=None):
    if spec_delimiter is None:
        spec_delimiter = '\n'
    return Pair(spec=spec_delimiter.join(p.spec for p in pairs),
                decl=decl)


def _compile_enum_packet_representation(ast, in_named_structure, parent=None):
    assert not hasattr(ast, 'cryptographic_attribute')
    entries = map(compile_packet_representation, ast.data.values())
    contents = ',\n    '.join(e.decl for e in entries)
    code = '''enum {} {{
    {},
}}
'''
    return merge_pairs(code.format(ast.name, contents),
                       *entries)


def _compile_structure_packet_representation(ast, in_named_structure, parent=None):
    fields = map(compile_packet_representation, list(ast.data.values())[0])
    fields = [compile_packet_representation(f, in_named_structure=True, parent=ast)
              for f in list(ast.data.values())[0]]

    name = fieldname(ast)
    decl_typ = typename(ast, parent, with_crypto_attr=True)
    spec_typ = typename(ast, parent, with_crypto_attr=False)

    if not hasattr(ast, 'cryptographic_attribute'):
        container = None
    else:
        attr = ast.cryptographic_attribute
        container = cryptographic_attribute_to_container(attr)

    if not hasattr(ast, 'structure_variant'):
        enum = ''
    else:
        var = ast.structure_variant
        variants = [compile_packet_representation(c, parent=ast)
                    for c in var.variant_cases]
        variants = list(itertools.chain(*variants))
        variant_decls = ',\n    '.join(v.decl for v in variants)
        spec = '''enum {}Variant {{
    {},
}}
'''
        decl = '{}: {}Variant'.format(var.name, ast.name)
        var = Pair(decl=decl, spec=spec.format(ast.name, variant_decls))
        fields.append(var)

    code = '''struct {} {{
    {},
}}
'''
    decl = '{}: {}'.format(name, decl_typ) if parent else ''
    spec = code.format(spec_typ, ',\n    '.join(f.decl for f in fields))
    struct = Pair(decl='', spec=spec)
    return merge_pairs(decl, *fields+[struct])


def compile_packet_representation(ast, in_named_structure=False, parent=None):
    if type(ast) == Symbol:
        return Pair(spec='',
                    decl='{}'.format(ast))
    elif type(ast) == ScalarField:
        assert not hasattr(ast, 'cryptographic_attribute')
        field_type = ast.type
        if field_type in implicit_types:
            desc = implicit_types[ast.type]
            field_type = desc['rust_type']

        return Pair(spec='',
                    decl='{}: {}'.format(ast.name, field_type))
    elif type(ast) == Definitions:
        pair_list = [compile_packet_representation(a, parent=parent) for a in ast]
        decl = '\n'.join(p.decl for p in pair_list)
        pair = merge_pairs(decl, *pair_list)
        return (pair.spec + pair.decl).strip()

    elif type(ast) is ConstantVectorField:
        assert not hasattr(ast, 'cryptographic_attribute')
        field_type = ast.vector_type
        if field_type in implicit_types:
            desc = implicit_types[ast.vector_type]
            field_type = desc['rust_type']

        return Pair(spec='',
                    decl='{}: {}[{}]'.format(ast.name, field_type, ast.vector_size))
    elif type(ast) is VariableVectorField:
        assert not hasattr(ast, 'cryptographic_attribute')
        field_type = ast.vector_type
        if field_type in implicit_types:
            desc = implicit_types[ast.vector_type]
            field_type = desc['rust_type']

        decl = '{}: Vec<{}>'.format(ast.name, field_type, ast.vector_bounds.ceiling)
        return Pair(spec='',
                    decl=decl)
    elif type(ast) is ExternalEnumEntry:
        return Pair(spec='',
                    decl='{} = {}'.format(ast.name, ast.value))
    elif type(ast) is InternalEnumEntry:
        return Pair(spec='',
                    decl='{}'.format(ast.name))
    elif type(ast) in [ExternalEnum, InternalEnum]:
        return _compile_enum_packet_representation(ast, in_named_structure,
                                                   parent=parent)
    elif type(ast) is VariantCase:
        return [Pair(spec='',
                     decl='{}({})'.format(c, ast.type))
                for c in ast.cases]
    elif type(ast) in [NamedStructure, UnnamedStructure]:
        return _compile_structure_packet_representation(ast, in_named_structure,
                                                        parent=parent)
    else:
        raise NotImplementedError


from pypeg2 import *

class Type(Symbol):
    pass

class Int(Symbol):
    pass

class ScalarField:
    grammar = attr('type', Type), name(), ';'

'''
4.3.  Vectors

   A vector (single-dimensioned array) is a stream of homogeneous data
   elements.  The size of the vector may be specified at documentation
   time or left unspecified until runtime.  In either case, the length
   declares the number of bytes, not the number of elements, in the
   vector.  The syntax for specifying a new type, T', that is a fixed-
   length vector of type T is

      T T'[n];

   Here, T' occupies n bytes in the data stream, where n is a multiple
   of the size of T.  The length of the vector is not included in the
   encoded stream.

   In the following example, Datum is defined to be three consecutive
   bytes that the protocol does not interpret, while Data is three
   consecutive Datum, consuming a total of nine bytes.

      opaque Datum[3];      /* three uninterpreted bytes */
      Datum Data[9];        /* 3 consecutive 3 byte vectors */

   Variable-length vectors are defined by specifying a subrange of legal
   lengths, inclusively, using the notation <floor..ceiling>.  When
   these are encoded, the actual length precedes the vector's contents
   in the byte stream.  The length will be in the form of a number
   consuming as many bytes as required to hold the vector's specified
   maximum (ceiling) length.  A variable-length vector with an actual
   length field of zero is referred to as an empty vector.

      T T'<floor..ceiling>;

   In the following example, mandatory is a vector that must contain
   between 300 and 400 bytes of type opaque.  It can never be empty.
   The actual length field consumes two bytes, a uint16, which is
   sufficient to represent the value 400 (see Section 4.4).  On the
   other hand, longer can represent up to 800 bytes of data, or 400
   uint16 elements, and it may be empty.  Its encoding will include a
   two-byte actual length field prepended to the vector.  The length of
   an encoded vector must be an even multiple of the length of a single
   element (for example, a 17-byte vector of uint16 would be illegal).

      opaque mandatory<300..400>;
            /* length field is 2 bytes, cannot be empty */
      uint16 longer<0..800>;
            /* zero to 400 16-bit unsigned integers */
'''

class VariableVectorBounds:
    grammar = '<', attr('floor', Int), '..', attr('ceiling', Int), '>'

class VariableVectorField:
    grammar = attr('vector_type', Type), name(), attr('vector_bounds', VariableVectorBounds), ';'

class ConstantVectorField:
    grammar = attr('vector_type', Type), name(), '[', attr('vector_size', Int), '];'

'''
4.5.  Enumerateds

   An additional sparse data type is available called enum.  A field of
   type enum can only assume the values declared in the definition.
   Each definition is a different type.  Only enumerateds of the same
   type may be assigned or compared.  Every element of an enumerated
   must be assigned a value, as demonstrated in the following example.
   Since the elements of the enumerated are not ordered, they can be
   assigned any unique value, in any order.

      enum { e1(v1), e2(v2), ... , en(vn) [[, (n)]] } Te;

   An enumerated occupies as much space in the byte stream as would its
   maximal defined ordinal value.  The following definition would cause
   one byte to be used to carry fields of type Color.

      enum { red(3), blue(5), white(7) } Color;
   One may optionally specify a value without its associated tag to
   force the width definition without defining a superfluous element.

   In the following example, Taste will consume two bytes in the data
   stream but can only assume the values 1, 2, or 4.

      enum { sweet(1), sour(2), bitter(4), (32000) } Taste;

   The names of the elements of an enumeration are scoped within the
   defined type.  In the first example, a fully qualified reference to
   the second element of the enumeration would be Color.blue.  Such
   qualification is not required if the target of the assignment is well
   specified.

      Color color = Color.blue;     /* overspecified, legal */
      Color color = blue;           /* correct, type implicit */

   For enumerateds that are never converted to external representation,
   the numerical information may be omitted.

      enum { low, medium, high } Amount;
'''
class ExternalEnumEntry():
    grammar = name(), '(', attr('value', Int), ')'

class ExternalEnum(Namespace):
    grammar = 'enum', '{', attr('enum_entries', csl(ExternalEnumEntry)), \
                        optional(',', '(', attr('enum_width', Int), ')'), \
                   '}', \
              optional(name()), ';'

class InternalEnumEntry():
    grammar = name()

class InternalEnum(Namespace):
    grammar = 'enum', '{', attr('enum_entries', csl(InternalEnumEntry)), '}', name(), ';'

'''
4.6.1.  Variants

   Defined structures may have variants based on some knowledge that is
   available within the environment.  The selector must be an enumerated
   type that defines the possible variants the structure defines.  There
   must be a case arm for every element of the enumeration declared in
   the select.  Case arms have limited fall-through: if two case arms
   follow in immediate succession with no fields in between, then they
   both contain the same fields.  Thus, in the example below, "orange"
   and "banana" both contain V2.  Note that this is a new piece of
   syntax in TLS 1.2.

   The body of the variant structure may be given a label for reference.
   The mechanism by which the variant is selected at runtime is not
   prescribed by the presentation language.

      struct {
          T1 f1;
          T2 f2;
          ....
          Tn fn;
           select (E) {
               case e1: Te1;
               case e2: Te2;
               case e3: case e4: Te3;
               ....
               case en: Ten;
           } [[fv]];
      } [[Tv]];

   For example:

      enum { apple, orange, banana } VariantTag;

      struct {
          uint16 number;
          opaque string<0..10>; /* variable length */
      } V1;

      struct {
          uint32 number;
          opaque string[10];    /* fixed length */
      } V2;

      struct {
          select (VariantTag) { /* value of selector is implicit */
              case apple:
                V1;   /* VariantBody, tag = apple */
              case orange:
              case banana:
                V2;   /* VariantBody, tag = orange or banana */
          } variant_body;       /* optional label on variant */
      } VariantRecord;
'''
class VariantCase():
    grammar = attr('cases', some('case', Symbol, ':')), attr('type', Type), ';'

class Variant():
    grammar = 'select', '(', attr('variant_type', Type), ')', '{', \
                  attr('variant_cases', some(VariantCase)), \
              '}', name(), ';'


'''
4.6.  Constructed Types

   Structure types may be constructed from primitive types for
   convenience.  Each specification declares a new, unique type.  The
   syntax for definition is much like that of C.

      struct {
          T1 f1;
          T2 f2;
          ...
          Tn fn;
      } [[T]];

   The fields within a structure may be qualified using the type's name,
   with a syntax much like that available for enumerateds.  For example,
   T.f2 refers to the second field of the previous declaration.
   Structure definitions may be embedded.
'''
class NamedStructure(Namespace):
    grammar = 'struct', '{', \
                             optional(attr('structure_fields', some(ScalarField))), \
                             optional(attr('structure_variant', Variant)), \
                        '}', name(), ';'


class UnnamedStructure():
    # this is not a Namespace, because Namespaces need names
    grammar = 'struct', '{', attr('structure_fields', maybe_some(ScalarField)), '}', ';'


"""
Implementation of C# System.Guid

References:
    https://referencesource.microsoft.com/#mscorlib/system/guid.cs

===

MIT License

Copyright (c) 2018 Dusty.P https://github.com/dustinpianalto

Permission is hereby granted, free of charge, to any person obtaining
a copy of this software and associated documentation files (the
"Software"), to deal in the Software without restriction, including
without limitation the rights to use, copy, modify, merge, publish,
distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to
the following conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

"""

from struct import Struct, pack
from math import log

# Constants for masking bytes
MAXINT64 = 0xFFFFFFFFFFFFFFFF
MAXINT16 = 0xFFFF
MAXINT8 = 0xFF


class Guid:
    """
    A Global Unique Identifier (Guid) based on the one provided in C#'s System package

    The Guid is stored as a tuple of length 11 for easy processing and comparisons

    Attributes:
        guid (tuple): A tuple containing the guid
    """
    def __init__(self, *args):
        """
        Initialize the Guid

        Arguments:
            Union[int, str, bytes, short(int will be masked to short)]:
                The arguments can be in any of the following formats:
                (bytes(len 16))
                (int(len <= 4), short, short, bytes(len 8))
                (int(len <= 8), int(len <= 8))
                (int(len <= 16))
                (str) - str must be formatted 00000000-0000-0000-0000-000000000000
        """
        # Guid will be stored as a tuple len 11
        if bool(args):
            self.get_guid(args)
        else:
            self.guid = (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)

    def get_guid(self, args) -> None:
        s = Struct('I2H8B')
        if len(args) == 1 and isinstance(args[0], bytes) and len(args[0]) == 16:
            b = args[0]
            guid = s.pack((int(b[3]) << 24) | (int(b[2]) << 16) | (int(b[1]) << 8) | b[0],
                          ((int(b[5]) << 8) | b[4]),
                          (int(b[7]) << 8) | b[6],
                          *b[8:16]
                          )
            self.guid = s.unpack(guid)
        elif len(args) == 4 and all(isinstance(arg, int) for arg in args[0:3]) \
                and isinstance(args[3], bytes) and len(args[3]) == 8:
            guid = s.pack(args[0], args[1] & MAXINT16, args[2] & MAXINT16, *args[3])
            self.guid = s.unpack(guid)
        elif len(args) == 2 and all(isinstance(arg, int) for arg in args):
            if all((self.bytes_needed(arg) <= 4) for arg in args):
                int1, int2 = (args[0] << 32), (args[1] & 0xFFFFFFFF)
                id_int = int1 | int2
                b = pack('Q8x', id_int)
            elif all((self.bytes_needed(arg) <= 8) for arg in args):
                b = pack('QQ', args[0], args[1])
            else:
                raise TypeError('Arguments don\'t match any allowed configuration')
            guid = s.pack((int(b[3]) << 24) | (int(b[2]) << 16) | (int(b[1]) << 8) | b[0],
                          ((int(b[5]) << 8) | b[4]),
                          ((int(b[7]) << 8) | b[6]),
                          *b[8:16]
                          )
            self.guid = s.unpack(guid)
        elif len(args) == 1 and isinstance(args[0], int):
            if self.bytes_needed(args[0]) <= 8:
                b = pack('Q8x', args[0])
            else:
                first = (args[0] >> 64) & MAXINT64
                second = args[0] & MAXINT64
                b = pack('QQ', first, second)
            guid = s.pack((int(b[3]) << 24) | (int(b[2]) << 16) | (int(b[1]) << 8) | b[0],
                          ((int(b[5]) << 8) | b[4]),
                          (int(b[7]) << 8) | b[6],
                          *b[8:16]
                          )
            self.guid = s.unpack(guid)
        elif len(args) == 1 and isinstance(args[0], str) and len(args[0]) == 36:
            self.parse_string(args[0])
        else:
            raise TypeError('Arguments don\'t match any allowed configuration')

    def parse_string(self, string):
        if len(string) == 36:
            if string[8] == '-' and string[13] == '-' and string[18] == '-' and string[23] == '-':
                guid_str = string.split('-')
                try:
                    self.guid = (int(guid_str[0], 16),
                                 int(guid_str[1], 16),
                                 int(guid_str[2], 16),
                                 int(guid_str[3], 16) >> 8,
                                 int(guid_str[3], 16) & MAXINT8,
                                 int(guid_str[4], 16) >> 40,
                                 int(guid_str[4], 16) >> 32,
                                 int(guid_str[4], 16) >> 24,
                                 int(guid_str[4], 16) >> 16,
                                 int(guid_str[4], 16) >> 8,
                                 int(guid_str[4], 16) & MAXINT8,
                                 )
                except ValueError:
                    raise TypeError('String is not formatted properly must be in format '
                                    '00000000-0000-0000-0000-000000000000')

    def to_string(self):
        output = ''
        output += self.hexs_to_chars(self.guid[0] >> 24, self.guid[0] >> 16)
        output += self.hexs_to_chars(self.guid[0] >> 8, self.guid[0])
        output += '-'
        output += self.hexs_to_chars(self.guid[1] >> 8, self.guid[1])
        output += '-'
        output += self.hexs_to_chars(self.guid[2] >> 8, self.guid[2])
        output += '-'
        output += self.hexs_to_chars(self.guid[3], self.guid[4])
        output += '-'
        output += self.hexs_to_chars(self.guid[5], self.guid[6])
        output += self.hexs_to_chars(self.guid[7], self.guid[8])
        output += self.hexs_to_chars(self.guid[9], self.guid[10])
        return output

    def to_byte_array(self):
        b = bytearray(16)
        b[0] = self.guid[0] & MAXINT8
        b[1] = (self.guid[0] >> 8) & MAXINT8
        b[2] = (self.guid[0] >> 16) & MAXINT8
        b[3] = (self.guid[0] >> 24) & MAXINT8
        b[4] = self.guid[1] & MAXINT8
        b[5] = (self.guid[1] >> 8) & MAXINT8
        b[6] = self.guid[2] & MAXINT8
        b[7] = (self.guid[2] >> 8) & MAXINT8
        b[8] = self.guid[3] & MAXINT8
        b[9] = self.guid[4] & MAXINT8
        b[10] = self.guid[5] & MAXINT8
        b[11] = self.guid[6] & MAXINT8
        b[12] = self.guid[7] & MAXINT8
        b[13] = self.guid[8] & MAXINT8
        b[14] = self.guid[9] & MAXINT8
        b[15] = self.guid[10] & MAXINT8
        return b

    def hexs_to_chars(self, _a, _b):
        out = f'{self.hex_to_char(_a>>4)}{self.hex_to_char(_a)}{self.hex_to_char(_b>>4)}{self.hex_to_char(_b)}'
        return out

    @staticmethod
    def bytes_needed(a):
        if a == 0:
            return 1
        return int(log(a, 256)) + 1

    @staticmethod
    def hex_to_char(a: int):
        a = a & 0xf
        out = chr(a - 10 + 0x61 if a > 9 else a + 0x30)
        return out

    def __hash__(self):
        t = self.guid
        return t[0] ^ ((int(t[1]) << 16) | int(t[2])) ^ ((int(t[5]) << 24) | t[10])

    def __eq__(self, other):
        if other is None or not isinstance(other, Guid):
            return False
        if other.guid[0] != self.guid[0]:
            return False
        if other.guid[1] != self.guid[1]:
            return False
        if other.guid[2] != self.guid[2]:
            return False
        if other.guid[3] != self.guid[3]:
            return False
        if other.guid[4] != self.guid[4]:
            return False
        if other.guid[5] != self.guid[5]:
            return False
        if other.guid[6] != self.guid[6]:
            return False
        if other.guid[7] != self.guid[7]:
            return False
        if other.guid[8] != self.guid[8]:
            return False
        if other.guid[9] != self.guid[9]:
            return False
        if other.guid[10] != self.guid[10]:
            return False
        return True

    def __bool__(self):
        return not (self.guid == (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0))

    def __str__(self):
        return self.to_string()

    def __repr__(self):
        return f'<Guid hash={self.__hash__()}>'

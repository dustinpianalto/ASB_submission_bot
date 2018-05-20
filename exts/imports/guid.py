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
    def __init__(self, guid_tuple: tuple=()):
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
        if bool(guid_tuple):
            if len(guid_tuple) == 11:
                if all(isinstance(t, int) for t in guid_tuple):
                    s = Struct('I2H8B')
                    guid = s.pack(guid_tuple[0],
                                  guid_tuple[1] & MAXINT16,
                                  guid_tuple[2] & MAXINT16,
                                  *guid_tuple[3])
                    self.guid = s.unpack(guid)
                else:
                    raise RuntimeError('Every item in tuple must be an integer')
            else:
                raise RuntimeError('Tuple must be length 11 to create the guid')
        else:
            self.guid = (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)

    @classmethod
    def from_tuple(cls, guid_bytes: bytes):
        s = Struct('I2H8B')
        if len(guid_bytes) == 16:
            guid = s.pack((int(guid_bytes[3]) << 24)
                          | (int(guid_bytes[2]) << 16)
                          | (int(guid_bytes[1]) << 8)
                          | guid_bytes[0],
                          (int(guid_bytes[5]) << 8)
                          | guid_bytes[4],
                          (int(guid_bytes[7]) << 8)
                          | guid_bytes[6],
                          *guid_bytes[8:16]
                          )
            return cls(s.unpack(guid))
        else:
            raise RuntimeError('Bytes object must be of length 16 to create a '
                               'guid')

    @classmethod
    def from_int(cls, guid_int1: int, guid_int2: int=0):
        if cls.bytes_needed(guid_int1) <= 16 and guid_int2 == 0:
            b = pack('QQ', guid_int1 >> 64, guid_int1 & MAXINT64)
        elif cls.bytes_needed(guid_int1) <= 4 and cls.bytes_needed(guid_int2) <= 4:
            int1, int2 = (guid_int1 << 32), (guid_int2 & 0xFFFFFFFF)
            guid_int = int1 | int2
            b = pack('Q8x', guid_int)
        elif cls.bytes_needed(guid_int1) <= 8 and cls.bytes_needed(guid_int2) <= 8:
            b = pack('QQ', guid_int1, guid_int2)
        else:
            raise RuntimeError('Integer is to large')
        guid = ((int(b[3]) << 24) | (int(b[2]) << 16) | (int(b[1]) << 8) | b[0],
                ((int(b[5]) << 8) | b[4]),
                ((int(b[7]) << 8) | b[6]),
                *b[8:16]
                )
        return cls(s.unpack(guid))

    @classmethod
    def from_string(cls, string: str):
        if len(string) == 36:
            if string[8] == '-' and string[13] == '-' and string[18] == '-' and string[23] == '-':
                guid_str = string.split('-')
                try:
                    guid = (int(guid_str[0], 16),
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
                    return cls(guid)
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

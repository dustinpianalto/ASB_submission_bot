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

from struct import Struct, pack, unpack
from math import log
from secrets import randbelow
import uuid
from datetime import datetime
import os

# Constants for masking bytes
MAXINT64 = 0xFFFFFFFFFFFFFFFF
MAXINT32 = 0xFFFFFFFF
MAXINT16 = 0xFFFF
MAXINT8 = 0xFF

# Host Machine's MAC Address
MAC_ADDR = uuid.getnode()

# Geeksbot Epoch Jan 01 2018 in seconds since Jan 01 1970
GEPOCH = datetime(2018, 1, 1).timestamp()


class Guid:
    """Creates a unique Guid object.

    Args:
       :param guid_tuple: (Optional) A tuple of length 11 containing
                                     the different parts of the Guid

    Returns:
       Guid object

    Raises:
       RuntimeError

    Example Usage:
    >>> g = Guid.from_int(1234567899876534, 23456754325675)
    >>> g
    <Guid hash=3721039026>
    >>> print(g)
    '3d1f8cb6-62d5-0004-ab58-827355150000'

    If initiated without any arguments a unique, semi-random Guid will be
    produced using a random number, host computer's mac address, python
    process id, and the current time in the following format:

    ########  -  ####  -  ####  -  ####  -  ############
       ^          ^         ^       ^            ^
     Random       MAC address      PID      Current Time
              masked to the last          In   microseconds
              4 bytes (last 2 of          since Jan 01 2018
              manufacture ID and          1514797200 seconds
              all of serial num)          After Unix Epoch.

    >>> g = Guid()
    >>> print(g)
    93da0643-375a-5496-f92e-060b44965042

    You can create a Guid object several different ways and there are
    constructor methods for the most common use cases.

    Guid.from_bytes(bytes_obj) Takes a bytes object of length 16
    Guid.from_int(int, int) Takes 1 or 2 integers (see help for size restrictions)
    Guid.from_string(str) Takes the string representation in the
                            format returned by Guid.to_string()
    Guid.empty() Takes no arguments and returns an empty (all 0s) Guid

    """
    def __init__(self, guid_tuple: tuple=()):
        if bool(guid_tuple):
            if len(guid_tuple) == 11:
                if all(isinstance(t, int) for t in guid_tuple):
                    s = Struct('I2H8B')
                    guid = s.pack(guid_tuple[0],
                                  guid_tuple[1] & MAXINT16,
                                  guid_tuple[2] & MAXINT16,
                                  *guid_tuple[3:])
                    self.guid = s.unpack(guid)
                else:
                    raise RuntimeError('Every item in tuple must be an integer')
            else:
                raise RuntimeError('Tuple must be length 11 to create the guid')
        else:
            # Generate semi random unique Guid
            time_now = int((datetime.utcnow().timestamp() - GEPOCH) * 1000000)
            rand_int = randbelow(0xFFFFFFFF)
            packed_guid = pack('2I4H',
                               rand_int,
                               MAC_ADDR & MAXINT32,
                               os.getpid() & MAXINT16,
                               (time_now >> 32) & MAXINT16,
                               (time_now >> 16) & MAXINT16,
                               time_now & MAXINT16)
            self.guid = unpack('I2H8B', packed_guid)

    @classmethod
    def from_bytes(cls, guid_bytes: bytes):
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
        if cls._bytes_needed(guid_int1) <= 4 and cls._bytes_needed(guid_int2) <= 4 and guid_int2 != 0:
            int1, int2 = (guid_int1 << 32), (guid_int2 & 0xFFFFFFFF)
            guid_int = int1 | int2
            b = pack('Q8x', guid_int)
        elif cls._bytes_needed(guid_int1) <= 8 and cls._bytes_needed(guid_int2) <= 8 and guid_int2 != 0:
            b = pack('QQ', guid_int1, guid_int2)
        elif cls._bytes_needed(guid_int1) <= 8 and guid_int2 == 0:
            b = pack('QQ', guid_int1 >> 32, guid_int1 & MAXINT32)
        elif cls._bytes_needed(guid_int1) <= 16 and guid_int2 == 0:
            b = pack('QQ', guid_int1 >> 64, guid_int1 & MAXINT64)
        else:
            raise RuntimeError('Integer is to large')
        guid = ((int(b[3]) << 24) | (int(b[2]) << 16) | (int(b[1]) << 8) | b[0],
                ((int(b[5]) << 8) | b[4]),
                ((int(b[7]) << 8) | b[6]),
                *b[8:16]
                )
        return cls(guid)

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

    @classmethod
    def empty(cls):
        return cls((0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0))

    def to_string(self):
        output = ''
        output += self._hexs_to_chars(self.guid[0] >> 24, self.guid[0] >> 16)
        output += self._hexs_to_chars(self.guid[0] >> 8, self.guid[0])
        output += '-'
        output += self._hexs_to_chars(self.guid[1] >> 8, self.guid[1])
        output += '-'
        output += self._hexs_to_chars(self.guid[2] >> 8, self.guid[2])
        output += '-'
        output += self._hexs_to_chars(self.guid[3], self.guid[4])
        output += '-'
        output += self._hexs_to_chars(self.guid[5], self.guid[6])
        output += self._hexs_to_chars(self.guid[7], self.guid[8])
        output += self._hexs_to_chars(self.guid[9], self.guid[10])
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

    def _hexs_to_chars(self, _a: int, _b: int) -> str:
        out = f'{self._hex_to_char(_a>>4)}{self._hex_to_char(_a)}{self._hex_to_char(_b>>4)}{self._hex_to_char(_b)}'
        return out

    @staticmethod
    def _bytes_needed(a: int) -> int:
        if a == 0:
            return 1
        return int(log(a, 256)) + 1

    @staticmethod
    def _hex_to_char(a: int) -> str:
        a = a & 0xf
        out = chr(a - 10 + 0x61 if a > 9 else a + 0x30)
        return out

    def __hash__(self):
        t = self.guid
        return t[0] ^ ((int(t[1]) << 16) | int(t[2])) ^ ((int(t[5]) << 24) | t[10])

    def __eq__(self, other):
        if self.__class__ == other.__class__:
            return self.guid == getattr(other, 'guid', None)
        return False

    def __bool__(self):
        return not (self.guid == (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0))

    def __str__(self):
        return self.to_string()

    def __repr__(self):
        return f'<Guid hash={self.__hash__()}>'

from struct import Struct, pack

def hex_to_char(a: int):
    a = a & 0xf
    out = chr(a - 10 + 0x61 if a > 9 else a + 0x30)
    return out


def hexs_to_chars(_a, _b):
    out = f'{hex_to_char(_a>>4)}{hex_to_char(_a)}{hex_to_char(_b>>4)}{hex_to_char(_b)}'
    return out


def to_string(guid):
    output = ''
    output += hexs_to_chars(guid[0] >> 24, guid[0] >> 16)
    output += hexs_to_chars(guid[0] >> 8, guid[0])
    output += '-'
    output += hexs_to_chars(guid[1] >> 8, guid[1])
    output += '-'
    output += hexs_to_chars(guid[2] >> 8, guid[2])
    output += '-'
    output += hexs_to_chars(guid[3], guid[4])
    output += '-'
    output += hexs_to_chars(guid[5], guid[6])
    output += hexs_to_chars(guid[7], guid[8])
    output += hexs_to_chars(guid[9], guid[10])
    return output


def get_guid_string(id1: int, id2: int):
    id1, id2 = (id1 << 32), (id2 & 0xFFFFFFFF)
    id_int = id1 | id2
    b = pack('Q8x', id_int)
    s = Struct('I2H8B')
    guid = s.pack((int(b[3]) << 24) | (int(b[2]) << 16) | (int(b[1]) << 8) | b[0],
                  ((int(b[5]) << 8) | b[4]),
                  (int(b[7]) << 8) | b[6],
                  *b[8:16]
                  )
    return to_string(s.unpack(guid))

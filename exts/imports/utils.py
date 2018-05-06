from io import StringIO
import sys
import asyncio
import discord
from discord.ext.commands.formatter import Paginator
import numpy as np
from struct import Struct


class Capturing(list):
    def __enter__(self):
        self._stdout = sys.stdout
        sys.stdout = self._stringio = StringIO()
        return self

    def __exit__(self, *args):
        self.extend(self._stringio.getvalue().splitlines())
        del self._stringio    # free up some memory
        sys.stdout = self._stdout


def to_list_of_str(items, out: list=list(), level=1, recurse=0):
    def rec_loop(item, key, out, level):
        quote = '"'
        if type(item) == list:
            out.append(f'{"    "*level}{quote+key+quote+": " if key else ""}[')
            new_level = level + 1
            out = to_list_of_str(item, out, new_level, 1)
            out.append(f'{"    "*level}]')
        elif type(item) == dict:
            out.append(f'{"    "*level}{quote+key+quote+": " if key else ""}{{')
            new_level = level + 1
            out = to_list_of_str(item, out, new_level, 1)
            out.append(f'{"    "*level}}}')
        else:
            out.append(f'{"    "*level}{quote+key+quote+": " if key else ""}{repr(item)},')

    if type(items) == list:
        if not recurse:
            out = list()
            out.append('[')
        for item in items:
            rec_loop(item, None, out, level)
        if not recurse:
            out.append(']')
    elif type(items) == dict:
        if not recurse:
            out = list()
            out.append('{')
        for key in items:
            rec_loop(items[key], key, out, level)
        if not recurse:
            out.append('}')

    return out


def paginate(text, maxlen=1990):
    paginator = Paginator(prefix='```py', max_size=maxlen+10)
    if type(text) == list:
        data = to_list_of_str(text)
    elif type(text) == dict:
        data = to_list_of_str(text)
    else:
        data = str(text).split('\n')
    for line in data:
        if len(line) > maxlen:
            n = maxlen
            for l in [line[i:i+n] for i in range(0, len(line), n)]:
                paginator.add_line(l)
        else:
            paginator.add_line(line)
    return paginator.pages


async def run_command(args):
    # Create subprocess
    process = await asyncio.create_subprocess_shell(
        args,
        # stdout must a pipe to be accessible as process.stdout
        stdout=asyncio.subprocess.PIPE)
    # Wait for the subprocess to finish
    stdout, stderr = await process.communicate()
    # Return stdout
    return stdout.decode().strip()


def hex_to_char(a: int):
    a = a & 0xf
    out = str(a - 10 + 0x61 if a > 9 else a + 0x30)
    print(out)
    return out


def hexs_to_chars(_a, _b):
    out = f'{hex_to_char(_a>>4)}{hex_to_char(_a)}{hex_to_char(_b>>4)}{hex_to_char(_b)}'
    print(out)
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


def get_guid(id1: int, id2: int):
    id_int = (id1 << 32) | (id2 & 0xFFFFFFFF)
    b = id_int.to_bytes(16, byteorder='little')
    s = Struct('i2h8i')
    guid = s.pack((int(b[3]) << 24) | (int(b[2]) << 16) | (int(b[1]) << 8) | b[0],
                  ((int(b[5]) << 8) | b[4]),
                  (int(b[7]) << 8) | b[6],
                  *b[8:16]
                  )
    return to_string(s.unpack(guid))
    # return _a ^ ((int(_b) << 16) | int(np.ushort(_c))) ^ ((int(_f) << 24) | _k)

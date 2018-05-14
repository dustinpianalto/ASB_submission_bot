"""
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


import zipfile
import os
import json
from configparser import ConfigParser
from .guid import Guid
from shutil import rmtree
from hashlib import md5

config_dir = 'config/'
bot_config_file = 'bot_config.json'


class MissingFile(Exception):
    pass


def load_zip(file) -> zipfile.ZipFile:
    return zipfile.ZipFile(file)


def check_for_mods(game_file) -> list:
    mods = list()
    for line in game_file.readlines():
        if line.startswith('ModIDS='):
            mods.append(line.split('=')[1].strip())
    return mods


def check_for_modded_dinos(dino_data, active_mods) -> list:
    with open(f'{config_dir}{bot_config_file}') as f:
        mods = json.load(f)['mods']
    for filename, dino in dino_data.items():
        for mod in mods:
            if dino['Dino Data']['DinoClass'].startswith(mod):
                if mods[mod] not in active_mods:
                    active_mods.append(mods[mod])
    return active_mods


def rename_section(cfg, sec, sec_new):
    items = cfg.items(sec)
    cfg.add_section(sec_new)
    for item in items:
        cfg.set(sec_new, item[0], item[1])
    cfg.remove_section(sec)
    return cfg


def get_server_guid(server_file):
    server_file = server_file.encode()
    m = md5(server_file).hexdigest().encode()
    guid = Guid(int(m.hex()))
    return guid


def process_file(in_file, file_type) -> ConfigParser:
    with open(f'{config_dir}{bot_config_file}') as f:
        bot_config = json.load(f)
        ignore_strings = bot_config['ignore_strings'][file_type]
        keep_blocks = bot_config['keep_blocks'][file_type]
    data = in_file.readlines()
    # data = [line.decode() for line in in_file]
    # data = [line.decode(encoding=encoding) for line in in_file]
    clean_data = list()

    if ignore_strings:
        for line in data:
            ignore = 0
            for string in ignore_strings:
                if string.lower() in line.lower():
                    ignore = 1
            if not ignore:
                clean_data.append(line)
    else:
        clean_data = data

    config = ConfigParser()
    config.optionxform = str
    config.read_string('\n'.join(clean_data))
    for section in config.sections():
        if section in keep_blocks:
            pass
        elif section.lower() in keep_blocks:
            config = rename_section(config, section, section.lower())
        elif section.title() in keep_blocks:
            config = rename_section(config, section, section.title())
        else:
            config.remove_section(section)
    print(f"{config.sections()} {config['Dino Ancestry']['DinoAncestorsCount']}")
    return config


def process_files(z) -> (ConfigParser, ConfigParser, list, Guid):
    dino_data = dict()
    game_config = ConfigParser()
    server_guid = Guid()
    mods = list()
    path = 'submissions_temp/tmp/'
    z.extractall(path=path)
    files = os.listdir(path)
    for filename in files:
        if filename.endswith('.ini'):
            # ignore any files that don't end with .ini
            if filename.lower() == 'game.ini':
                # Clean the Game.ini file, removing unnecessary lines
                try:
                    with open(f'{path}{filename}', encoding='utf-8') as file:
                        game_config = process_file(file, 'game.ini')
                        file.seek(0)
                        mods = check_for_mods(file)
                        file.seek(0)
                        server_file = file.read()
                except UnicodeDecodeError as e:
                    print(e)
                    try:
                        with open(f'{path}{filename}', 'rb') as file:
                            contents = file.read()
                            with open(f'{path}utf8{filename}', 'wb') as f:
                                f.write(contents.decode('utf-16-le').replace('\uFEFF', '').encode('utf-8'))
                        with open(f'{path}utf8{filename}', encoding='utf-8') as file:
                            game_config = process_file(file, 'game.ini')
                            file.seek(0)
                            mods = check_for_mods(file)
                            file.seek(0)
                            server_file = file.read()
                    except UnicodeDecodeError as e:
                        print(e)
                        return 0, 0, 0
                server_guid = get_server_guid(server_file)
            elif 'DinoExport' in filename:
                # Get the contents of all DinoExport_*.ini files loaded into a dict
                print(filename)
                try:
                    with open(f'{path}{filename}', encoding='utf-8') as file:
                        dino_data[filename] = process_file(file, 'dino.ini')
                except UnicodeDecodeError as e:
                    print(e)
                    try:
                        with open(f'{path}{filename}', 'rb') as file:
                            contents = file.read()
                            with open(f'{path}utf8{filename}', 'wb') as f:
                                f.write(contents.decode('utf-16-le').replace('\uFEFF', '').encode('utf-8'))
                        with open(f'{path}utf8{filename}', encoding='utf-8') as file:
                            dino_data[filename] = process_file(file, 'dino.ini')
                    except UnicodeDecodeError as e:
                        print(e)
                        return 0, 0, 0
    rmtree('submissions_temp/tmp')
    if not mods:
        mods = check_for_modded_dinos(dino_data, mods)
    return game_config, dino_data, mods, server_guid


def generate_game_ini(game_config, mods, directory):
    print(game_config.sections())
    if mods:
        game_config['/script/shootergame.shootergamemode']['ModIDS'] = ', '.join(mods)
    with open(f'{directory}/Game.ini', 'w') as f:
        game_config.write(f, space_around_delimiters=False)


def generate_dino_files(dino_data, directory):
    for filename, dino in dino_data.items():
        print(filename)
        guid = Guid(int(dino['Dino Data']['DinoID1']), int(dino['Dino Data']['DinoID2']))
        dino['Dino Data']['Guid'] = str(guid)
        with open(f'{directory}/{filename}', 'w') as f:
            dino.write(f, space_around_delimiters=False)


def generate_files(storage_dir, ctx, dirname, game_ini, dinos_data, mods):
    if not os.path.isdir(f'{storage_dir}/{ctx.author.id}'):
        os.mkdir(f'{storage_dir}/{ctx.author.id}')
    directory = f'{storage_dir}/{ctx.author.id}/{dirname}'
    if not os.path.isdir(directory):
        os.mkdir(directory)
    generate_game_ini(game_ini, mods, directory)
    generate_dino_files(dinos_data, directory)
    return 1

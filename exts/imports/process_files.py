import zipfile
import os
import json
from configparser import ConfigParser
from . import guid
from shutil import rmtree

config_dir = 'config/'
bot_config_file = 'bot_config.json'


class MissingFile(Exception):
    pass


def load_zip(file) -> zipfile.ZipFile:
    return zipfile.ZipFile(file)


def check_for_mods(game_file) -> list:
    mods = list()
    for line in list(map(bytes.decode, game_file.readlines())):
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
    print(config.sections())
    return config


def process_files(z) -> (ConfigParser, ConfigParser, list):
    dino_data = dict()
    game_config = ConfigParser()
    mods = list()
    path = 'submissions_temp/tmp/'
    z.extractall(path=path)
    for filename in os.listdir(path):
        if filename.endswith('.ini'):
            # ignore any files that don't end with .ini
            if filename.lower() == 'game.ini':
                # Clean the Game.ini file, removing unnecessary lines
                try:
                    with open(f'{path}{filename}', encoding='utf-8') as file:
                        game_config = process_file(file, 'game.ini')
                        mods = check_for_mods(file)
                except UnicodeDecodeError as e:
                    print(e)
                    try:
                        with open(f'{path}{filename}', 'w+b') as file:
                            contents = file.read()
                            file.write(contents.decode('utf-16-le').encode('utf-8'))
                        with open(f'{path}{filename}', encoding='utf-8') as file:
                            game_config = process_file(file, 'game.ini')
                            mods = check_for_mods(file)
                    except UnicodeDecodeError as e:
                        print(e)
                        return 0, 0, 0
            elif 'DinoExport' in filename:
                # Get the contents of all DinoExport_*.ini files loaded into a dict
                print(filename)
                try:
                    with open(f'{path}{filename}', encoding='utf-8') as file:
                        dino_data[filename] = process_file(file, 'dino.ini')
                except UnicodeDecodeError as e:
                    print(e)
                    try:
                        with open(f'{path}{filename}', 'w+b') as file:
                            contents = file.read()
                            file.write(contents.decode('utf-16-le').encode('utf-8'))
                        with open(f'{path}{filename}', encoding='utf-8') as file:
                            dino_data[filename] = process_file(file, 'dino.ini')
                    except UnicodeDecodeError as e:
                        print(e)
                        return 0, 0, 0
    # rmtree('submissions_temp/tmp')
    if not mods:
        mods = check_for_modded_dinos(dino_data, mods)
    return game_config, dino_data, mods


def generate_game_ini(game_config, mods, directory):
    print(game_config.sections())
    if mods:
        game_config['/script/shootergame.shootergamemode']['ModIDS'] = ', '.join(mods)
    with open(f'{directory}/Game.ini', 'w') as f:
        game_config.write(f, space_around_delimiters=False)


def generate_dino_files(dino_data, directory):
    for filename, dino in dino_data.items():
        print(filename)
        dino['Dino Data']['Guid'] = guid.get_guid_string(int(dino['Dino Data']['DinoID1']),
                                                         int(dino['Dino Data']['DinoID2']))
        with open(f'{directory}/{filename}', 'w') as f:
            dino.write(f, space_around_delimiters=False)


def generate_files(storage_dir, ctx, filename, game_ini, dinos_data, mods):
    if not os.path.isdir(f'{storage_dir}/{ctx.author.id}'):
        os.mkdir(f'{storage_dir}/{ctx.author.id}')
    directory = f'{storage_dir}/{ctx.author.id}/{filename}_' \
                f'{ctx.message.created_at.strftime("%Y%m%dT%H%M%S")}'
    os.mkdir(directory)
    generate_game_ini(game_ini, mods, directory)
    generate_dino_files(dinos_data, directory)
    return 1

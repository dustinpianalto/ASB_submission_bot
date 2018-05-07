import zipfile
import os


class MissingFile(Exception):
    pass


def open_zip(file: str) -> zipfile.ZipFile:
    if file.endswith('.zip'):
        return zipfile.ZipFile(file)
    else:
        raise FileNotFoundError('File name must end in .zip')


def process_game_ini(file):
    return 1


def process_dino_ini(file):
    return 1


def process_files(z):
    dino_data = []
    game_text = None
    for filename in z.namelist():
        if filename.endswith('.ini'):  # ignore any files that don't end with .ini
            if filename == 'Game.ini':
                game_text = process_game_ini(z.open(filename))
            elif 'DinoExport' in filename:
                dino_data.append(process_dino_ini(z.open(filename)))
    return game_text, dino_data
    # if game_text is None:
    #     raise MissingFile('Game.ini')
    # if dino_data is []:
    #     raise MissingFile('DinoExport')

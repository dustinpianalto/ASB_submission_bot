from configparser import ConfigParser
from . import guid
from distutils.util import strtobool
from collections import OrderedDict

config_setup = {'Dino Data': ['DinoID1',
                              'DinoID2',
                              'DinoClass',
                              'DinoNameTag',
                              'bIsFemale',
                              'bNeutered',
                              'TamerString',
                              'TamedName',
                              'ImprinterName',
                              'RandomMutationsMale',
                              'RandomMutationsFemale',
                              'BabyAge',
                              'CharacterLevel',
                              'DinoImprintingQuality'],
                'Colorization': ['ColorSet'],
                'Max Character Status Values': ['Health',
                                                'Stamina',
                                                'Torpidity',
                                                'Oxygen',
                                                'food',
                                                'Water',
                                                'Temperature',
                                                'Weight',
                                                'Melee Damage',
                                                'Movement Speed',
                                                'Fortitude',
                                                'Crafting Skill'],
                'Dino Ancestry': ['DinoAncestorsCount', 'DinoAncestorsMale']
                }

ancestry_setup = {'DinoAncestors': ['DinoAncestors'],
                  'DinoAncestorsMale': ['DinoAncestorsMale']
                  }


class InvalidConfig(AttributeError):
    pass


class Color:
    def __init__(self, r=0, g=0, b=0, a=0):
        self.r = self._hex_to_float(r) if isinstance(r, int) else r
        self.g = self._hex_to_float(g) if isinstance(g, int) else g
        self.b = self._hex_to_float(b) if isinstance(b, int) else b
        self.a = self._hex_to_float(a) if isinstance(a, int) else a

    def to_rgba_string(self, hex_values: bool=False):
        if not hex_values:
            return f'(R={self.r:.6f},G={self.g:.6f},B={self.b:.6f},A={self.a:.6f})'
        else:
            return (f'(R={self._float_to_hex(self.r)},'
                    f'G={self._float_to_hex(self.g)},'
                    f'B={self._float_to_hex(self.b)},'
                    f'A={self._float_to_hex(self.a)})')

    @staticmethod
    def _float_to_hex(a: float) -> int:
        return int(((a - 0.0)/(1.0 - 0.0)) * (255 - 0) + 0.0)

    @staticmethod
    def _hex_to_float(a: int) -> float:
        return float(((a - 0.0)/(255.0 - 0.0)) * (1.0 - 0.0) + 0.0)


class Dino:
    def __init__(self, dino_data: ConfigParser):
        self.dino_data_orig = dino_data
        if dino_data == ConfigParser():
            self.dino_data = self._get_dino_data()
            self.colors = self._get_colors()
            self.stats = self._get_colors()
            self.ancestry = self._get_ancestry()
            self.guid = self.get_guid()
        elif isinstance(dino_data, ConfigParser):
            self.dino_data = self._get_dino_data(list(dino_data['Dino Data'].values()))
            self.colors = self._get_colors(list(dino_data['Colorization'].values()))
            self.stats = self._get_stats(list(dino_data['Max Character Status Values'].values()))
            self.ancestry = self._get_ancestry(list(dino_data['Dino Ancestry'].values()), dino_data)
            self.guid = self.get_guid()
        else:
            raise InvalidConfig('Arguments don\'t match any valid configuration.')

    def get_guid(self) -> guid.Guid:
        return guid.Guid(self.dino_data['DinoID1'], self.dino_data['DinoID2'])

    @staticmethod
    def _get_colors(colorization: list=list()) -> [Color]:
        colors = list()
        if colorization != list():
            for values in colorization:
                value = values.strip('()').split(',')
                c = dict()
                for v in value:
                    v = v.split('=')
                    c[v[0].lower()] = float(v[1])
                colors.append(Color(**c))
        return colors

    @staticmethod
    def _get_stats(stats: list=list()) -> OrderedDict:
        if len(stats) < 12:
            stats.extend([0] * (12 - len(stats)))
        elif len(stats) > 12:
            raise InvalidConfig("Stats list is too long")
        stats = [float(stat) for stat in stats]
        return OrderedDict(zip(config_setup['Max Character Status Values'], stats))

    @staticmethod
    def _get_dino_data(data: list=list()) -> OrderedDict:
        for i, value in enumerate(data):
            try:
                data[i] = int(value)
            except ValueError:
                try:
                    data[i] = float(value)
                except ValueError:
                    try:
                        data[i] = bool(strtobool(value))
                    except ValueError:
                        pass

        if len(data) < 14:
            data.extend([0] * (14 - len(data)))
        elif len(data) > 14:
            raise InvalidConfig
        dino_dict = OrderedDict(zip(config_setup['Dino Data'], data))
        return dino_dict

    @staticmethod
    def _get_ancestry(ancestry: list=list(), data: ConfigParser=None) -> OrderedDict:
        ancestry_dict = OrderedDict()
        if ancestry != list():
            ancestry_dict['DinoAncestorsCount'] = int(ancestry[0])
            ancestry_dict['DinoAncestorsMale'] = int(ancestry[1])

            if ancestry_dict['DinoAncestorsCount'] != 0:
                if 'DinoAncestors' in data.sections():
                    dino_anc = [a for a in data['DinoAncestors'].values()]
                    ancestors = list()
                    for dino in dino_anc:
                        ancestors.append(OrderedDict([field.split('=') for field in dino.split(';')]))
                    ancestry_dict['DinoAncestors_'] = ancestors

            if ancestry_dict['DinoAncestorsMale'] != 0:
                if 'DinoAncestorsMale' in data.sections():
                    dino_anc = [a for a in data['DinoAncestorsMale'].values()]
                    ancestors_male = list()
                    for dino in dino_anc:
                        ancestors_male.append(OrderedDict([field.split('=') for field in dino.split(';')]))
                    ancestry_dict['DinoAncestorsMale_'] = ancestors_male

        return ancestry_dict

    def to_config(self):
        config = ConfigParser()
        config.optionxform = str
        for section in config_setup:
            config.add_section(section)
        for key, data in self.dino_data.items():
            config.set('Dino Data', str(key), (f'{data:.6f}' if type(data) == float else str(data)))
        config.set('Dino Data', 'ASMBot_GUID', str(self.guid))
        for key, data in self.stats.items():
            config.set('Max Character Status Values', str(key), f'{data:.6f}')
        for i, data in enumerate(self.colors):
            config.set('Colorization', f'{config_setup["Colorization"][0]}[{i}]', data.to_rgba_string(hex_values=False))
        if 'DinoAncestors_' in self.ancestry:
            config.add_section('DinoAncestors')
        if 'DinoAncestorsMale_' in self.ancestry:
            config.add_section('DinoAncestorsMale')
        for key, data in self.ancestry.items():
            if key == 'DinoAncestors_':
                for i, item in enumerate(data):
                    config.set('DinoAncestors', f'{ancestry_setup["DinoAncestors"][0]}{i}',
                               ';'.join([f'{k}={v}' for k, v in item.items()]))
            elif key == 'DinoAncestorsMale_':
                for i, item in enumerate(data):
                    config.set('DinoAncestorsMale', f'{ancestry_setup["DinoAncestorsMale"][0]}{i}',
                               ';'.join([f'{k}={v}' for k, v in item.items()]))
            else:
                config.set('Dino Ancestry', str(key), str(data))
        return config

    def to_file(self, path: str):
        if not path.endswith('/'):
            path += '/'
        path += f'DinoExport_{self.dino_data["DinoID1"]}{self.dino_data["DinoID2"]}.ini'
        config = self.to_config()
        with open(path, 'w') as f:
            config.write(f, space_around_delimiters=False)
        print(f'Dino has been written to {path}')

    def parents(self):
        if 'DinoAncestors' in self.ancestry:
            parents = self.ancestry['DinoAncestors'][-1]
            father = Parent(name=parents['MaleName'],
                            id1=parents['MaleDinoID1'],
                            id2=parents['MaleDinoID2'],
                            female=False)
            mother = Parent(name=parents['FemaleName'],
                            id1=parents['FemaleDinoID1'],
                            id2=parents['FemaleDinoID2'],
                            female=True)
            return father, mother
        else:
            return Parent('', True, 0, 0), Parent('', False, 0, 0)

    @classmethod
    def empty(cls):
        return Dino(ConfigParser())

    def __eq__(self, other):
        if self.__class__ == other.__class__:
            if self.guid == other.guid:
                return self.dino_data == other.dino_data and self.stats == other.stats
        return False

    def __str__(self):
        return f'<Dino name={self.dino_data["TamedName"]}, level={self.dino_data["CharacterLevel"]}, guid={self.guid}>'

    def __repr__(self):
        return (f'<Dino species={self.dino_data["DinoNameTag"]} name={self.dino_data["TamedName"]}, '
                f'level={self.dino_data["CharacterLevel"]}, guid={self.guid}>')


class Parent(Dino):
    # noinspection PyMissingConstructor
    def __init__(self, name: str, female: bool, id1: int=0, id2: int=0):
        try:
            self.dino_data = self._get_dino_data([id1, id2, '', '', female, '', '', name])
            self.colors = self._get_colors([])
            self.stats = self._get_stats([])
            self.ancestry = self._get_ancestry([])
            self.guid = self.get_guid()
        except InvalidConfig:
            raise InvalidConfig('Arguments don\'t match any valid configuration.')

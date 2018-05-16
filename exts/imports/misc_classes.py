import configparser
from . import guid


class Color:
    def __init__(self, r=0, g=0, b=0, a=0):
        self.r = self.float_to_hex(r) if isinstance(r, float) else r
        self.g = self.float_to_hex(g) if isinstance(g, float) else g
        self.b = self.float_to_hex(b) if isinstance(b, float) else b
        self.a = self.float_to_hex(a) if isinstance(a, float) else a

    @staticmethod
    def float_to_hex(a: float):
        return ((a - 0.0)/(1.0 - 0.0)) * (255 - 0) + 0.0


class Dino:
    def __init__(self, dino_data=None, parent=False):
        self.parent = parent
        if dino_data is None and parent is False:
            self.dino_data = None
            self.dino_data_orig = None
            self.colors = None
            self.stats = None
            self.ancestry = None
            self.guid = guid.Guid()
        elif parent is False and isinstance(dino_data, configparser.ConfigParser):
            self.dino_data_orig = dino_data
            self.dino_data = self._get_dino_data(dino_data['Dino Data'])
            self.colors = self._get_colors(dino_data['Colorization'])
            self.stats = self._get_colors(dino_data['Max Character Status Values'])
            self.ancestry = self._get_ancestry(dino_data['Dino Ancestry'], dino_data)
            self.guid = self.get_guid()
        elif parent is True and isinstance(dino_data, list):
            self.dino_data = {
                'TamedName': dino_data[0],
                'DinoID1': dino_data[1],
                'DinoID2': dino_data[2]
            }
            self.stats = self._zero_stats()
            self.colors = list()
            self.ancestry = dict()
            self.guid = self.get_guid()
        else:
            raise TypeError('Arguments don\'t match any valid configuration.')

    def get_guid(self) -> guid.Guid:
        return guid.Guid(self.dino_data['DinoID1'], self.dino_data['DinoID2'])

    @staticmethod
    def _get_colors(colorization) -> [Color]:
        colors = list()
        for color, values in colorization.items():
            value = values.strip('()').split(',')
            c = dict()
            for v in value:
                v = v.split('=')
                c[v[0]] = float(v[1])
            colors.append(Color(**c))
        return colors

    def _zero_stats(self):
        return self._get_stats({i: '0' for i in range(12)})

    @staticmethod
    def _get_stats(stat_values) -> dict:
        stats = [stat for stat in stat_values.values()]
        stats_dict = dict()
        stats_dict['Health'] = float(stats[0])
        stats_dict['Stamina'] = float(stats[1])
        stats_dict['Torpidity'] = float(stats[2])
        stats_dict['Oxygen'] = float(stats[3])
        stats_dict['food'] = float(stats[4])
        stats_dict['Water'] = float(stats[5])
        stats_dict['Temperature'] = float(stats[6])
        stats_dict['Weight'] = float(stats[7])
        stats_dict['Melee Damage'] = float(stats[8])
        stats_dict['Movement Speed'] = float(stats[9])
        stats_dict['Fortitude'] = float(stats[10])
        stats_dict['Crafting Skill'] = float(stats[11])
        return stats_dict

    @staticmethod
    def _get_dino_data(dino_data) -> dict:
        data = [d for d in dino_data.values()]
        data_dict = dict()
        data_dict['DinoID1'] = int(data[0])
        data_dict['DinoID2'] = int(data[1])
        data_dict['DinoClass'] = data[2]
        data_dict['DinoNameTag'] = data[3]
        if data[4] == 'True':
            data_dict['bIsFemale'] = True
        else:
            data_dict['bIsFemale'] = False
        if data[5] == 'True':
            data_dict['bNeutered'] = True
        else:
            data_dict['bNeutered'] = False
        data_dict['TamerString'] = data[6]
        data_dict['TamedName'] = data[7]
        data_dict['ImprinterName'] = data[8]
        data_dict['RandomMutationsMale'] = int(data[9])
        data_dict['RandomMutationsFemale'] = int(data[10])
        data_dict['BabyAge'] = float(data[11])
        data_dict['CharacterLevel'] = int(data[12])
        data_dict['DinoImprintingQuality'] = float(data[13])
        return data_dict

    @staticmethod
    def _get_ancestry(ancestry_data, data) -> dict:
        ancestry = [a for a in ancestry_data.values()]
        ancestry_dict = dict()
        ancestry_dict['DinoAncestorsCount'] = int(ancestry[0])
        ancestry_dict['DinoAncestorsMale'] = int(ancestry[1])

        if ancestry_dict['DinoAncestorsCount'] != 0:
            if 'DinoAncestors' in data.sections():
                dino_anc = [a for a in data['DinoAncestors'].values()]
                ancestors = list()
                for dino in dino_anc:
                    ancestors.append(dict([field.split('=') for field in dino.split(';')]))
                ancestry_dict['DinoAncestors'] = ancestors

        if ancestry_dict['DinoAncestorsMale'] != 0:
            if 'DinoAncestorsMale' in data.sections():
                dino_anc = [a for a in data['DinoAncestorsMale'].values()]
                ancestors_male = list()
                for dino in dino_anc:
                    ancestors_male.append(dict([field.split('=') for field in dino.split(';')]))
                ancestry_dict['DinoAncestorsMale'] = ancestors_male

        return ancestry_dict

    def parents(self) -> (Dino, Dino):
        if 'DinoAncestors' in self.ancestry:
            parents = self.ancestry['DinoAncestors'][-1]
            father = Dino.from_min_req(parents['MaleName'],
                                       parents['MaleDinoID1'],
                                       parents['MaleDinoID2'],
                                       True)
            mother = Dino.from_min_req(parents['FemaleName'],
                                       parents['FemaleDinoID1'],
                                       parents['FemaleDinoID2'],
                                       True)
            return father, mother
        else:
            return Dino.empty(), Dino.empty()

    @classmethod
    def from_min_req(cls, name, id1, id2, parent=False):
        return Dino([name, id1, id2], parent=parent)

    @classmethod
    def empty(cls):
        return Dino()

    def __eq__(self, other):
        if isinstance(other, Dino):
            if self.guid == other.guid:
                return self.dino_data == other.dino_data and self.stats == other.stats
            return False
        elif isinstance(other, str):
            try:
                o = guid.Guid(other)
            except TypeError:
                return False
            else:
                return self.guid == o
        elif isinstance(other, guid.Guid):
            return self.guid == other
        else:
            return False

    def __str__(self):
        return f'<Dino name={self.dino_data["TamedName"]}, level={self.dino_data["CharacterLevel"]}, guid={self.guid}>'

    def __repr__(self):
        return (f'<Dino species={self.dino_data["DinoNameTag"]} name={self.dino_data["TamedName"]}, '
                f'level={self.dino_data["CharacterLevel"]}, guid={self.guid}>')

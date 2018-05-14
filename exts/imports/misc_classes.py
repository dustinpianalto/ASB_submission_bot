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
    def __init__(self, dino_data: configparser.ConfigParser):
        self.dino_data_orig = dino_data
        self.dino_data = self._get_dino_data(dino_data['Dino Data'])
        self.colors = self._get_colors(dino_data['Colorization'])
        self.stats = self._get_colors(dino_data['Max Character Status Values'])
        self.ancestry = self._get_ancestry(dino_data['Dino Ancestry'], dino_data)
        self.guid = self.get_guid()

    def get_guid(self):
        return guid.Guid(self.dino_data['DinoID1'], self.dino_data['DinoID2'])

    @staticmethod
    def _get_colors(colorization):
        colors = list()
        for color, values in colorization.items():
            value = values.strip('()').split(',')
            c = dict()
            for v in value:
                v = v.split('=')
                c[v[0]] = float(v[1])
            colors.append(Color(**c))
        return colors

    @staticmethod
    def _get_stats(stat_values):
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
    def _get_dino_data(dino_data):
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
    def _get_ancestry(ancestry_data, data):
        ancestry = [a for a in ancestry_data.values()]
        ancestry_dict = dict()
        ancestry_dict['DinoAncestorsCount'] = int(ancestry[0])
        ancestry_dict['DinoAncestorsMale'] = int(ancestry[1])

        if ancestry_dict['DinoAncestorsCount'] != 0:
            if 'DinoAncestors' in data.sections():
                dino_anc = [a for a in data['DinoAncestors'].values()]
                ancestors = list()
                for dino in dino_anc:
                    dino = dino.split(';')
                    for field in dino:
                        pass

from __future__ import division


class Pokemon(object):
    __slots__ = [
        'id', 'evolutions', 'learns', 'name',
        'description',
    ]

    def __init__(self, **k):
        self.evolutions = k.get('evolutions', [])
        self.id = k.get('id', None)
        self.learns = k.get('learns', []),
        self.name = k.get('name', None)
        self.description = k.get('description', None)


class Learn(object):
    __slots__ = ['move_id', 'level']

    def __str__(self):
        return '   LVL {}: {}'.format(
            self.level,
            moves[self.move_id - 1]
        )

    def __repr__(self):
        return 'Learn(0x{:02X}, 0x{:02X})'.format(
            self.level,
            self.move_id,
        )


class Evolution(object):
    NO = 0
    LEVEL = 1
    STONE = 2
    INTERCHANGE = 3

    __slots__ = ['type', 'into_id', 'level', 'stone_id']


class WildData(object):
    __slots__ = ['choices', 'chances', 'offset', 'rate']

    def __init__(self, offset=None, rate=0):
        self.chances = {}
        self.choices = []
        self.offset = offset
        self.rate = rate

    def feed(self, lvl, pkmn_id):
        t = lvl, pkmn_id
        self.choices.append(t)

    def calculate_chances(self):
        choiset = set(self.choices)
        chances = {}
        total = len(self.choices)

        for choice in choiset:
            chances[choice] = self.choices.count(choice)

        for key in chances:
            chances[key] /= total

        self.chances = chances
        return self.chances
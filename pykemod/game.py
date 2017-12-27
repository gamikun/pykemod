from __future__ import absolute_import
from pykemod import graphics


class Game:
    def __init__(self, data):
        self.data = data

    def get_segment(self, offset, length):
        return self.data[offset:offset + length]

    def find(self, data):
        return self.data.find(data)

    def set_segment(self, offset, segment):
        for index, c in enumerate(segment):
            self.data[offset + index] = c

    def get_evolution(self, pkmn):
        if pkmn == 0xB0: # Charmander
            return (self.data[offset],
                    self.data[offset + 1]
                    )

        raise NotImplementedError('no pkmn evolution')

    def set_evolution(self, pkmn, level=0):
        if pkmn == 0xB0:
            self.data[offset]


class Evolution(object):
    __slots__ = ['pkmn']

    @staticmethod
    def fromraw(raw):
        pass

def open_game(filename):
    with open(filename, 'wb+') as fp:
        data = fp.read()
        game = Game(data)
        return game

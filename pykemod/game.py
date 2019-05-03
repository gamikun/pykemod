# -*- coding: utf8 -*-
from __future__ import absolute_import
from pykemod import graphics
from pykemod.pokemon import Pokemon, Evolution, Learn


class Game:
    PKMN_NAMES_OFFSET = 0x1C21E
    TOTAL_PKMN_SLOTS = 190
    EVO_OFFSET = 242136
    TOTAL_MOVES = 165
    MOVES_OFFSET = 0xB0000
    ROUTE_NAMES_OFFSET = 0x71473
    LETTERS_OFFSET = 0x11A80
    TOTAL_CHARS = 128

    def __init__(self, rom):
        self.rom = rom
        self.pokemons = []
        self.pkmn_names_range = (
            self.PKMN_NAMES_OFFSET,
            self.PKMN_NAMES_OFFSET + 10 * self.TOTAL_PKMN_SLOTS,
        )
        self.evos_upper_limit = -1
        self.move_names_upper_limit = -1
        self.moves = []

    def get_segment(self, offset, length):
        return self.rom[offset:offset + length]

    def find(self, data):
        return self.rom.find(data)

    def set_segment(self, offset, segment):
        for index, c in enumerate(segment):
            self.rom[offset + index] = c

    def get_evolution(self, pkmn):
        if pkmn == 0xB0: # Charmander
            return (self.rom[offset],
                    self.rom[offset + 1]
                    )

        raise NotImplementedError('no pkmn evolution')

    def set_evolution(self, pkmn, level=0):
        if pkmn == 0xB0:
            self.rom[offset]

    def parse_pokemons(self):
        from binascii import hexlify
        pkmns = []
        for index in range(self.TOTAL_PKMN_SLOTS):
            offset = self.PKMN_NAMES_OFFSET + index * 10
            raw = self.rom[offset:offset + 10]
            name = self.decode_text(raw)
            pkmns.append(Pokemon(id=index + 1, name=name))
        self.pokemons = pkmns

        return self.pokemons

    def parse_moves(self):
        moves = []
        index = 0
        offset = self.MOVES_OFFSET

        while index < self.TOTAL_MOVES:
            eos = self.rom.find(b'\x50', offset)
            move_name = self.decode_text(self.rom[offset:eos])
            moves.append(move_name)
            offset = eos + 1
            index += 1

        self.moves = moves
        self.move_names_upper_limit = offset

    def decode_text(self, data):
        chars = []
        for c in data:
            if c == b'\xe0':
                chars.append("'")
            elif c == b'\xe8':
                chars.append('.')
            elif c == b'\xef':
                chars.append(b'♂')
            elif c == b'\xf5':
                chars.append(b'♀')
            elif c == b'\x50':
                pass
            elif c== b'\xba':
                chars.append(b'É')
            elif c == b'\x7F':
                chars.append(b' ')
            elif ord(c) >= 0x80 and ord(c) <= 0x99:
                chars.append(chr(ord(c) - 63))
            else:
                chars.append('[{:02X}]'.format(ord(c)))
                    
        return ''.join(chars)

    def parse_route_names(self):
        offset = self.ROUTE_NAMES_OFFSET
        names = []
        raw = self.rom[offset:offset + 100]
        text = self.decode_text(raw)
        print(raw)

    def parse_evolutions(self):
        if not self.pokemons:
            self.parse_pokemons()

        offset = self.EVO_OFFSET
        for pkmn_index in range(self.TOTAL_PKMN_SLOTS):
            evolutions = []
            learns = []
            pkmn = self.pokemons[pkmn_index]
            end_offset = self.rom.find(b'\x00', offset)
            if end_offset == -1:
                break

            while offset < end_offset:
                evo = Evolution()
                evo.type = ord(self.rom[offset])

                if evo.type == Evolution.LEVEL:
                    evo.level = ord(self.rom[offset + 1])
                    evo.into_id = ord(self.rom[offset + 2])
                    offset += 3
                elif evo.type == Evolution.STONE:
                    evo.stone_id = ord(self.rom[offset + 1])
                    evo.into_id = ord(self.rom[offset + 3])
                    offset += 4
                elif evo.type == Evolution.INTERCHANGE:
                    evo.into_id = ord(self.rom[offset + 2])
                    offset += 3

                evolutions.append(evo)

            offset += 1
            end_offset = self.rom.find(b'\x00', offset)
            if end_offset == -1:
                break

            while offset < end_offset:
                learn = Learn()
                learn.level = ord(self.rom[offset])
                learn.move_id = ord(self.rom[offset + 1])
                learns.append(learn)
                offset += 2

            offset += 1

            pkmn.learns = learns
            pkmn.evolutions = evolutions
            self.evos_upper_limit = offset

def open_game(filename):
    with open(filename, 'rb') as fp:
        data = fp.read()
        game = Game(data)
        return game

if __name__ == '__main__':
    game = open_game('pykemod/Pokemon Red.gb')
    game.parse_evolutions()
    for pkmn in game.pokemons:
        #print('{}'.format(pkmn.name))
        #print(pkmn.learns)
        pass
    print('PKMN from 0x{:06X} to 0x{:06X} ({} bytes)'.format(
        game.pkmn_names_range[0],
        game.pkmn_names_range[1],
        game.pkmn_names_range[1] - game.pkmn_names_range[0]
    ))

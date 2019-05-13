# -*- coding: utf8 -*-
from __future__ import absolute_import
from pykemod import graphics
from pykemod.pokemon import Pokemon, Evolution, Learn
from binascii import unhexlify


class Game:
    PKMN_NAMES_OFFSET = 0x1C21E
    PKMN_DESCRIPTIONS_OFFSET = 0xAC001
    # PKMN_DESCRIPTIONS_OFFSET = 0xAEC77
    TOTAL_PKMN_SLOTS = 190
    EVO_OFFSET = 242136
    TOTAL_MOVES = 165
    MOVES_OFFSET = 0xB0000
    ROUTE_NAMES_OFFSET = 0x71473
    LETTERS_OFFSET = 0x11A80
    DIALOGS_OFFSET = 0x0A4001
    TOTAL_CHARS = 128
    TOTAL_ROUTES = 53

    decode_map = [
        '?', '?', '?', '?', '?', '?', '?', '?', '?', '?', '?', '?', '?', '?', '?', '?', # 0
        '?', '?', '?', '?', '?', '?', '?', '?', '?', '?', '?', '?', '?', '?', '?', '?', # 16
        '?', '?', '?', '?', '?', '?', '?', '?', '?', '?', '?', '?', '?', '?', '?', '?', # 32
        '?', '?', '?', '?', '?', '?', '?', '?', '?', '?', '?', '?', '?', '?', '?', '?', # 48
        '?', '?', '?', '?', '?', '?', '?', '?', '?', '?', '?', '?', '?', '?', '?', '?', # 64
        '?', '?', '?', '?', '?', '?', '?', '?', '?', '?', '?', '?', '?', '?', '?', '?', # 80
        '?', '?', '?', '?', '?', '?', '?', '?', '?', '?', '?', '?', '?', '?', '?', '?', # 96
        '?', '?', '?', '?', '?', '?', '?', '?', '?', '?', '?', '?', '?', '?', '?', ' ', # 112
        'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', # 128
        'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', '?', '?', '?', '?', '?', '?', # 144
        'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', # 160
        'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', 'É', '?', '?',"'s","'t", '?', # 176
        '?', '?', '?', '?', '?', '?', '?', '?', '?', '?', '?', '?', '?', '?', '?', '?', # 192
        '?', '?', '?', '?', '?', '?', '?', '?', '?', '?', '?', '?', '?', '?', '?', '?', # 208
        "'", '?', '?', '?',"'r", '?', '?', '!', '.', '?', '?', '?', '?', '?', '?', '♂', # 224
        '?', '?', '?', '?', '?', '♀', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', # 240
    ]

    # EXPERIMENTAL
    # RATATA LEVEL 3
    # 1048576
    # Pikachu in Forest, level 3
    # 54554 - 54725

    def __init__(self, rom):
        self.rom = rom
        self.pokemons = []
        self.pkmn_names_range = (
            self.PKMN_NAMES_OFFSET,
            self.PKMN_NAMES_OFFSET + 10 * self.TOTAL_PKMN_SLOTS,
        )
        self.evos_upper_limit = -1
        self.move_names_upper_limit = -1
        self.routes_names_upper_limit = -1
        self.pokemon_descriptions_upper_limit = -1
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
        desc_offset = self.PKMN_DESCRIPTIONS_OFFSET

        for index in range(self.TOTAL_PKMN_SLOTS):
            offset = self.PKMN_NAMES_OFFSET + index * 10

            raw = self.rom[offset:offset + 10]
            pkmn = Pokemon(
                id=index + 1,
                name=self.decode_text(raw),
            )

            # Description
            desc_end = self.rom.index(b'\x00', desc_offset)
            if desc_end != -1:
                raw = self.rom[desc_offset:desc_end]
                pkmn.description = self.decode_text(raw)
                desc_offset = desc_end + 1

            pkmns.append(pkmn)

        self.pokemon_descriptions_upper_limit = desc_offset
        self.pokemons = pkmns
        return self.pokemons

    def get_text(self, offset, ends=b'\x00'):
        end_offset = self.rom.index(ends, offset)
        if end_offset != -1:
            raw = self.rom[offset:end_offset]
            text = self.decode_text(raw)
            return text, end_offset + len(ends)
        else:
            return None, offset

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
            """ Numbers: 0-9 """
            if c == b'\x54':
                chars.append('(')
                chars.append('P')
                chars.append('O')
                chars.append('K')
                chars.append('É')
                chars.append(')')
            else:
                cc = self.decode_map[ord(c)]
                if cc != '?':
                    chars.append(cc)
                else:
                    chars.append('[{:02X}]'.format(ord(c)))
                    
        return ''.join(chars)

    def parse_route_names(self):
        offset = self.ROUTE_NAMES_OFFSET
        final_offset = self.rom.index(b'\x00', offset)
        names = []

        # print('routes: 0x{:04X}-0x{:04X}'.format(offset, final_offset))

        if final_offset == -1:
            raise ValueError('end not found')

        for index in range(1, self.TOTAL_ROUTES + 1):
            end_offset = self.rom.index(b'\x50', offset)
            if end_offset != -1:
                raw = self.rom[offset:end_offset]
                text = self.decode_text(raw)
                offset = end_offset + 1
                # print("{:02X} {}".format(index, text))
            else:
                break

        self.routes_names_upper_limit = offset

    def parse_pokemon_descriptions(self):
        offset = self.PKMN_DESCRIPTIONS_OFFSET        
        texts = []

        while True:
            end_offset = self.rom.index('\x00', offset)
            raw = self.rom[offset:end_offset]
            text = self.decode_text(raw)
            if text:
                texts.append(text)
                offset = end_offset + 1
            else:
                break

        self.long_texts_upper_limit = offset + 1

        return texts

    def parse_string_table(self, offset):
        texts = []
        text = ''
        while True:
            text, offset = self.get_text(offset)
            if text:
                texts.append(text)
            else:
                break
        return texts

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
    game.parse_pokemon_descriptions()
    game.parse_evolutions()
    # game.parse_route_names()
    game.parse_moves()
    for pkmn in game.pokemons:
        #print('{}'.format(pkmn.name))
        #print(pkmn.learns)
        pass
    print('PKMN from 0x{:06X} to 0x{:06X} ({} bytes)'.format(
        game.pkmn_names_range[0],
        game.pkmn_names_range[1],
        game.pkmn_names_range[1] - game.pkmn_names_range[0]
    ))

    print('MOVES\n---------- (To: {:04X})'.format(game.move_names_upper_limit))
    for index, move in enumerate(game.moves):
        print('{:02X} {}'.format(index + 1, move))
        pass

    print(game.decode_text(unhexlify('EA3ECD3E')))
    dialogs = game.parse_string_table(0x054001)
    for index, dialog in enumerate(dialogs):
        #print("{:02X} {}".format(index, dialog))
        pass

    print('\nPOKEMONS\n-----------')
    pokemons = game.parse_pokemons()
    for index, pkmn in enumerate(pokemons):
        print("{:02X} {}".format(index + 1, pkmn.name))
        pass
        #print(pkmn.description)



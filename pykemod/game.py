# -*- coding: utf8 -*-
from __future__ import absolute_import
from pykemod import graphics
from pykemod.pokemon import Pokemon, Evolution, Learn, WildData
from binascii import unhexlify, hexlify


class Game:
    # PKMN_DESCRIPTIONS_OFFSET = 0xAEC77
    TOTAL_PKMN_SLOTS = 190
    TOTAL_MOVES = 165
    TOTAL_CHARS = 128
    TOTAL_ROUTES = 53
    TOTAL_ITEMS = 83
    TOTAL_MAP_SPRITES = 93
    TOTAL_MAP_TILES = 128

    TOTAL_HOUSE_SPRITES = 72

    # Offsets
    ITEMS_NAMES_OFFSET       = 0x0472b # ~0x04abc
    WILD_OFFSET              = 0x0D0DF # ~0x0d2ad - then 
    WILD_OFFSET_B            = 0x0D2B1
    WILD_OFFSET_C            = 0x0D36A
    WILD_OFFSET_D            = 0x0D3FC
    CHARACTERS_OFFSET        = 0x11A80 # ~0x11e80
    # 41886 bytes
    PKMN_NAMES_OFFSET        = 0x1C21E
    EVO_OFFSET               = 0x3b1d8

    # Outdoors
    MAP_SPRITES_OFFSET       = 0x64010
    MAP_TILES_OFFSET         = 0x645E0

    # Indoors
    HOUSE_SPRITES_OFFSET     = 0x64df0
    HOUSE_MAP_TILES_OFFSET   = 0x65270

    # Houses 2
    HOUSE_2_SPRITES_OFFSET   = 0x653b0
    HOUSE_2_MAP_TILES_OFFSET = 0x65980
    # 0x65bb0: 47,299 bytes

    # 50835 bytes
    ROUTE_NAMES_OFFSET       = 0x71473 # ~0x716bd
    # 207,172 bytes
    DIALOGS_OFFSET           = 0xA4001
    PKMN_DESCRIPTIONS_OFFSET = 0xAC001
    MOVES_OFFSET             = 0xB0000


    decode_map = [
        '?', '?', '?', '?', '?', '?', '?', '?', '?', '?', '?', '?', '?', '?', '?', '?', # 0
        '?', '?', '?', '?', '?', '?', '?', '?', '?', '?', '?', '?', '?', '?', '?', '?', # 16
        '?', '?', '?', '?', '?', '?', '?', '?', '?', '?', '?', '?', '?', '?', '?', '?', # 32
        '?', '', '', '', '?', '?', '?', '?', '?', '?', '?', '?', '?', '?', '?', '?', # 48
        '?', '?', '?', '?', '?', '?', '?', '?', '?', '?', '?', '?', '?', '?', '?', '?', # 64
         '', '?', '?', '?', '?', '?', '?', '?', '?', '?', '?', '?', '?', '?', '?', '?', # 80
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
        pass
        # if pkmn == 0xB0:
        #     self.rom[offset]

    def extract_strings(self,
        offset: int,
        length: int = 50,
        decode_text: bool = False,
    ) -> list[str]|list[bytearray]:
        strings = []
        while len(strings) < length:
            ending = self.rom.index(0x50, offset)
            raw = self.rom[offset:ending]
            if decode_text:
                decoded = self.decode_text(raw)
                strings.append(decoded)
            else:
                strings.append(raw)
            offset = ending + 1
        return strings
    
    def extract_items_names(self) -> list[bytearray]:
        return self.extract_strings(self.ITEMS_NAMES_OFFSET, length=83)

    def parse_pokemons(self, decode_text=True):
        pkmns = []
        desc_offset = self.PKMN_DESCRIPTIONS_OFFSET

        for index in range(self.TOTAL_PKMN_SLOTS):
            offset = self.PKMN_NAMES_OFFSET + index * 10

            raw = self.rom[offset:offset + 10]
            pkmn = Pokemon(
                id=index + 1,
                name=self.decode_text(raw)\
                     if decode_text else self.cleanup_text(raw),
            )

            # Description
            desc_end = self.rom.index(b'\x00', desc_offset)
            if desc_end != -1:
                raw = self.rom[desc_offset:desc_end]
                pkmn.description = self.decode_text(raw)\
                    if decode_text else raw
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

    def get_cstring(self, offset, ends=b'\x00'):
        end_offset = self.rom.index(ends, offset)
        if end_offset != -1:
            s = self.rom[offset:end_offset]
            return s, end_offset + len(ends)
        else:
            return None, offset

    def parse_moves(self, decode_text=True):
        moves = []
        index = 0
        offset = self.MOVES_OFFSET

        while index < self.TOTAL_MOVES:
            eos = self.rom.find(b'\x50', offset)
            if decode_text:
                move_name = self.decode_text(self.rom[offset:eos])
            else:
                move_name = self.cleanup_text(self.rom[offset:eos])
            moves.append(move_name)
            offset = eos + 1
            index += 1

        self.moves = moves
        self.move_names_upper_limit = offset

        return self.moves

    def parse_wild(self, offset=WILD_OFFSET):
        choices = []
        total_items = 21
        current = 0

        while True:
            block, new_offset = self.get_cstring(offset)

            if block:
                block_size = len(block)
                wild = WildData()
                wild.offset = offset
                wild.rate = block[0]
                wild.choices = [(block[index * 2 + 1],
                                 block[index * 2 + 2],)
                    for index in range(int((block_size - 1) / 2))
                ]
                wild.calculate_chances()
                choices.append(wild)
                offset = new_offset
            elif block == '':
                choices.append(None)
                offset = new_offset
            
            current += 1
            
            if current >= total_items:
                break

        return choices

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
                cc = self.decode_map[c]
                if cc != '?':
                    chars.append(cc)
                else:
                    chars.append('[{:02X}]'.format(c))
                    
        return ''.join(chars)

    def cleanup_text(self, text):
        index_end = text.find(b'\x50')
        if index_end != -1:
            return text[:index_end]
        return text

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
                print(f"length = {len(raw)} (ending: {end_offset})")
            else:
                break

        self.routes_names_upper_limit = offset

    def pseudo_encode_text(self, text) -> bytes:
        return bytearray([self.decode_map.index(ch) for ch in text])

    def parse_places_names(self):
        names = []

        offset = self.ROUTE_NAMES_OFFSET

        for _ in range(0, self.TOTAL_ROUTES):
            end_offset = self.rom.index(b'\x50', offset)
            names.append(self.rom[offset:end_offset])
            offset = end_offset + 1

        return names

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
                evo.type = self.rom[offset]

                if evo.type == Evolution.LEVEL:
                    evo.level = self.rom[offset + 1]
                    evo.into_id = self.rom[offset + 2]
                    offset += 3
                elif evo.type == Evolution.STONE:
                    evo.stone_id = self.rom[offset + 1]
                    evo.into_id = self.rom[offset + 3]
                    offset += 4
                elif evo.type == Evolution.INTERCHANGE:
                    evo.into_id = self.rom[offset + 2]
                    offset += 3

                evolutions.append(evo)

            offset += 1
            end_offset = self.rom.find(b'\x00', offset)
            if end_offset == -1:
                break

            while offset < end_offset:
                learn = Learn()
                learn.level = self.rom[offset]
                learn.move_id = self.rom[offset + 1]
                learns.append(learn)
                offset += 2

            offset += 1

            pkmn.learns = learns
            pkmn.evolutions = evolutions
            self.evos_upper_limit = offset

    def parse_map_from(self, offset):
        height = self.rom[offset]
        width = self.rom[offset + 1]
        portals = []
        messages = []
        tiles = []

        offset += 2

        offset_map_x = self.rom[offset]
        offset_map_y = self.rom[offset + 1]
        offset += 2

        text_offsets = self.rom[offset:offset + 2]
        offset += 2

        other_offset = self.rom[offset:offset + 2]
        offset += 3

        up_map_id = self.rom[offset]
        up_map_offset = self.rom[offset + 1]

        offset += 2

        algo_de_arriba = self.rom[offset]
        relleno_arriba = self.rom[offset + 1]
        offset_mapa_arriba = self.rom[offset + 2]
        mas_relleno_arriba = self.rom[offset + 3]
        mas_relleno_arriba_2 = self.rom[offset + 4]
        que = self.rom[offset + 5]
        offset += 5

        # TODO: do not move to fixed offset, because for now
        # i'm seeking to relative offset 34, where are portals.
        offset = offset + 28

        portal_counter = self.rom[offset]
        offset += 1

        for index in range(portal_counter):
            portals.append((
                self.rom[offset], # X
                self.rom[offset + 1], # Y
                self.rom[offset + 2], # SPAWN IN
                self.rom[offset + 3], # MAP
            ))
            offset += 4

        messages_counter = self.rom[offset]
        offset += 1

        for index in range(messages_counter):
            messages.append((
                self.rom[offset], # Y
                self.rom[offset + 1], # X
                self.rom[offset + 2], # MESSAGE ID
            ))
            offset += 3

        # TODO: discover what is there in 99038
        offset += 7
        datalen = width * height

        for index in range(datalen):
            tiles.append(self.rom[offset])
            offset += 1

        print('SIZE: {}x{}'.format(width, height))
        print('MAP OFFSET XY: 0x{:02x},0x{:02x}'.format(
            offset_map_x, offset_map_y)
        )
        print('MAP UP OFFSET: {0} (0x{0:02x})'.format(up_map_offset))
        print("MAP UP ID: {0} (0x{0:02x})".format(up_map_id))
        print('TEXT OFFSET: {}'.format(hexlify(text_offsets)))
        print("portals: \n{}\n".format(portals))
        print("messages: \n{}\n".format(messages))
        print("tiles: \n{}\n".format(tiles))

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
        print("{:02X} {}".format(index, dialog))
        pass

    print('\nPOKEMONS\n-----------')
    pokemons = game.parse_pokemons()
    for index, pkmn in enumerate(pokemons):
        print("{:02X} {}".format(index + 1, pkmn.name))
        pass
        #print(pkmn.description)



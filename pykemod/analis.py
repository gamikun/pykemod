from struct import unpack
from binascii import hexlify




NAMES_OFFSET = 0x1C21E
TOTAL_PKMN_SLOTS = 190
ITEMS_NAMES_OFFSET = 18219
TOTAL_ITEMS = 83
MOVES_OFFSET = 720896 #263673
TOTAL_MOVES = 165
EVOLUTIONS_OFFSET = 242136

class Evolution(object):
    NO = 0
    LEVEL = 1
    STONE = 2
    INTERCHANGE = 3

    __slots__ = ['type', 'into_id', 'level', 'stone_id']


class Learn(object):
    __slots__ = ['move_id', 'level']

    def __str__(self):
        return '   LVL {}: {}'.format(
            self.level,
            moves[self.move_id - 1]
        )


class Pokemon(object):
    __slots__ = [
        'id', 'evolutions', 'learns', 'name',
    ]

    def __init__(self, **k):
        self.evolutions = k.get('evolutions', [])
        self.id = k.get('id', None)
        self.learns = k.get('learns', [])

pokemons = [Pokemon(id=index + 1) for index in range(TOTAL_PKMN_SLOTS)]
items = []
moves = []

with open('/Users/lizet/Library/Application Support/OpenEmu/Game Library/roms/Game Boy/Pokemon Red.gb', 'rb') as fp:
    game = fp.read()

text = b'BULBASAUR'
dif = [ord(text[0]) - ord(c) for c in text]

def guess(c):
    return b''.join([chr(ord(c) - d) for d in dif])

lower_limit = ord(min(text))

# Encontrar por linguistica
"""for index in range(lower_limit, lower_limit + 100):
    what = guess(chr(index))
    in_index = game.find(what)
    if in_index != -1:
        print(in_index, index)
        break
"""

def find_text(text):
    upper = range(65, 91)
    tofind = b''.join([
        b'\x7F' if c == b' ' else chr(ord(c) + 63)
        for c in text
    ])
    index = game.find(tofind)
    return index

# print(find_text('TACKLE'))

def decode_text(data):
    chars = []
    for c in data:
        if c == b'\x7F':
            chars.append(b' ')
        else:
            try:
                chars.append(chr(ord(c) - 63))
            except ValueError:
                chars.append('[{:02X}]'.format(ord(c)))
    return ''.join(chars)

def parse_pkmn_names():
    names = [''] * (TOTAL_PKMN_SLOTS)
    for index in range(TOTAL_PKMN_SLOTS):
        offset = NAMES_OFFSET + index * 10
        raw = game[offset:offset + 10]
        name = [chr(ord(c) - 63) for c in raw]
        names[index] = ''.join(name)
    return names

for index, name in enumerate(parse_pkmn_names()):
    pokemons[index].name = name

"""
spearrow = Evolution.from_bytes(game[0x3B216:0x3B216 + 2], pkmn_id=5)
clefairy = Evolution.from_bytes(game[0x3B1F7:0x3B1F7 + 2], pkmn_id=0x04)
charmander = Evolution.from_bytes(game[0x3B939:0x3B939 + 2], pkmn_id=0xB0)
"""

item_name = []
offset = ITEMS_NAMES_OFFSET
item_index = 0

print('\n--- ITEMS ---')
while item_index < TOTAL_ITEMS:
    eos = game.find(b'\x50', offset)
    name = decode_text(game[offset:eos])
    print("{:02X} {}".format(
        item_index + 1,
        name,
    ))
    items.append(name)
    offset = eos + 1
    item_index += 1

offset = MOVES_OFFSET
move_index = 0

print('\n--- MOVES ---')
while move_index < TOTAL_MOVES:
    eos = game.find(b'\x50', offset)
    move_name = decode_text(game[offset:eos])
    print("{:02X} {}".format(
        move_index + 1,
        move_name,
    ))
    moves.append(move_name)
    offset = eos + 1
    move_index += 1

offset = EVOLUTIONS_OFFSET


for pkmn_index in range(TOTAL_PKMN_SLOTS):
    evolutions = []
    learns = []
    pkmn = pokemons[pkmn_index]
    end_offset = game.find(b'\x00', offset)
    if end_offset == -1:
        break

    while offset < end_offset:
        evo = Evolution()
        evo.type = ord(game[offset])

        if evo.type == Evolution.LEVEL:
            evo.level = ord(game[offset + 1])
            evo.into_id = ord(game[offset + 2])
            offset += 3
        elif evo.type == Evolution.STONE:
            evo.stone_id = ord(game[offset + 1])
            evo.into_id = ord(game[offset + 3])
            offset += 4
        elif evo.type == Evolution.INTERCHANGE:
            evo.into_id = ord(game[offset + 2])
            offset += 3

        evolutions.append(evo)

    offset += 1
    end_offset = game.find(b'\x00', offset)
    if end_offset == -1:
        break

    while offset < end_offset:
        learn = Learn()
        learn.level = ord(game[offset])
        learn.move_id = ord(game[offset + 1])
        learns.append(learn)
        offset += 2

    offset += 1

    pkmn.learns = learns
    pkmn.evolutions = evolutions

for pkmn in pokemons:
    print("{:02X} {}".format(
        pkmn.id,
        pkmn.name,
    ))
    if pkmn.evolutions:
        for evo in pkmn.evolutions:
            if evo.type == Evolution.LEVEL:
                print('  LVL {} -> {}'.format(
                    evo.level,
                    pokemons[evo.into_id - 1].name,
                ))
            elif evo.type == Evolution.STONE:
                print('  With {} -> {}'.format(
                    items[evo.stone_id - 1],
                    pokemons[evo.into_id - 1].name,
                ))
            elif evo.type == Evolution.INTERCHANGE:
                print('  When interchange -> {}'.format(
                    pokemons[evo.into_id - 1].name
                ))
            else:
                import sys
                print('waaaaaat')
                sys.exit(0)
    if pkmn.learns:
        for learn in pkmn.learns:
            print('  LVL {} learns {}'.format(
                learn.level,
                moves[learn.move_id - 1],
            ))

 
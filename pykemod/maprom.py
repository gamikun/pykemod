from PIL import Image
from pykemod.game import open_game
import numpy as np

BASICS_COLOR = (255,0,0)

def maprom(game):
    data = np.array([255 for i in range(1024*1024*3)], dtype=np.dtype('B'))
    data[0x1D203*3:0x1D203*3+3] = BASICS_COLOR # Nivel de pokemon inicial
    data[0x1D10E*3:0x1D10E*3+3] = BASICS_COLOR # Pokemon inicial A
    data[0x1D11F*3:0x1D11F*3+3] = BASICS_COLOR # Pokemon inicial B
    data[0x1D130*3:0x1D130*3+3] = BASICS_COLOR # Pokemon inicial C

    # PKMN names
    fill_range(data, *game.pkmn_names_range)

    # PKMN evolutions
    fill_range(data, game.EVO_OFFSET, game.evos_upper_limit)

    # MOVES names
    fill_range(data, game.MOVES_OFFSET, game.move_names_upper_limit)

    # Characters sprites
    fill_range(data, 0x14000, 0x17800)

    # Letters map
    fill_range(data, game.CHARACTERS_OFFSET,
        game.CHARACTERS_OFFSET + game.TOTAL_CHARS * 8,
        color=(0, 0x99, 0)
    )

    # More stuff (to be checked)
    fill_range(data, 0x11e80, 0x11e80 + 199 * 8,
        color=(0, 0, 0xff)
    )

    # KAnto Tiles
    fill_range(data, 0x124b8, 0x124b8 + 32 * 8, color=(255, 0, 255))

    # Map tiles
    fill_range(data, 0x64190, 0x64550, color=(0, 0, 255))

    # Map tiles tiles
    fill_range(data, 0x0645E0, 0x064DE1, color=(192, 64, 15))

    # Route pokemons
    fill_range(data,
        game.ROUTE_NAMES_OFFSET,
        game.evos_upper_limit,
        color=(128, 0, 255)
    )

    # First character 
    fill_range(data,
        0x10000,
        0x11140
    )

    # Movable objects in map
    fill_range(data,
        0x11140,
        0x11380
    )

    # Pokemon Logo
    fill_range(data,
        0x11380,
        0x11a80,
        color=(0xff, 0xff, 0x00)
    )

    # Long Texts
    fill_range(data,
        game.PKMN_DESCRIPTIONS_OFFSET,
        game.pokemon_descriptions_upper_limit,
        color=(0xff, 0x88, 0x00),
    )

    # Pokemon descriptions
    fill_range(data, 0x0A8001, 0x0A8330)

    # Some templated strings
    fill_range(data, 0x0A4001, 0x0A6B94)

    # Red intro sprite
    fill_range(data, 0x126A8, 0x128D8)

    # Empty
    empty = (0xCC, 0xCC, 0xCC)

    # Dialogs
    fill_range(data, 0x0A0001, 0x0A2A37, color=(0,0xcc,0))
    fill_range(data, 0x09C001, 0x09EAA4, color=(0,0,0xff))
    
    fill_range(data, 0x0427F3, 0x044001, color=empty)
    fill_range(data, 0x0470AB, 0x048001, color=empty)
    fill_range(data, 0x04A38F, 0x04C000, color=empty)
    fill_range(data, 0x052A42, 0x054001, color=empty)
    fill_range(data, 0x056A4B, 0x058001, color=empty)
    fill_range(data, 0x05A5BA, 0x05C000, color=empty)
    fill_range(data, 0x05DF15, 0x060000, color=empty)
    fill_range(data, 0x06252A, 0x064010, color=empty)
    fill_range(data, 0x073B9D, 0x074000, color=empty)
    fill_range(data, 0x07687B, 0x078000, color=empty)
    fill_range(data, 0x081EF7, 0x084001, color=empty)
    fill_range(data, 0x086CA1, 0x088001, color=empty)
    fill_range(data, 0x08ACF9, 0x08C001, color=empty)
    fill_range(data, 0x08EC09, 0x090001, color=empty)
    
    fill_range(data, 0x09AB7B, 0x09C001, color=empty)
    fill_range(data, 0x09EAA4, 0x0A0001, color=empty)
    fill_range(data, 0x0AF838, 0x0B0000, color=empty)
    fill_range(data, 0x0A8330, 0x0AC001, color=empty)
    fill_range(data, 0x0A6B94, 0x0A8001, color=empty)
    fill_range(data, 0x0A2A37, 0x0A4001, color=empty)
    fill_range(data, 0x0B060F, 0x100000, color=empty)

    # PALLET TOWN
    fill_range(data, 0x0182FB, 0x18355)

    # VIRIDIAN CITY
    fill_range(data, 0x0183ea, 0x0183ea + 20 * 18)

    # PEWER CITY
    fill_range(data, 0x0185e4, 0x0185e4 + 20 * 18)

    # CERULEAN CITY
    fill_range(data, 0x01882e, 0x01882e + 20 * 18)

    # LAVENDER TOWN
    fill_range(data, 0x018a3d, 0x018a3d + 20 * 18)

    # VERMILION CITY
    fill_range(data, 0x018c84, 0x018c84 + 20 * 18)

    # ROUTE 1
    fill_range(data, 0x01C0FA, 0x01C0FA + 10 * 18)

    # PKMN WILD
    fill_range(data, game.WILD_OFFSET, 0x00D5C6, color=(0x99, 0, 0x99))

    # print('UNTIL ROUTE NAMES: {}'.format(game.evos_upper_limit))

    im = Image.frombytes('RGB', (1024, 1024), data)
    return im

def fill_range(arr, begin, ends, color=(255,0,0)):
    for offset in range(begin, ends):
        arr[offset * 3:offset * 3 + 3] = color

if __name__ == '__main__':
    game = open_game('pokemon-red.gb')
    game.parse_evolutions()
    game.parse_moves()
    game.parse_route_names()
    game.parse_pokemons()
    image = maprom(game)
    image.save('maprom.png')
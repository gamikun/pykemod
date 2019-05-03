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
    fill_range(data, game.LETTERS_OFFSET,
        game.LETTERS_OFFSET + game.TOTAL_CHARS * 8,
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

    im = Image.frombytes('RGB', (1024, 1024), data)
    return im

def fill_range(arr, begin, ends, color=(255,0,0)):
    for offset in range(begin, ends):
        arr[offset * 3:offset * 3 + 3] = color

if __name__ == '__main__':
    game = open_game('Pokemon Red.gb')
    game.parse_evolutions()
    game.parse_moves()
    game.parse_route_names()
    image = maprom(game)
    image.save('maprom.png')
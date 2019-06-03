from __future__ import division
from pykemod.game import open_game
import sys
import os

env = os.environ

if sys.argv[1] == 'pkmn' and sys.argv[2] == 'list':
    """ List of pokemos """
    filename = env.get('PKMN_FILE', 'pykemod/Pokemon Red.gb')
    game = open_game(filename)
    game.parse_pokemons()
    for index, pkmn in enumerate(game.pokemons):
        print("{:02X} {}".format(index + 1, pkmn.name))

elif sys.argv[1] == 'wild' and sys.argv[2] == 'list':
    filename = env.get('PKMN_FILE', 'pykemod/Pokemon Red.gb')
    game = open_game(filename)
    game.parse_pokemons()
    wild = game.parse_wild()
    for index, wblock in enumerate(wild):
        if wblock:
            print('\nBLOCK {} | 0x{:06X} {:.02f}% (DEC {})\n{}'\
                .format(
                    index + 1,
                    wblock.offset,
                    (wblock.rate / 256) * 100,
                    wblock.rate,
                    '-' * 35
                )
            )
            for k, c in wblock.chances.items():
                lvl, pkmn_id = k
                pkmn = game.pokemons[pkmn_id - 1]
                print("{}% {:02X} {:<10} LVL {}".format(
                    int(c * 100), pkmn_id, pkmn.name, lvl)
                )
        else:
            print('\nBLOCK {}: EMPTY\n{}'.format(index + 1, '-' * 35))


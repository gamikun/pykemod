if __name__ == '__main__':
    from argparse import ArgumentParser
    from pykemod.game import open_game
    from pykemod import graphics
    from os import environ as env

    parser = ArgumentParser()
    # parser.add_argument('game')
    parser.add_argument('entity')
    parser.add_argument('action')
    parser.add_argument('-i', dest='input')
    parser.add_argument('-o', dest='output')
    parser.add_argument('-t', dest='target')
    parser.add_argument('-offset', dest='offset', type=int)
    parser.add_argument('-game', dest='game',
        default=env.get('PYKEMOD_GAME', None)
    )
    args = parser.parse_args()

    if args.entity == 'sprite':
        if args.action == 'replace':
            game = open_game(args.game)
            target = args.target
            filename = args.input
            rawdata = game.get_segment(int(args.target), 64)
            image = graphics.image16_from_raw(rawdata)
            image.save('error.png')

    elif args.entity == 'map':
        if args.action == 'parse-from':
            game = open_game(args.game)
            game.parse_map_from(args.offset)

    elif args.entity == 'mapshot':
        from PIL import Image
        
        with open('./bros.nes', 'rb') as f:
            data = f.read()
            image = Image.frombytes('RGB', (68, 68), data)
            image = image.resize((68 * 12, 68 * 12))
            image.save('mapshot-nes.png')

    elif args.entity == 'strings':
        if args.action == 'parse':
            game = open_game(args.game)
            strings = game.parse_string_table(0x054001)
            for string in strings:
                print(strings)






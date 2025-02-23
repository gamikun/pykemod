if __name__ == '__main__':
    from argparse import ArgumentParser
    from pykemod.game import open_game
    from pykemod import graphics
    from binascii import unhexlify, hexlify
    from os import environ as env

    parser = ArgumentParser()
    # parser.add_argument('game')
    parser.add_argument('entity')
    parser.add_argument('action')
    parser.add_argument('-i', dest='input')
    parser.add_argument('-o', dest='output')
    parser.add_argument('-t', dest='target')
    parser.add_argument('-text', type=str)
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
            strings = game.parse_string_table(args.offset if args.offset else 0x054001)
            for string in strings:
                print(strings)
        elif args.action == 'parse-fixed':
            game = open_game(args.game)
            strings = game.extract_strings(
                game.ITEMS_NAMES_OFFSET,
                length=83,
                decode_text=True,
            )
            for index, s in enumerate(strings):
                print(f"{index + 1:>3}: {s}")
        elif args.action == 'encode':
            game = open_game(args.game)
            encoded = game.pseudo_encode_text(args.text)
            print(hexlify(encoded))
        elif args.action == 'decode':
            game = open_game(args.game)
            decoded = game.decode_text(unhexlify(args.text))
            print(decoded)
        elif args.action == 'find':
            game = open_game(args.game)
            encoded = game.encoeargs.text

    elif args.entity == 'routes':
        game = open_game(args.game)
        routes = game.parse_route_names()




if __name__ == '__main__':
    from argparse import ArgumentParser
    from pykemod.game import open_game
    from pykemod import graphics

    parser = ArgumentParser()
    parser.add_argument('game')
    parser.add_argument('entity')
    parser.add_argument('action')
    parser.add_argument('-i', dest='input')
    parser.add_argument('-o', dest='output')
    parser.add_argument('-t', dest='target')
    args = parser.parse_args()

    if args.entity == 'sprite':
        if args.action == 'replace':
            game = open_game(args.game)
            target = args.target
            filename = args.input
            rawdata = game.get_segment(int(args.target), 64)
            image = graphics.image16_from_raw(rawdata)
            image.save('error.png')





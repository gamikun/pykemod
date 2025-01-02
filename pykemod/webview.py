from __future__ import absolute_import
from os.path import join, dirname
from base64 import b64decode, b64encode
from urllib.parse import parse_qs

from pykemod.game import Game
from pykemod.graphics import image16_from_raw, \
                             image8_from_raw, \
                             image8x8_from_bitmap1
from pykemod.pokemon import Pokemon, Evolution
from wsgiref.handlers import format_date_time
import email.utils as eut
from binascii import hexlify
from io import BytesIO
from PIL import Image
from struct import unpack
import time
import json

html_templete = """
<!doctype html>
<html>
<head>
    <title>Pykemod</title>
</head>
</html>
<body>
    {content}
    <script src="script.js"></script>
</body>
</html>
"""

palettes = [
    [ # 1bpp
        (0x00, 0x00, 0x00, 0x00),
        (0x00, 0x00, 0x00, 0xFF)
    ],
    [ # 2bpp
        (0xff,0xff,0xff,0xff), # blanco
        (0x00,0x00,0x00,0x00), # transparent
        (0x99,0x99,0x99,0xff), # gris
        (0x00,0x00,0x00,0xff), # negro
    ]
]

default_palette = [
    (0xff,0xff,0xff,0xff), # blanco
    (0x00,0x00,0x00,0x00), # transparent
    (0x99,0x99,0x99,0xff), # gris
    (0x00,0x00,0x00,0xff), # negro
]
tile_cache = {
    "outdoor": [None] * 129,
    "house": [None] * 129,
    "house_2": [None] * 129,
}

class state:
    charmap = None
    last_modified = None

class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(self, Pokemon):
            return ['POKEMON']
        return json.JSONEncoder.default(self, obj)

with open('/Users/soul/Library/Application Support/OpenEmu/Game Library/roms/Game Boy/pokemon-red.gb', 'rb') as fp:
    game = Game(fp.read())

def fromaddr(addr, do_print=False, bpp=2, palette=None):
    ar = []
    length = int((64 * bpp) / 8)
    tile = game.rom[addr:addr + length]

    if palette is None:
        palette = palettes[bpp - 1]

    for y in range(8):
        low = tile[y * bpp]
        if bpp == 2:
            high = tile[y * bpp + 1]
        for bn in range(7, -1, -1):
            p = (low >> bn) & 0x1
            if bpp == 2:
                p |= (high >> bn) << 1
                p &= 0x3
            ar.append(palette[p])

    image = Image.new('RGBA', (8, 8))
    image.putdata(ar)

    return image

def get_charmap() -> list[bytes]:
    charmap = []
    offset = game.CHARACTERS_OFFSET
    for _ in range(256):
        achar = get_sprite(offset, (8, 8), bpp=1)
        with BytesIO() as output:
            achar.save(output, format="PNG")
            charmap.append(output.getvalue())
        offset += 8
    return charmap

def get16x16(addr, scale=1):
    image = Image.new('RGBA', (16, 16))
    img1 = fromaddr(addr, do_print=True)
    img2 = fromaddr(addr + 16)
    img3 = fromaddr(addr + 32)
    img4 = fromaddr(addr + 48)
    image.paste(img1, (0, 0))
    image.paste(img2, (8, 0))
    image.paste(img3, (0, 8))
    image.paste(img4, (8, 8))

    return image

def get_sprite(addr, size, bpp=2, palette=None, scale=1):
    """ TODO: put in graphics submodule """
    w, h = size
    sw, sh = w / 8, h / 8
    pixel_count = w * h
    segments_count = int(pixel_count / 64)
    sprite = Image.new('RGBA', (w, h))
    segment_length = int((64 * bpp) / 8)

    for index in range(segments_count):
        y = int(index / sw) * 8
        x = int(index % sw) * 8
        offset = addr + index * segment_length
        segment = fromaddr(offset, bpp=bpp, palette=palette)
        sprite.paste(segment, (x, y))

    if scale > 1:
        return sprite.resize(
          (w * scale, h * scale),
          resample=Image.NEAREST,
        )

    return sprite

def get_map_tile(addr, palette=None, map_section="outdoor"):
    image = Image.new('RGBA', (32, 32))
    data = game.rom[addr:addr + 16]
    for index, spid in enumerate(data):
        spindex = spid - 1
        if spindex >= 129:
            continue
        if not tile_cache[map_section][spindex]:
            if map_section == "house":
                sprite_offset = game.HOUSE_SPRITES_OFFSET
            elif map_section == "house_2":
                sprite_offset = game.HOUSE_2_SPRITES_OFFSET
            else:
                sprite_offset = game.MAP_SPRITES_OFFSET
            tile_cache[map_section][spindex] = get_sprite(
                sprite_offset + 16 * spindex,
                (8, 8),
                palette=palette,
            )
        chunk = tile_cache[map_section][spindex]
        y = int(index / 4) * 8
        x = int(index % 4) * 8
        image.paste(chunk, (x, y))

    return image

def get_map_image(addr, palette=None, size=(10, 9), map_section="outdoor"):
    # 38 39 01 01 38 39 01 4D
    w = game.rom[addr] - 1
    h = game.rom[addr + 1]
    w, h = size
    image = Image.new('RGBA', (w * 32, h * 32),
        color=(0x00, 0x99, 0x00, 0xff)
    )
    offset = addr + 2
    n = w * h

    for index in range(w * h):
        tile_id = game.rom[offset + index]

        if map_section == "house_2":
            tiles_offset = game.HOUSE_2_MAP_TILES_OFFSET
        elif map_section == "house":
            tiles_offset = game.HOUSE_MAP_TILES_OFFSET
        else:
            tiles_offset = game.MAP_TILES_OFFSET

        tile = get_map_tile(tiles_offset + tile_id * 16,
            map_section=map_section,
            palette=palette
        )
        y = int(index / w) * 32
        x = int(index % w) * 32
        image.paste(tile, (x, y))

    return image

def first_adapter(qs):
    def _first_adapter(qs):
        return qs[0]
    return _first_adapter

def parse_palette(value):
    colors = [
        (
            int(color[0:2], 16),
            int(color[2:4], 16),
            int(color[4:6], 16),
            int(color[6:8], 16),
        )
        for color in value.split(',')
    ]
    return colors


def app(environ, start_response):
    path = environ.get('PATH_INFO')

    if path == '/script.js':
        start_response('200 OK', [('Content-Type', 'application/js')])
        with open(join(dirname(__file__), 'script.js')) as fp:
            return [fp.read()]

    if path == '/find-sprite/':
        json.loads(b64decode(path.split('/')[2]))

    #elif path == '/list-sprites':
    #    offset = 82304 - 64 * 8
    #    divs = []
    #    for i in range(8):
    #        pass
    #    start_response('200 OK', [('Content-Type', 'application/json')])
    #    return ['hola mundo']

    elif path == '/find-pattern':
        start_response('200 OK', [('Content-Type', 'text/html')])
        return [
            html_templete.format(content='')
        ]
    
    # elif path.startswith("/pkmn-names/"):
    #     pkmn_id = int(path.split("/")[-1].split(".")[0])
    #     start_response('200 OK', [('Content-Type', 'text/html')])
    #     return [json.dumps({"pkmn_id": pkmn_id}).encode()]

    elif path == '/char.png':
        qs = parse_qs(environ['QUERY_STRING'])
        c = int(qs.get('c', ['0'])[0])
        if_mod = environ.get('HTTP_IF_MODIFIED_SINCE', None)
        now = time.time()

        if if_mod and state.last_modified < now:
            start_response('304 Not Modified', [])
            return ['']

        start_response('200 OK', [
            ('Content-Type', 'image/png'),
            ('Cache-Control', 'public'),
            ('Last-Modified', format_date_time(state.last_modified)),
        ])
        return [state.charmap[c - 1]]

    elif path == '/pokemons.json':
        qs = parse_qs(environ['QUERY_STRING'])

        if not game.pokemons:
            game.parse_pokemons(decode_text=False)

        game.parse_evolutions()

        data = []
        for pokemon in game.pokemons:
            pkmn = {}
            data.append({
                "id": pokemon.id,
                "name": [n for n in pokemon.name],
                "description": [n for n in pokemon.description],
                "evolutions": [{
                    "into_id": e.into_id,
                    "type": e.type,
                    "level": e.level,
                    "stone_id": e.stone_id
                } for e in pokemon.evolutions],
                "learns": [{
                    "move_id": l.move_id,
                    "level": l.level   
                } for l in pokemon.learns]
            })

        start_response('200 OK', [('Content-Type', 'application/json')])
        return [json.dumps(data).encode()]
    
    elif path == '/items.json':
        qs = parse_qs(environ['QUERY_STRING'])
        items_names = [{
            "id": item_index + 1,
            "name": [x for x in y]
        } for item_index, y in enumerate(game.extract_items_names())]

        start_response('200 OK', [('Content-Type', 'application/json')])
        return [json.dumps(items_names).encode()]
    
    elif path == '/evolutions.json':
        qs = parse_qs(environ['QUERY_STRING'])

        if not game.pokemons:
            game.parse_pokemons(decode_text=False)

        items_names = game.extract_items_names()
        game.parse_evolutions()

        types_map = {
            Evolution.LEVEL: "Level",
            Evolution.STONE: "Stone",
            Evolution.INTERCHANGE: "Interchange",
        }

        data = []
        for pokemon in game.pokemons:
            if pokemon.evolutions:
                for evolution in pokemon.evolutions:
                    data.append({
                        "type": {
                            "id": evolution.type,
                            "description": types_map[evolution.type],
                        },
                        "level": evolution.level,
                        "stone": {
                            "id": evolution.stone_id,
                            "name": [x for x in items_names[evolution.stone_id - 1]],
                        } if evolution.stone_id else None,
                        "from_pokemon": {
                            "id": pokemon.id,
                            "name": [n for n in pokemon.name]
                        },
                        "to_pokemon": {
                            "id": evolution.into_id,
                            "name": [n for n in game.pokemons[evolution.into_id - 1].name]
                        }
                    })

        start_response('200 OK', [('Content-Type', 'application/json')])
        return [json.dumps(data).encode()]

    elif path == '/favicon.ico':
        start_response('200 OK', [('Content-Type', 'image/x-icon')])
        return [open('./pykemod/static/favicon.ico', 'rb').read()]

    elif path == '/moves.json':
        moves = game.parse_moves(decode_text=False)

        start_response('200 OK', [('Content-Type', 'application/json')])
        
        return [
            json.dumps({
                "moves": [[t for t in m] for m in moves]
            }).encode()
        ]

    elif path == '/places.json':
        names = game.parse_places_names()

        start_response('200 OK', [('Content-Type', 'application/json')])
        return [
            json.dumps({
                "names": [[t for t in m] for m in names]
            }).encode()
        ]

    elif path == '/wild.json':
        wild = game.parse_wild()

        start_response('200 OK', [('Content-Type', 'application/json')])

        return [
            json.dumps({
                "wild": [
                    {
                        "rate": w.rate,
                        "offset": w.offset,
                        "chances": [
                            {
                                "rate": v,
                                "pkmn_id": k[1],
                                "lvl": k[0]
                            } for k, v in w.chances.items()
                        ]
                    } if w else None for w in wild
                ]
            }).encode()
        ]

    elif path == '/sprite':
        qs = parse_qs(environ['QUERY_STRING'])
        scale = qs.get('scale', [1])[0]
        scale = int(scale) if scale else 1
        size = [int(x) for x in qs.get('size', '16,16')[0].split(',')]
        depth = int(qs.get('depth', [2])[0])
        offset = int(qs.get('aoffset')[0])
        map_section = qs.get('map_section', ["outdoor"])[0]
        is_map_tile = bool(int(qs.get('is_map_tile')[0]))
        is_map = bool(int(qs.get('is_map')[0]))
        palette = parse_palette(qs.get('palette')[0])\
                  if 'palette' in qs else None

        if is_map:
            size = [int(x) for x in qs.get('size', '10,9')[0].split(',')]
            image = get_map_image(offset,
                map_section=map_section,
                palette=[
                    (0xff,0xff,0xff,0xff), # blanco
                    (0xC0,0xc0,0xC0,0xff), # gris
                    (0x90, 0x90, 0x90, 0xff),
                    (0x00,0x00,0x00,0xff), # negro
                ],
                size=size
            )
        elif is_map_tile:
            image = get_map_tile(offset, map_section=map_section)
            
        else:
            image = get_sprite(offset, size,
                bpp=depth,
                scale=scale,
                palette=palette
            )

        io = BytesIO()
        io.seek(0)
        image.save('./super.png')
        image.save(io, format="png")
        io.seek(0)

        start_response('200 OK', [('Content-Type', 'image/png')])
        return [io.read()]

    elif path == '/':
        start_response('200 OK', [('Content-Type', 'text/html')])
        with open(join(dirname(__file__), 'static/index.html'), 'rb') as fp:
            return [fp.read()]

if __name__ == '__main__':
    port = 8912
    from wsgiref.simple_server import make_server
    
    game.parse_pokemons(decode_text=False)
    state.charmap = get_charmap()
    state.last_modified = time.time()

    server = make_server('', port, app)
    print('starting: http://localhost:{}'.format(port))
    server.serve_forever()
from __future__ import absolute_import
from os.path import join, dirname
from base64 import b64decode
from urlparse import parse_qs
from pykemod.game import Game
from pykemod.graphics import image16_from_raw, \
                             image8_from_raw, \
                             image8x8_from_bitmap1
from binascii import hexlify
from StringIO import StringIO
from PIL import Image
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
        #(0x00,0x00,0x00,0x00),
        (0xff, 0x00, 0xff, 0xff),
        (0xff,0xff,0xff,0xff),
        (0x99,0x99,0x99,0xff),
        (0x00,0x00,0x00,0xff),
    ]
]



with open('/Users/lizet/Library/Application Support/OpenEmu/Game Library/roms/Game Boy/Pokemon Red.gb', 'rb') as fp:
    game = Game(fp.read())

def fromaddr(addr, do_print=False, bpp=2):
    ar = []
    length = (64 * bpp) / 8
    tile = game.rom[addr:addr + length] 
    palette = palettes[bpp - 1]

    for y in range(8):
        low = ord(tile[y * bpp])
        if bpp == 2:
            high = ord(tile[y * bpp + 1])
        for bn in range(7, -1, -1):
            p = (low >> bn) & 0x1
            if bpp == 2:
                p |= (high >> bn) << 1
                p &= 0x3
            ar.append(palette[p])

    image = Image.new('RGBA', (8, 8))
    image.putdata(ar)

    return image

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

def get_sprite(addr, size, bpp=2):
    """ TODO: put in graphics submodule """
    w, h = size
    sw, sh = w / 8, h / 8
    pixel_count = w * h
    segments_count = pixel_count / 64
    sprite = Image.new('RGBA', (w, h))
    segment_length = (64 * bpp) / 8

    for index in range(segments_count):
        y = (index / sw) * 8
        x = (index % sw) * 8
        offset = addr + index * segment_length
        segment = fromaddr(offset, bpp=bpp)
        sprite.paste(segment, (x, y))

    return sprite

def first_adapter(qs):
    def _first_adapter(qs):
        return qs[0]
    return _first_adapter

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

    elif path == '/sprite':
        qs = parse_qs(environ['QUERY_STRING'])
        scale = qs.get('scale', None)
        scale = int(scale) if scale else 1
        size = [int(x) for x in qs.get('size', '16,16')[0].split(',')]
        depth = int(qs.get('depth', [2])[0])
        offset = int(qs.get('aoffset')[0])


        image = get_sprite(offset, size, bpp=depth)

        """
        if depth == 1:
            data = game.rom[offset:offset + 8]
            image = image8x8_from_bitmap1(data)
        else:
            if size == 16:
                image = get16x16(offset)
            elif size == 8:
                image = fromaddr(offset)
        """

        io = StringIO()
        io.seek(0)
        image.save('./super.png')
        image.save(io, format="png")
        io.seek(0)

        start_response('200 OK', [('Content-Type', 'image/png')])
        return [io.read()]

    elif path == '/':
        start_response('200 OK', [('Content-Type', 'text/html')])
        with open(join(dirname(__file__), 'static/index.html')) as fp:
            return [fp.read()]

if __name__ == '__main__':
    port = 8912
    from wsgiref.simple_server import make_server
    server = make_server('', port, app)
    print('starting: http://localhost:{}'.format(port))
    server.serve_forever()
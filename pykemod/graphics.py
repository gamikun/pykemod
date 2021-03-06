from PIL import Image
from binascii import hexlify

default_palette = [
    (0x00,0x00,0x00,0x00),
    (0xff,0xff,0xff,0xff),
    (0x99,0x99,0x99,0xff),
    (0x00,0x00,0x00,0xff),
]

default_reverse_palette = {\
    v: k for k, v \
         in enumerate(default_palette) \
}

palette = default_palette

def image8_from_raw(raw):
    """ Takes a segment of 16 bytes and creates
    an image of 8x8 pixels in size """
    
    bitmap = bitmap8_from_raw(raw)
    image = Image.new('RGBA', (8, 8))
    image.putdata(bitmap)

    return image

def bitmap8_from_raw(raw):
    ar = []

    for y in range(8):
        low = ord(raw[y * 2])
        high = ord(raw[y * 2 + 1])
        for bn in range(7, -1, -1):
            p = (low >> bn) & 0x1
            p |= (high >> bn) << 1
            p &= 0x03
            ar.append(palette[p])

    return ar

def image16_from_raw(raw):
    """ Takes a segment of 64 bytes and creates
    and image conformed of 4 images of 8x8 """

    bitmap = []
    image = Image.new('RGBA', (16, 16))

    for i in range(4):
        offset = i * 16
        segment = raw[offset:offset + 16]
        bm = bitmap8_from_raw(segment)
        bitmap += bm

    image.putdata(bitmap)

    return image

def image_from_raw(raw, size=8):
    if size == 8:
        return graphics.image8_from_raw(
            raw
        )
    elif size == 16:
        return graphics.image8_from_raw(
            raw
        )
    else:
        raise NotImplementedError('incorrect size')

def raw8_from_image(image):
    """ Takes an PIL.Image and convert it
    to an bytearray of lenght of 16. """

    rawdata = bytearray(16)
    imagedata = image.getdata()
    high = 0
    low = 0
    bn = 0

    for i, p in enumerate(data):
        c = default_reverse_palette[p]
        low  |= (c & 1) << 7 - bn
        high |= ((c & 2) >> 1) << 7 - bn
        if bn == 8:
            rawdata[i * 2] = low
            rawdata[i * 2 + 1] = high
            low = 0
            high = 0

    return rawdata

def raw8_from_image_16(image):
    """ Takes an PIL.Image and convert it
    to an bytearray of lenght of 16. """
    """ SNES """


    default_reverse_palette = {
        0x00: 0x00,
        0xFF: 0xFF,
    }

    rawdata = bytearray(16)
    imagedata = image.getdata()
    high = 0
    low = 0
    bn = 0

    for i, p in enumerate(rawdata):
        c = default_reverse_palette[p]
        low  |= (c & 2) << 6 - bn
        high |= ((c & 4) >> 1) << 6 - bn
        if bn == 8:
            rawdata[i * 4] = low
            rawdata[i * 4 + 1] = high
            low = 0
            high = 0

    return rawdata

def planar8x8_from_bitmap(bitmap):
    planar = bytearray(16)
    for index, bt in enumerate(bitmap):
        offset = (index >> 3) << 1
        bn = 7 - (index % 8)
        planar[offset + 0] |= (bt & 1) << bn
        planar[offset + 1] |= ((bt >> 1) & 1) << bn
    return planar

def bitmap_from_array(a):
    """ Given an array of numbers or bytearray, return a
    bitmap of 1 bit per pixel compatible with GB. """

    new_bitmap = bytearray(len(a) >> 3)
    for index, bt in enumerate(a):
        offset = index >> 3
        bn = 7 - (index % 8)
        new_bitmap[offset] |= (bt & 1) << bn
    return new_bitmap

def image8x8_from_bitmap1(bitmap):
    """ Given a bitmap of 1 bit per pixel in the
    gb format, returns an 4 channels tiff image """
    image = Image.new('RGBA', (8, 8))

    array = [(0, 0, 0, 0)] * len(bitmap) * 8
    for index in range(len(bitmap) * 8):
        bn = 7 - (index % 8)
        if (ord(bitmap[index >> 3]) >> bn) & 1:
            array[index] = (0, 0, 0, 255)

    image.putdata(array)
    return image
    

if __name__ == '__main__':
    result = bitmap1_from_array([
        # 0,0,0,0,0,0,0,0,
        0, 0, 0, 1, 0, 0, 0, 0,
        0, 0, 1, 0, 1, 0, 0, 0,
        0, 0, 1, 0, 1, 0, 0, 0,
        0, 1, 0, 0, 0, 1, 0, 0,
        0, 1, 1, 1, 1, 1, 0, 0,
        1, 0, 0, 0, 0, 0, 1, 0,
        1, 0, 0, 0, 0, 0, 1, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
    ])
    print(hexlify(result))
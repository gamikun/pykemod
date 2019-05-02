# -*- coding: utf-8 -*-
from PIL import Image
from binascii import hexlify
from cStringIO import StringIO
from struct import unpack
import numpy as np

with open('./pkmn-chars.txt', 'rb') as f:
  chars = [f.read(1) for i in range(256)]

with open("pkmn.txt") as f:
  pokemons = [l.replace('\n','') for l in f.readlines()]
n_pkmn = len(pokemons)

with open('./Pokemon Red.gb', 'rb') as f:
  sdata = f.read()
  data = np.array([ord(i) for i in sdata], dtype=np.dtype('B'))

def find_all_text(text):
  matches = []
  index = 0
  while True:
    index = find_text(text, start=index)
    if index != -1:
      matches.append(index)
      index += len(text)
    else:
      break
  return matches

def find_text(text, start=0):
  txt = ''
  for c in text:
    ic = ord(c)
    if ic >= ord('A') and ic <= ord('Z'):
      txt += chr(ic+63)
    else:
      txt += hexlify(ic)
  # encontrar
  return sdata.find(txt, start)

def get_string_from_position(position, length):
  text = ''
  for i in range(position, position+length):
    text += chr(data[i])
  return text

def from_pkmn_string(string):
  text = ''
  for s in string:
    if chars[ord(s)] == '?':
      text += '[' + hexlify(s) + ']'
    else:
      text += chars[ord(s)]
  return text

filename = "./Pokemon Red.gb"
f = open(filename, "rb")
f.seek(0x3AD89)
#f.seek(0x3B2B1)

"""
for i in range(255):
  pos = f.tell()
  lvl, pkmn = unpack('BB', f.read(2))
  f.seek(f.tell()+14)
  ultimo = ord(f.read(1))
  if pkmn != 0:
    print "%s (%d), nivel: %d ... valor: %d [%d]" % (pokemons[pkmn], pkmn, lvl, ultimo, pos)
"""

"""
f.seek(0x39010)
for i in range(190):
  spr,spr_b = unpack('BB', f.read(2))
  print "%s (spr: %d, %d)" % (pokemons[i], spr, spr_b)
"""

# CELADON (297264)
# PEWTER (377773)
# CERULEAN (378585)
# VERMILION (379477)
# SAFFRON (380979)
# PALLET (463987)
# VIRIDIAN (463999)
# FUCHSIA (464081)
# CINNABAR (464094)

# CELADON  [297264, 464068, 573732, 573784, 573882, 573919, 574113, 576945, 581260, 582260, 592126, 594742, 595755, 596135, 640645, 642924, 643859, 645217, 645958, 647663, 679171, 679193, 679234, 679299, 679338, 679465]
# PEWTER   [377773, 464013, 525952, 579422, 616840, 673139, 674352, 674964, 674994, 675020, 675085]
# CERULEAN [378585, 464025, 464548, 526569, 567614, 574047, 574916, 575425, 579508, 580601, 580633, 581211, 583207, 607684, 622704, 659633, 676648, 676763, 676934]
# VERMILION[379477, 464053, 531337, 578803, 580649, 581227, 594360, 606911, 640240, 678084, 678108, 678255, 678311, 678378]
# SAFFRON  [380979, 464125, 543002, 568099, 573996, 581769, 581931, 640114, 640201, 664095, 664184, 680762, 681064, 681336, 681398]
# PALLET   [463987, 577383, 579330, 579369, 613484, 672652]
# VIRIDIAN [463999, 464366, 477375, 525936, 567418, 575547, 579080, 579383, 579406, 579560, 580895, 615358, 615544, 648189, 672885, 673188, 673844, 674122]
# FUCHSIA  [464081, 480357, 530553, 592945, 594036, 594347, 594757, 594949, 595770, 596150, 597066, 643718, 656616, 679834, 679954]
# CINNABAR [464094, 481147, 526917, 597749, 597833, 597844, 597895, 657514, 678416, 680423, 680551, 680611]

# Posible cuarto de RED
# Teoria 1. 0 = bloqueado
# 0000 0000 = 00
# 0001 1111 = 1F
# 1111 1111 = FF

# 0111 1101 = 7D
# 0111 1101 = 7D
# 1110 1111 = EF

# 1000 0010 = 82
# 1000 0010 = 82
# 0001 0000 = 10

# Teoria 2. 1 = bloqueado
# 1111 1111 = FF
# 1110 0000 = 07
# 0000 0000 = 00

# Teoría 3 (nibles), 0 = bloqueado, F = disponible
# 0000 0000 = 00
# 0000 0000 = 00
# 0000 0000 = 00
# 0000 0000 = 00

# 0000 0000 = 00
# 0000 0001 = 01
# 0001 0001 = 11
# 0001 0001 = 11
# 0001 0001 = 11

# Teoría 4. Byte por cuadro (00/01)
# 00 00 00 00 00 00 00 00
# 00 00 00 01 01 01 01 01
# 01 01 01 01 01 01 01 01

# Teoría 5. Byte por cuadro (00/FF)
# 00 00 00 00 00 00 00 00
# 00 00 00 FF FF FF FF FF
# FF FF FF FF FF FF FF FF
# 

# Teoría 6. Byte por cuadro (01/00)
# 01 01 01 01 01 01 01 01
# 01 01 01 00 00 00 00 00
# 00 00 00 00 00 00 00 00

# Teoría 7. Byte por cuadro (FF/00)
# FF FF FF FF FF FF FF FF
# FF FF FF 00 00 00 00 00
# 00 00 00 00 00 00 00 00
# 00 00 00 00 00 00 00 00

# Teoría 6. Coordenadas inversas
# 00 00 01 01 01 01 00

# Teoría 100.
# 01 00 00 00 00 00 00 00
# 01 00 00 00 00 00 01 01
# 01 00 00 00 00 00 00 00


# SPRITES PKMN (CHARMANDER)
# 00 = negro
# 01 = blanco
# 10 = naranja
# 11 = naranja obscuro
# 0001 1010 = 1A
# 0011 1110 = 3E
# 1010 1010 = AA

# SPRITES PKMN (CHARMANDER)
# 00 = blanco
# 01 = negro
# 10 = naranja
# 11 = naranja obscuro
# 0100 1010 = 4A
# 0111 1110 = 7E
# 1010 1010 = AA

# SPRITES PKMN (CHARMANDER)
# 00 = naranja
# 01 = naranja obscuro
# 10 = blanco
# 11 = negro
# 1110 0000 = E0
# 1101 0100 = D4
# 0000 0000 = 00

# 1111 1111 = FF
# 0001 0101 = 15
# 0101 1010 = 5A

# ROUTES []
index = find_all_text('CINNABAR')
#print index
for i in range(256):
  suelo = chr(i)
  suelo_3  = "".join([suelo for qi in range(3)])
  suelo_4  = "".join([suelo for qj in range(4)])
  for j in range(256):
    if j != i:
      for k in range(256):
        if j != k and k != i:
          dt = suelo_3 + chr(j) + suelo_4 \
            + suelo_3 + chr(k) + suelo_4
          index = sdata.find(dt)
          if index != -1:
            print index, "(suelo:" + str(i) \
              + ", j: "+str(j) \
              + ", k: "+str(k) +") "  + hexlify(dt)

#print from_pkmn_string(get_string_from_position(463987, 1200))


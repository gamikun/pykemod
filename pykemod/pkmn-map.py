# -*- coding: utf-8 -*-
from binascii import hexlify
from PIL import Image
import numpy as np

#with open('./pkmn-chars.txt', 'rb') as f:
#chars = [f.read(1) for i in range(256)]

pk_data = open('./Pokemon Red.gb', 'rb')
  
# Datos del mapa de descubrimiento
data = np.array([255 for i in range(1024*1024*3)], dtype=np.dtype('B'))

# -- Datos básicos --
BASICS_COLOR = (0,0,0)
data[0x1D203*3:0x1D203*3+3] = BASICS_COLOR # Nivel de pokemon inicial
data[0x1D10E*3:0x1D10E*3+3] = BASICS_COLOR # Pokemon inicial A
data[0x1D11F*3:0x1D11F*3+3] = BASICS_COLOR # Pokemon inicial B
data[0x1D130*3:0x1D130*3+3] = BASICS_COLOR # Pokemon inicial C

# -- Nombres PKMN -- 
NAMES_COLOR = (0,128,0)
for i in range(190*10):
  data[(0x1C21E+i)*3:(0x1C21E+i)*3+3] = NAMES_COLOR

# -- Ataques PKMN --
ATK_COLOR = (128,0,0)
atk_index = 0
byte_index = 0
pk_data.seek(0xB0000)
while True:
  by = ord(pk_data.read(1))
  if by == 80:
    atk_index += 1
  byte_index += 1
  if atk_index >= 165:
    break
for i in range(byte_index):
  data[(0xB0000+i)*3:(0xB0000+i)*3+3] = ATK_COLOR

# Pokemon Data
PKMN_DATA_COLOR = (0,0,200)
for i in range(190*83):
  data[(0x39010+i)*3:(0x39010+i)*3+3] = PKMN_DATA_COLOR

# -- Evoluciones --
EVOL_COLOR = (128, 0, 255)
data[0x3B939*3:0x3B939*3+6] = EVOL_COLOR+EVOL_COLOR # Charmander -> Charmeleon
data[0x3B95B*3:0x3B95B*3+6] = EVOL_COLOR+EVOL_COLOR # Charmeleon -> Charizard
data[0x3B94A*3:0x3B94A*3+6] = EVOL_COLOR+EVOL_COLOR # Squirtle   -> Warturtle
data[0x3B96C*3:0x3B96C*3+6] = EVOL_COLOR+EVOL_COLOR # Warturtle  -> Blastoise
data[0x3B2B1*3:0x3B2B1*3+6] = EVOL_COLOR+EVOL_COLOR # Cubone     -> Marowak

# Maps
# Pallet Town
for index in range(10 * 9):
  data[0x0182fb + index * 3:(0x0182fb + index * 3) + 3] = (0, 0, 0)
#data[0x0182fb:0x0182fb + 10 * 9] = (0, 0, 0)
# Viridian City
for index in range(20 * 18):
  data[0x0183ea + index * 3:(0x0183ea + index * 3) + 3] = (255, 128, 0)
#data[0x0183ea:0x0183ea + 20 * 18] = (0, 0, 0)
# Route 1
#data[0x01C0FA:0x01C0FA + 10 * 18] = (0, 0, 0)

# -- Rutas -- (estimado)
ROUTE_COLOR = (0, 255, 255)
data[0x71473*3:0x71473*3+600] = [128 for i in range(600)]

im = Image.frombuffer('RGB', (1024, 1024), data, 'raw', 'RGB', 0, 1)
im.save('./imagen.png')
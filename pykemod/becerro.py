from PIL import Image
from basehash import base52
from binascii import hexlify
import base64
import hashlib

ha = hashlib.new('SHA256')
base52 = base52()

file = '/Users/lizet/Downloads/CzITHnEIlkQw9SbaX5futCzFrKk1qe_NwvWnIBmP2fY.png'

counter = 0

colors = [() for c in range(256)]

#data = open(file, 'rb').read()

#print(data[9950391])

image = Image.open(file)
w, h = image.size

data = image.getdata()

new_pixels = bytearray(w * h * 4)

values = []
cadena = []
started = False

for index, pixel in enumerate(data):
	black, alpha = pixel

	if (black >= 200 and black <= 254):
		#if (black >= 0 and black <= 25):
		v = round(black / 52)
		new_pixels[index * 4] = v
		new_pixels[index * 4 + 1] = v
		new_pixels[index * 4 + 2] = v
		new_pixels[index * 4 + 3] = 255
		values.append(black)
		cadena.append(black - 202)
		counter += 1
		if not started:
			print('STARTEDA AT: {}'.format(index))
			started = True
	else:
		new_pixels[index * 4] = 255
		new_pixels[index * 4 + 1] = 255
		new_pixels[index * 4 + 2] = 255
		new_pixels[index * 4 + 3] = 255
		#values.append(None)

	#if index == 1599 * 1105:
	#	break

	"""
	if alpha != 255:
		new_pixels[index * 4] = 255
		new_pixels[index * 4 + 1] = 0
		new_pixels[index * 4 + 2] = 0
		counter += 1
		# ha.update(chr(black).encode())
	else:
		new_pixels[index * 4] = black
		new_pixels[index * 4 + 1] = black
		new_pixels[index * 4 + 2] = black


	new_pixels[index * 4 + 3] = 255
	"""

new_image = Image.frombytes('RGBA', (w, h), bytes(new_pixels))
# new_image = new_image.resize((1600, 100))
new_image.save('new.png')

print(cadena)

print(ha.hexdigest())

print(repr(values))

print('CADENA LENGTH: {}'.format(len(cadena)))

"""
cords = []
values = [[x, 0, None] for x in range(256)]

counter = 0
for index, pixel in enumerate(data):
	black, alpha = pixel
	values[alpha][1] += 1

	if alpha == 203:
		counter += 1

"""
"""for y in range(h):
	for x in range(w):
		offset = y * w + x
		if data[offset][1] == 203:
			cords.append((x, y))"""


#print([v for v in values if v[1] > 0])
#print(len([v for v in values if v[1] > 0]))

#print(cords)
print(counter)
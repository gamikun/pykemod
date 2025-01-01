from PIL import Image, ImageDraw

with open('./bros.nes', 'rb') as f:
	data = f.read()
	image = Image.new('RGB', (256, 256))
	draw = ImageDraw.Draw(image)
	length = int(len(data) / 2)

	print('length: ' + str(length))

	lx = 0
	ly = 0

	for index in range(length):
		x = ord(data[index * 2])
		y = ord(data[index * 2 + 1])
		print(x, y)
		draw.line([(lx, ly), (x, y)])
		lx = x
		ly = y

	image.save('lineas.png')
# import EAN13 from barcode module
from barcode import Code128
  
# import ImageWriter to generate an image file
from barcode.writer import ImageWriter

import os
from PIL import Image, ImageDraw, ImageFont


def export_barcode(number,name):

	my_code = Code128(number, writer=ImageWriter())
	  
	# Our barcode is ready. Let's save it.
	my_code.save("new_code1")


	filename = 'new_code1.png'

	sq_fit_size = 300
	logo_file = f'{os.getcwd()}/inventory/static/logo.png'
	logoIm = Image.open(logo_file)
	logoWidth, logoHeight = logoIm.size


	im = Image.open(filename)
	width, height = im.size


	newsize = (width * 2, height * 2)
	resizedim = im.resize(newsize)



	resizedim.paste(logoIm, (15, height * 2 - logoHeight - 15), logoIm)



	draw = ImageDraw.Draw(resizedim)
	text = name
	font = ImageFont.truetype("/Library/fonts/Arial.ttf", 30)
	draw.text((width, height * 2 - 125), text, fill ="black", anchor ="mm", font = font) 



	filepath_export =  f'{os.getcwd()}/inventory/static/new_code1.png'
	resizedim.save(os.path.join('', filepath_export))


	os.remove("new_code1.png")

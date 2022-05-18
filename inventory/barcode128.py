from flask import render_template, redirect, url_for, flash, request, send_from_directory,send_file,Response,Blueprint
from flask_login import login_required
from inventory.resources import Dictionaries,Scan,Funcs
import code128
import io
import json

barcode = Blueprint('barcode',__name__)

@login_required
@barcode.route('render/<barcode>')
def return_128_barcode(barcode):
	img = code128.image(barcode)
	img_io = io.BytesIO()
	img.save(img_io, 'JPEG', quality=70)
	img_io.seek(0)

	return send_file(img_io, mimetype='image/jpeg')


@login_required
@barcode.route('/render', methods=['GET', 'POST'])
def barcode_render():
	dictionaries = Dictionaries()
	items = dictionaries.items
	itemdict = dictionaries.itemdict
	itemdict2 = dictionaries.itemdict2

	barcode_items = json.loads(request.form['items'])
	barcode_items = [int(i) for i in barcode_items]

	print(barcode_items)

	return render_template("render_barcodes.html",
		items = items,
		itemdict = itemdict,
		itemdict2 = itemdict2,
		barcode_items = barcode_items)


@login_required
@barcode.route('/')
def barcode_page():
	dictionaries = Dictionaries()
	items = dictionaries.items
	itemdict = dictionaries.itemdict
	itemdict2 = dictionaries.itemdict2

	return render_template("barcode128.html",
		items = items,
		itemdict = itemdict,
		itemdict2 = itemdict2)

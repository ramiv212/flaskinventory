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
	name_item_dict = dictionaries.name_item_dict
	ID_item_dict = dictionaries.ID_item_dict

	barcode_items = json.loads(request.form['items'])
	barcode_items = [int(i) for i in barcode_items]


	return render_template("render_barcodes.html",
		items = items,
		name_item_dict = name_item_dict,
		ID_item_dict = ID_item_dict,
		barcode_items = barcode_items)


@login_required
@barcode.route('/')
def barcode_page():
	dictionaries = Dictionaries()
	items = dictionaries.items
	name_item_dict = dictionaries.name_item_dict
	ID_item_dict = dictionaries.ID_item_dict


	return render_template("barcode128.html",
		items = items,
		name_item_dict = name_item_dict,
		ID_item_dict = ID_item_dict)

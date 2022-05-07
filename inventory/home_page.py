from flask import render_template, redirect, url_for, flash, request, send_from_directory,Blueprint
from flask_login import login_required
from inventory.models import Item, Event
from inventory.forms import CreateEventForm,ItemInspectorForm,CreateItemForm,AddToEventForm
from inventory import db
from inventory.mybarcode import export_barcode
from inventory.resources import Dictionaries,Scan,Funcs
import json
import os
from sqlalchemy.orm import load_only


homepage = Blueprint('homepage',__name__)



@homepage.route("/", methods=['GET', 'POST'])
@login_required
def home_page():
	dictionaries = Dictionaries()
	inspector_form = ItemInspectorForm()
	create_item_form = CreateItemForm()
	create_event_form = CreateEventForm()
	add_to_event_form = AddToEventForm()
	scan = Scan()
	funcs = Funcs()


	# code to update item in database
	if inspector_form.submit.data and inspector_form.validate_on_submit():
		funcs.update_item(inspector_form)

		flash(f'{inspector_form.name.data} was updated.')

		return redirect(url_for('homepage.home_page'))



	# code to show barcode
	elif inspector_form.print_barcode.data and inspector_form.validate_on_submit():
		export_barcode(str(inspector_form.barcode.data),inspector_form.name.data)

		return send_from_directory(f'{os.getcwd()}/inventory/static/', "new_code1.png") 



	# code to delete item from db
	elif inspector_form.delete.data and inspector_form.validate_on_submit():
		item_to_delete = Item.query.get(inspector_form.ID.data)
		db.session.delete(item_to_delete)
		db.session.commit()

		flash(f'{inspector_form.name.data} was deleted.')

		return redirect(url_for('homepage.home_page'))



	# code to add a new item to db
	if create_item_form.create.data and create_item_form.validate_on_submit():

		funcs.create_item(create_item_form)

		flash(f'{create_item_form.name.data} was created.')

		return redirect(url_for('homepage.home_page'))



	# get the scanned items from the hidden form, add them to the items that are already in the selected form,
	# and then update the items of the event in the database
	if add_to_event_form.add_scanned_items.data and add_to_event_form.validate_on_submit():
		scan.add_scanned_items(add_to_event_form.hidden_scanned_items.data)



	# create an event
	if create_event_form.submit.data and create_event_form.validate_on_submit():

		funcs.create_event(create_event_form)

		# update event submitfields
		funcs.update_event_submitfields()

		flash(f"Event \"{create_event_form.event_name.data}\" was created.")

		return redirect(url_for('homepage.home_page'))



		# if inspector_form.errors != {}: #If there are not errors from the validations
	for err_msg in inspector_form.errors.values():
		flash(f'There was an error with the form: {err_msg}',category='danger')
		print(err_msg)

		print(f"\n\nbarcode.data = {inspector_form.print_barcode.data}")
		print(f"barcode.data = {inspector_form.validate_on_submit()}\n\n")


	funcs.update_event_submitfields()


	return render_template("home.html", 
		items=dictionaries.items, 
		itemdict=dictionaries.itemdict,
		itemdict2=dictionaries.itemdict2,
		barcodedict=dictionaries.barcodedict,
		inspector_form=inspector_form,
		create_item_form=create_item_form,
		create_event_form=create_event_form,
		add_to_event_form=add_to_event_form)
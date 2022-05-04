from flask import render_template, redirect, url_for, flash, request, send_from_directory,Blueprint
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
		print("RAN UPDATE")

		print("\ninspector_form validated\n")

		item_to_update = {    "ID" : inspector_form.ID.data,
							  "barcode" : inspector_form.barcode.data,
							  "serial" : inspector_form.serial.data,
							  "manufacturer" : inspector_form.manufacturer.data,
							  "name" : inspector_form.name.data,
							  "category" : inspector_form.category.data,
							  "storage" : inspector_form.storage.data,
							  "status" : inspector_form.status.data,
							  "notes" : inspector_form.notes.data,
		
						}

		item = Item.query.get(inspector_form.ID.data)

		for key, value in item_to_update.items():
			setattr(item, key, value)

		db.session.commit()

		flash(f'{inspector_form.name.data} was updated.')

		return redirect(url_for('homepage.home_page'))



	# code to show barcode
	elif inspector_form.print_barcode.data and inspector_form.validate_on_submit():
		export_barcode(str(inspector_form.barcode.data),inspector_form.name.data)

		return send_from_directory(f'{os.getcwd()}/inventory/static/', "new_code1.png") 



	# code to delete item from db
	elif inspector_form.delete.data and inspector_form.validate_on_submit():
		item_to_delete = Item.query.get(inspector_form.ID.data)
		print(f"\n###{item_to_delete}###\n")
		db.session.delete(item_to_delete)
		db.session.commit()

		flash(f'{inspector_form.name.data} was deleted.')

		return redirect(url_for('homepage.home_page'))



	# code to add a new item to db
	if create_item_form.create.data and create_item_form.validate_on_submit():
		print("\ncreate_item_form form validated\n")

		barcode = dictionaries.return_max_barcode()

		for _ in range(create_item_form.qty.data):
			item_to_create = Item(barcode=barcode + 1,
								  serial=create_item_form.serial.data,
								  manufacturer=create_item_form.manufacturer.data,
								  name=create_item_form.name.data,
								  category=create_item_form.category.data,
								  storage=create_item_form.storage.data,
								  status="OK",
								  notes=create_item_form.storage.data)
			db.session.add(item_to_create)

			barcode += 1
		
		db.session.commit()

		flash(f'{create_item_form.name.data} was created.')

		return redirect(url_for('homepage.home_page'))

	# get the scanned items from the hidden form, add them to the items that are already in the selected form,
	# and then update the items of the event in the database
	if add_to_event_form.add_scanned_items.data and add_to_event_form.validate_on_submit():
		scan.add_scanned_items(add_to_event_form.hidden_scanned_items.data)



	# create an event
	if create_event_form.submit.data and create_event_form.validate_on_submit():
		print("\ncreate_event form validated\n")
		event_to_create = Event(event_name=create_event_form.event_name.data,
							  event_date_start=create_event_form.event_date_start.data,
							  event_date_end=create_event_form.event_date_end.data,
							  event_client=create_event_form .event_client.data,
							  active=True,

							  # empty JSON string
							  items = """ 
								{
	"items": [
	]
}
							  """)


		db.session.add(event_to_create)
		
		db.session.commit()

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
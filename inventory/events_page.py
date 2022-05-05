from flask import render_template, redirect, url_for, flash, request, send_from_directory, flash
from inventory.models import Item, Event
from inventory.forms import CreateEventForm,ItemInspectorForm,CreateItemForm,AddToEventForm,SelectEventForm,Blueprint
from inventory import db
from inventory.mybarcode import export_barcode
from inventory.resources import Dictionaries,Scan,Funcs
from inventory.checkdates import get_conflicting_event_items
import json
import os
from sqlalchemy.orm import load_only
from sqlalchemy import delete
from wtforms import SelectField
from datetime import datetime,timedelta



eventspage = Blueprint('events',__name__)


@eventspage.route('/', methods=['GET', 'POST'])
def event_page():
	create_event_form = CreateEventForm()
	dictionaries = Dictionaries()
	inspector_form = ItemInspectorForm()
	create_item_form = CreateItemForm()
	add_to_event_form = AddToEventForm()
	select_event_form = SelectEventForm()
	scan = Scan()
	funcs = Funcs()
	selected_event = None
	selected_event_items = []


	# create an event
	if create_event_form.submit.data and create_event_form.validate_on_submit():
		event_to_create = Event(event_name=create_event_form.event_name.data,
							  event_date_start=create_event_form.event_date_start.data,
							  event_date_end=create_event_form.event_date_end.data,
							  event_client=create_event_form.event_client.data,
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


		return redirect(url_for('events.event_page'))



	# select an event
	if select_event_form.submit.data and select_event_form.validate_on_submit():
		selected_event = select_event_form.event_field.data
		selected_event_id = dictionaries.eventdict[selected_event][0]
		selected_event_items = json.loads(dictionaries.eventdict[selected_event][5])
		selected_event_items = selected_event_items['items']
		conflicting_event_items = get_conflicting_event_items(selected_event)



		return render_template('create-event.html', 
		items=dictionaries.items,
		itemdict=dictionaries.itemdict,
		itemdict2=dictionaries.itemdict2,
		create_event_form=create_event_form,
		inspector_form=inspector_form,
		create_item_form=create_item_form,
		add_to_event_form=add_to_event_form,
		select_event_form=select_event_form,
		selected_event_name=selected_event,
		selected_event_items=selected_event_items,
		selected_event_id=selected_event_id,
		conflicting_event_items=conflicting_event_items,
		event_start_date=dictionaries.eventdict[select_event_form.event_field.data][1],
		event_end_date=dictionaries.eventdict[select_event_form.event_field.data][2])

	# get the scanned items from the hidden form, add them to the items that are already in the selected form,
	# and then update the items of the event in the database
	if add_to_event_form.add_scanned_items.data and add_to_event_form.validate_on_submit():
		scan.add_scanned_items(add_to_event_form.hidden_scanned_items.data)


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

		return redirect(url_for('events.event_page'))


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

		return redirect(url_for('events.event_page'))



	if select_event_form.errors != {}: #If there are not errors from the validations
		for err_msg in select_event_form.errors.values():
			flash(f'There was an error: {err_msg}',category='danger')
			print(err_msg)

	funcs.update_event_submitfields()

	return render_template('create-event.html',
		items=dictionaries.items,
		itemdict=dictionaries.itemdict,
		itemdict2=dictionaries.itemdict2,
		inspector_form=inspector_form,
		create_item_form=create_item_form,
		create_event_form=create_event_form,
		add_to_event_form=add_to_event_form,
		select_event_form=select_event_form,
		selected_event_items=selected_event_items,
		conflicting_event_items=list())


# remove item
@eventspage.route('/remove', methods=['GET', 'POST'])
def remove_from_event():
	scan = Scan()
	dictionaries = Dictionaries()

	event_name = request.form["event"]

	event_ID = dictionaries.eventdict[event_name][0]

	print(request.form["id"],event_ID)

	scan.remove_func(request.form["id"],event_ID)


	return redirect(url_for('events.event_page'))



# add item
@eventspage.route('/add', methods=['GET', 'POST'])
def add_item_to_event():
	scan = Scan()
	dictionaries = Dictionaries()

	event_name = request.form["event"]

	event_ID = dictionaries.eventdict[event_name][0]

	scan.add_items(request.form["id"],event_ID)


	return redirect(url_for('events.event_page'))


# render a checklist of the event
@eventspage.route('/checklist', methods=['GET', 'POST'])
def return_event_checklist():
	dictionaries = Dictionaries()
	event = request.args.get('event')

	if event:
		return render_template('checklist.html',
			itemdict2=dictionaries.itemdict2,
			event_name=event,
			event_date_start=dictionaries.eventdict[event][1],
			event_date_end=dictionaries.eventdict[event][2],
			event_client=dictionaries.eventdict[event][3],
			event_items=json.loads(dictionaries.eventdict[event][5])['items'])
	else:
		flash("No event was selected")
		return redirect(url_for('events.event_page'))


@eventspage.route('/delete-event', methods=['GET', 'POST'])
def delete_event():
	dictionaries = Dictionaries()
	funcs = Funcs()
	event = request.args.get('event')
	
	if event:
		event_ID = dictionaries.eventdict[event][0]

		Event.query.filter_by(ID=event_ID).delete()
		db.session.commit()
		funcs.update_event_submitfields()
		
		flash(f"{event} was deleted")

		return redirect(url_for('events.event_page'))
	else:
		flash("No event was selected")
		return redirect(url_for('events.event_page'))



from flask import render_template, redirect, url_for, flash, request, send_from_directory, flash
from inventory.models import Item, Event
from inventory.forms import CreateEventForm,ItemInspectorForm,CreateItemForm,AddToEventForm,SelectEventForm,Blueprint
from inventory import db
from inventory.mybarcode import export_barcode
from inventory.resources import Dictionaries,Scan,Funcs
import json
from sqlalchemy.orm import load_only
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

		return redirect(url_for('events.event_page'))



	# select an event

	if select_event_form.submit.data and select_event_form.validate_on_submit():
		selected_event = select_event_form.event_field.data
		selected_event_id = dictionaries.eventdict[selected_event][0]
		selected_event_items = json.loads(dictionaries.eventdict[selected_event][5])
		selected_event_items = selected_event_items['items']

		return render_template('create-event.html', 
		items=dictionaries.items,
		itemdict=dictionaries.itemdict,
		itemdict2=dictionaries.itemdict2,
		create_event_form=create_event_form,
		inspector_form=inspector_form,
		create_item_form=create_item_form,
		add_to_event_form=add_to_event_form,
		select_event_form=select_event_form,
		selected_event_items=selected_event_items,
		selected_event_id=selected_event_id)

	# get the scanned items from the hidden form, add them to the items that are already in the selected form,
	# and then update the items of the event in the database
	if add_to_event_form.add_scanned_items.data and add_to_event_form.validate_on_submit():
		scan.add_scanned_items(add_to_event_form.hidden_scanned_items.data)


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
		selected_event_items=selected_event_items)


@eventspage.route('/remove', methods=['GET', 'POST'])
def remove_from_event():
	scan = Scan()
	dictionaries = Dictionaries()

	event_name = request.form["event"]

	event_ID = dictionaries.eventdict[event_name][0]

	print(request.form["id"],event_ID)

	scan.remove_func(request.form["id"],event_ID)


	return redirect(url_for('events.event_page'))



@eventspage.route('/add', methods=['GET', 'POST'])
def add_item_to_event():
	scan = Scan()
	dictionaries = Dictionaries()

	event_name = request.form["event"]

	event_ID = dictionaries.eventdict[event_name][0]

	scan.add_items(request.form["id"],event_ID)


	return redirect(url_for('events.event_page'))


# @eventspage.route('/datetime', methods=['GET', 'POST'])
# def check_item_datetime():
# 	start = start = datetime.datetime.strptime(request.form["start"], "%d-%m-%Y")
# 	end = datetime.datetime.strptime(request.form["end"], "%d-%m-%Y")
# 	TODAY_CHECK = datetime.datetime.now()

# 	if start <= TODAY_CHECK <= end:
# 		print("Not Available")
# 		return False
# 	else:
# 		print("Available")
# 		return True


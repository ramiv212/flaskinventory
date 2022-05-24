from flask import render_template, redirect, url_for, flash, request, send_from_directory, flash
from flask_login import login_required
from inventory.models import Item, Event,EventArchive
from inventory.forms import CreateEventForm,ItemInspectorForm,CreateItemForm,AddToEventForm,SelectEventForm,EditEventForm,Blueprint
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
@login_required
def event_page():
	create_event_form = CreateEventForm()
	edit_event_form = EditEventForm()
	dictionaries = Dictionaries()
	inspector_form = ItemInspectorForm()
	create_item_form = CreateItemForm()
	add_to_event_form = AddToEventForm()
	select_event_form = SelectEventForm()
	scan = Scan()
	funcs = Funcs()
	selected_event = None
	selected_event_items = []
	selected_event_items_dict = dict()


	# code to update item in database
	if inspector_form.submit.data and inspector_form.validate_on_submit():
		funcs.update_item(inspector_form)

		flash(f'{inspector_form.name.data} was updated.')

		return redirect(url_for('events.event_page'))
		

	# create an event
	if create_event_form.submit.data and create_event_form.validate_on_submit():

		funcs.create_event(create_event_form)

		# update event submitfields
		funcs.update_event_submitfields()

		flash(f"Event \"{create_event_form.event_name.data}\" was created.")


		return redirect(url_for('events.event_page'))



	# select an event
	if select_event_form.submit.data and select_event_form.validate_on_submit() and select_event_form.event_field.data != "":
		selected_event = select_event_form.event_field.data
		selected_event_id = dictionaries.eventdict[selected_event]['ID']
		selected_event_items = json.loads(dictionaries.eventdict[selected_event]['items'])
		for item in selected_event_items: 
			selected_event_items_dict[dictionaries.ID_item_dict[item]['name']] = {'ID': item,'qty': dictionaries.name_item_dict[dictionaries.ID_item_dict[item]['name']]['qty'], 'manufacturer' : dictionaries.ID_item_dict[item]['manufacturer'], 'status' : dictionaries.ID_item_dict[item]['status'], 'name' : item, 'barcode' : dictionaries.ID_item_dict[item]['barcode'] }


		for item in selected_event_items_dict:
			print(f'{item}: {selected_event_items_dict[item]}')

		conflicting_event_items = get_conflicting_event_items(selected_event)

		contact_info = json.loads(dictionaries.eventdict[selected_event]['contact'])

		# populate event fields with event data
		edit_event_form.event_name.data = selected_event
		edit_event_form.event_client.data = dictionaries.eventdict[selected_event]['client']
		edit_event_form.event_date_start.data = datetime.strptime(dictionaries.eventdict[selected_event]['date_start'],"%m/%d/%Y")
		edit_event_form.event_date_end.data = datetime.strptime(dictionaries.eventdict[selected_event]['date_end'],"%m/%d/%Y")
		edit_event_form.load_in.data = datetime.strptime(dictionaries.eventdict[selected_event]['load_in'],"%m/%d/%Y")
		edit_event_form.load_out.data = datetime.strptime(dictionaries.eventdict[selected_event]['load_out'],"%m/%d/%Y")
		edit_event_form.edit_notes.data = dictionaries.eventdict[selected_event]['notes']


		return render_template('create-event.html', 
		items=dictionaries.items,
		name_item_dict=dictionaries.name_item_dict,
		ID_item_dict=dictionaries.ID_item_dict,
		create_event_form=create_event_form,
		edit_event_form=edit_event_form,
		inspector_form=inspector_form,
		create_item_form=create_item_form,
		add_to_event_form=add_to_event_form,
		select_event_form=select_event_form,
		selected_event_name=selected_event,
		selected_event_items=selected_event_items,
		selected_event_items_dict=selected_event_items_dict,
		selected_event_id=selected_event_id,
		conflicting_event_items=conflicting_event_items,
		event_start_date=dictionaries.eventdict[selected_event]['date_start'],
		event_end_date=dictionaries.eventdict[selected_event]['date_end'],
		load_in_date=dictionaries.eventdict[selected_event]['load_in'],
		load_out_date=dictionaries.eventdict[selected_event]['load_out'],
		contact_info=contact_info,
		event_notes=dictionaries.eventdict[selected_event]['notes']
		)

	# get the scanned items from the hidden form, add them to the items that are already in the selected form,
	# and then update the items of the event in the database
	if add_to_event_form.add_scanned_items.data and add_to_event_form.validate_on_submit() and add_to_event_form.event_select.data != "":
		scan.add_scanned_items(add_to_event_form.hidden_scanned_items.data)


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

		return redirect(url_for('events.event_page'))


	# code to add a new item to db
	if create_item_form.create.data and create_item_form.validate_on_submit():

		funcs.create_item(create_item_form)

		flash(f'{create_item_form.name.data} was created.')

		return redirect(url_for('events.event_page'))


	# code to update an event
	if edit_event_form.update.data and edit_event_form.validate_on_submit():
		event_name = edit_event_form.event_name.data
		event_date_start = edit_event_form.event_date_start.data
		event_date_end = edit_event_form.event_date_end.data
		event_client = edit_event_form.event_client.data
		load_in = edit_event_form.load_in.data
		load_out = edit_event_form.load_out.data
		notes = edit_event_form.edit_notes.data


		event_to_update = { 
							  "event_date_start" : edit_event_form.event_date_start.data,
							  "event_date_end" : edit_event_form.event_date_end.data,
							  "event_client" : edit_event_form.event_client.data,
							  "load_in" : edit_event_form.load_in.data,
							  "load_out" : edit_event_form.load_out.data,
							  "notes" : edit_event_form.edit_notes.data,
						}

		event = Event.query.filter_by(event_name = event_name).first()


		for key, value in event_to_update.items():
			setattr(event, key, value)

		db.session.commit()

		flash(f'{event_name} was updated')

		return redirect(url_for('events.event_page'))



	if select_event_form.errors != {}: #If there are not errors from the validations
		for err_msg in select_event_form.errors.values():
			flash(f'There was an error: {err_msg}',category='danger')
			print(err_msg)

	funcs.update_event_submitfields()

	return render_template('create-event.html',
		items=dictionaries.items,
		name_item_dict=dictionaries.name_item_dict,
		ID_item_dict=dictionaries.ID_item_dict,
		inspector_form=inspector_form,
		create_item_form=create_item_form,
		create_event_form=create_event_form,
		edit_event_form=edit_event_form,
		add_to_event_form=add_to_event_form,
		select_event_form=select_event_form,
		selected_event_items=selected_event_items,
		selected_event_items_dict=selected_event_items_dict,
		contact_info="""{
		"contact_name":"",
		"contact_phone":"",
		"contact_email":"",
		}""",
		conflicting_event_items=list())


# remove item
@eventspage.route('/remove', methods=['GET', 'POST'])
@login_required
def remove_from_event():
	scan = Scan()
	dictionaries = Dictionaries()

	event_name = request.form["event"]

	event_ID = dictionaries.eventdict[event_name]['ID']

	print(event_name,event_ID)

	scan.remove_func(request.form["id"],event_ID)

	return redirect(url_for('events.event_page'))



# add item
@eventspage.route('/add', methods=['GET', 'POST'])
@login_required
def add_item_to_event():
	scan = Scan()
	dictionaries = Dictionaries()

	event_name = request.form["event"]

	event_ID = dictionaries.eventdict[event_name]["ID"]

	scan.add_items(request.form["id"],event_ID)

	return redirect(url_for('events.event_page'))


# render a checklist of the event
@eventspage.route('/checklist', methods=['GET', 'POST'])
@login_required
def return_event_checklist():
	event = request.args.get('event')

	if event:
		dictionaries = Dictionaries()
		event_items=json.loads(dictionaries.eventdict[event]['items'])
		audio_list = []
		video_list = []
		lighting_list = []
		rigging_list = []
		other_list = []

		contact_info = json.loads(dictionaries.eventdict[event]['contact'])

		for item in event_items:
			if dictionaries.ID_item_dict[item]['category'] == 'Audio':
				audio_list.append(item)
			elif dictionaries.ID_item_dict[item]['category'] == 'Video':
				video_list.append(item)
			elif dictionaries.ID_item_dict[item]['category'] == 'Lighting':
				lighting_list.append(item)
			elif dictionaries.ID_item_dict[item]['category'] == 'Rigging':
				rigging_list.append(item)
			elif dictionaries.ID_item_dict[item]['category'] == 'Other':
				other_list.append(item)
	else:
			flash("No event was selected")
			return redirect(url_for('events.event_page'))


	if event:
		return render_template('checklist.html',
			ID_item_dict=dictionaries.ID_item_dict,
			event_name=event,
			event_date_start=dictionaries.eventdict[event]['date_start'],
			event_date_end=dictionaries.eventdict[event]['date_end'],
			event_client=dictionaries.eventdict[event]['client'],
			event_items=event_items,
			load_in_date=dictionaries.eventdict[event]['load_in'],
			load_out_date=dictionaries.eventdict[event]['load_out'],
			contact_info=contact_info,
			event_notes=dictionaries.eventdict[event]['notes'],
			audio_list=audio_list,
			video_list=video_list,
			lighting_list=lighting_list,
			rigging_list=rigging_list,
			other_list=other_list)
	else:
		flash("No event was selected")
		return redirect(url_for('events.event_page'))


@eventspage.route('/archive-event', methods=['GET', 'POST'])
@login_required
def archive_event():
	dictionaries = Dictionaries()
	funcs = Funcs()
	event = request.args.get('event')
	newdict = dict()

	# delete event from event db
	if event:
		event_dict = dictionaries.eventdict[event]
		event_ID = event_dict['ID']

		Event.query.filter_by(ID=event_ID).delete()
		db.session.commit()
		funcs.update_event_submitfields()

		if event_dict['items']:
			for item in json.loads(event_dict['items']):
				print(item)
				newdict[item] = {'barcode' : dictionaries.ID_item_dict[item]['barcode'],
								'serial': dictionaries.ID_item_dict[item]['serial'],
								'manufacturer' : dictionaries.ID_item_dict[item]['manufacturer'],
								'name' : dictionaries.ID_item_dict[item]['name'],
								'category' : dictionaries.ID_item_dict[item]['category'],
								'storage' : dictionaries.ID_item_dict[item]['storage'],
								'status' : dictionaries.ID_item_dict[item]['status'],
								'notes' : dictionaries.ID_item_dict[item]['notes']
								}

		if event_dict['contact']:
			contact_info = event_dict['contact']
		else:
			contact_info = """{
		"contact_name":"",
		"contact_phone":"",
		"contact_email":"",
		}"""
			
		print(newdict)

		# add to event archive
		archived_event = EventArchive(
			event_name = event,
			event_date_start = datetime.strptime(event_dict['date_start'],"%m/%d/%Y"),
			event_date_end = datetime.strptime(event_dict['date_end'],"%m/%d/%Y"),
			load_in = datetime.strptime(event_dict['load_in'],"%m/%d/%Y"),
			load_out = datetime.strptime(event_dict['load_out'],"%m/%d/%Y"),
			event_client = event_dict['client'],
			active = 0,
			items = json.dumps(newdict),
			contact = contact_info,
			notes = event_dict['notes']
			)

		db.session.add(archived_event)
		
		db.session.commit()

		
		flash(f"{event} was archived")

		return redirect(url_for('events.event_page'))
	else:
		flash("No event was selected")
		return redirect(url_for('events.event_page'))


@eventspage.route('/archive', methods=['GET','POST'])
@login_required
def event_archive():

	archived_events = EventArchive.query.all()

	# get event request and render page with items
	if request.form and archived_events:
		if request.form['event']:
			event_name = request.form['event']

			event = EventArchive.query.filter_by(event_name=event_name).first()

			items = json.loads(event.items)
			event_date_start = event.event_date_start.strftime('%m/%d/%Y')
			event_date_end = event.event_date_end.strftime('%m/%d/%Y')
			event_load_in = event.load_in.strftime('%m/%d/%Y')
			event_load_out = event.load_out.strftime('%m/%d/%Y')
			contact_info = json.loads(event.contact)

			return render_template("event-archive.html", 
				archived_events=archived_events,
				items=items, 
				event_name=event.event_name,
				event_client=event.event_client,
				event_date_start=event_date_start,
				event_date_end=event_date_end,
				load_in_date=event_load_in,
				load_out_date=event_load_out,
				contact_info=contact_info,
				event_notes=event.notes)

	# if there is events but no request, render page with no items
	elif archived_events:
		archived_events = EventArchive.query.all()
		return render_template("event-archive.html",archived_events=archived_events,
			contact_info="""{
		"contact_name":"",
		"contact_phone":"",
		"contact_email":"",
		}""")

	# if there is no events, render page with no events
	else:
		return render_template("event-archive.html",archived_events=archived_events,
			contact_info="""{
		"contact_name":"",
		"contact_phone":"",
		"contact_email":"",
		}""")


@eventspage.route('/delete-archive', methods=['GET','POST'])
@login_required
def delete_event_archive():
	if request.args.get('event'):
		event_name = request.args.get('event')
		event_to_delete = EventArchive.query.filter_by(event_name=event_name).first()
		db.session.delete(event_to_delete)
		db.session.commit()
		flash(f'{event_to_delete.event_name} was deleted')
		return redirect(url_for('events.event_archive'))

	else:
		flash(f'No event was selected')
		return redirect(url_for('events.event_archive'))
		

@eventspage.route('/checkout', methods=['GET','POST'])
@login_required
def checkout():
	select_event_form = SelectEventForm()
	dictionaries = Dictionaries()

	if select_event_form.submit.data and select_event_form.validate_on_submit():
		selected_event = select_event_form.event_field.data
		event_items = json.loads(dictionaries.eventdict[selected_event]['items'])
		print(event_items)
		

		return render_template("checkout.html", 
			event_items=event_items,
			select_event_form=select_event_form,
			ID_item_dict=dictionaries.ID_item_dict,
			)
	else:
		selected_event = None
		event_items = None
		return render_template("checkout.html", 
			event_items=[],
			select_event_form=select_event_form,
			ID_item_dict=dictionaries.ID_item_dict
			)




from flask import render_template, redirect, url_for, flash, request, send_from_directory, flash
from flask_login import login_required
from inventory.models import Item, Event,EventArchive
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
@login_required
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
	if select_event_form.submit.data and select_event_form.validate_on_submit():
		selected_event = select_event_form.event_field.data
		selected_event_id = dictionaries.eventdict[selected_event][0]
		selected_event_items = json.loads(dictionaries.eventdict[selected_event][5])
		selected_event_items = selected_event_items['items']
		conflicting_event_items = get_conflicting_event_items(selected_event)

		contact_info = json.loads(dictionaries.eventdict[selected_event][8])
		print(contact_info)



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
		event_start_date=dictionaries.eventdict[selected_event][1],
		event_end_date=dictionaries.eventdict[selected_event][2],
		load_in_date=dictionaries.eventdict[selected_event][6],
		load_out_date=dictionaries.eventdict[selected_event][7],
		contact_info=contact_info,
		event_notes=dictionaries.eventdict[selected_event][9]
		)

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
		db.session.delete(item_to_delete)
		db.session.commit()

		flash(f'{inspector_form.name.data} was deleted.')

		return redirect(url_for('events.event_page'))


	# code to add a new item to db
	if create_item_form.create.data and create_item_form.validate_on_submit():

		funcs.create_item(create_item_form)

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

	event_ID = dictionaries.eventdict[event_name][0]

	scan.remove_func(request.form["id"],event_ID)

	return redirect(url_for('events.event_page'))



# add item
@eventspage.route('/add', methods=['GET', 'POST'])
@login_required
def add_item_to_event():
	scan = Scan()
	dictionaries = Dictionaries()

	event_name = request.form["event"]

	event_ID = dictionaries.eventdict[event_name][0]

	scan.add_items(request.form["id"],event_ID)

	return redirect(url_for('events.event_page'))


# render a checklist of the event
@eventspage.route('/checklist', methods=['GET', 'POST'])
@login_required
def return_event_checklist():
	dictionaries = Dictionaries()
	event = request.args.get('event')
	event_items=json.loads(dictionaries.eventdict[event][5])['items']
	audio_list = []
	video_list = []
	lighting_list = []
	rigging_list = []
	other_list = []

	for item in event_items:
		if dictionaries.itemdict2[item][5] == 'Audio':
			audio_list.append(item)
		elif dictionaries.itemdict2[item][5] == 'Video':
			video_list.append(item)
		elif dictionaries.itemdict2[item][5] == 'Lighting':
			lighting_list.append(item)
		elif dictionaries.itemdict2[item][5] == 'Rigging':
			rigging_list.append(item)
		elif dictionaries.itemdict2[item][5] == 'Other':
			other_list.append(item)


	if event:
		return render_template('checklist.html',
			itemdict2=dictionaries.itemdict2,
			event_name=event,
			event_date_start=dictionaries.eventdict[event][1],
			event_date_end=dictionaries.eventdict[event][2],
			event_client=dictionaries.eventdict[event][3],
			event_items=event_items,
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
def delete_event():
	dictionaries = Dictionaries()
	funcs = Funcs()
	event = request.args.get('event')
	newdict = dict()

	# delete event from event db
	if event:
		event_dict = dictionaries.eventdict[event]
		event_ID = event_dict[0]

		Event.query.filter_by(ID=event_ID).delete()
		db.session.commit()
		funcs.update_event_submitfields()


		if event_dict[5]:
			for item in json.loads(event_dict[5])['items']:
				newdict[dictionaries.itemdict2[item][0]] = dictionaries.itemdict2[item][0],dictionaries.itemdict2[item][1],dictionaries.itemdict2[item][2],dictionaries.itemdict2[item][3],dictionaries.itemdict2[item][4],dictionaries.itemdict2[item][5],dictionaries.itemdict2[item][6],dictionaries.itemdict2[item][7]
			

			# add to event archive
			archived_event = EventArchive(
				event_name = event,
				event_date_start = datetime.strptime(event_dict[1],"%m/%d/%Y"),
				event_date_end = datetime.strptime(event_dict[2],"%m/%d/%Y"),
				event_client = event_dict[3],
				active = 0,
				items = json.dumps(newdict)
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

			return render_template("event-archive.html", 
				archived_events=archived_events,
				items=items, 
				event_name=event.event_name,
				event_client=event.event_client,
				event_date_start=event_date_start,
				event_date_end=event_date_end)

	# if there is events but no request, render page with no items
	elif archived_events:
		archived_events = EventArchive.query.all()
		return render_template("event-archive.html",archived_events=archived_events)

	# if there is no events, render page with no events
	else:
		return render_template("event-archive.html",archived_events=archived_events)


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
		print(selected_event)
		event_items = json.loads(dictionaries.eventdict[selected_event][5])['items']
		

		return render_template("checkout.html", 
			event_items=event_items,
			select_event_form=select_event_form,
			itemdict2=dictionaries.itemdict2,
			)
	else:
		selected_event = None
		event_items = None
		return render_template("checkout.html", 
			event_items=[],
			select_event_form=select_event_form,
			itemdict2=dictionaries.itemdict2
			)




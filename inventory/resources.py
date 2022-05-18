from flask import redirect,url_for,Blueprint,flash
from inventory import db
from inventory.forms import CreateEventForm,ItemInspectorForm,CreateItemForm,AddToEventForm,SelectEventForm
from inventory.models import Item, Event
from wtforms import SelectField
import json
import os

json_routes = Blueprint('json',__name__)


class JSONFiles:
	def __init__(self):
		dictionaries = Dictionaries()
		# update the submitfield of events with the list of events including the newly created event
		events = Event.query.all()
		event_names = [x.event_name for x in events]
		event_names.insert(0,"")
		AddToEventForm.event_select = SelectField(label='Event',choices=event_names)


		# this turns the second dictionary into a JSON object
		self.jsondict2 = json.dumps(dictionaries.itemdict2, indent = 4)


		# this turns the barcode dictionary into a JSON object
		self.json_barcodes = json.dumps(dictionaries.barcodedict, indent = 4)


		# this turns the event dictionary into a JSON object
		self.json_events = json.dumps(dictionaries.eventdict, indent = 4)


# class JSONPaths:
# 	def __init__(self):
# 		print("json JSONSerializer")
# 		# this file path is for writing the JSON file to the static folder
# 		self.json_file_path = f'{os.getcwd()}/inventory/static/json_data.json'

# 		# this file path is for writing the JSON file to the static folder
# 		self.json_barcode_file_path = f'{os.getcwd()}/inventory/static/json_barcode_data.json'

# 		# this file path is to create a route for the JSON file to be rendered to so that it can be accessed
# 		self.json_file_path2 = f'{os.getcwd()}/inventory/static/'

# 		# this file path is for writing the JSON file to the static folder
# 		self.json_event_file_path = f'{os.getcwd()}/inventory/static/json_event_data.json'


class Dictionaries:
	def __init__(self):
		self.items = Item.query.all()
		self.events = Event.query.all()

		self.itemdict = dict()
		self.itemdict2 = dict()
		self.barcodedict = dict()
		self.eventdict = dict()

		# add all item names as keys into the dictionary. This dictionary is used to populate the rows in the inventory page.
		# It does not have duplicate name child items. It has Qty.
		for item in self.items:
			self.itemdict[item.name] = [item.ID,item.barcode,item.serial,item.manufacturer,item.name,item.category,item.storage,item.status,item.notes,0]

		for item in self.items:
			self.itemdict[item.name][9] = self.itemdict[item.name][9] + 1


		# this dictionary is used to populate the inspector when the inspect button is pushed.
		# It contains all items. Also used to populate Events page.
		for item in self.items:
			self.itemdict2[item.ID] = [item.ID,item.barcode,item.serial,item.manufacturer,item.name,item.category,item.storage,item.status,item.notes,0]


		# this dictionary is used to get values when scanning barcode
		for item in self.items:
			self.barcodedict[item.barcode] = [item.ID,item.barcode,item.serial,item.manufacturer,item.name,item.category,item.storage,item.status,item.notes,0]


		# this dictionary is used to get the event info of the currenty selected event in the selectfield
		for event in self.events:
			if event.active:
				self.eventdict[event.event_name] = [event.ID,
										event.event_date_start.strftime("%m/%d/%Y"),
										event.event_date_end.strftime("%m/%d/%Y"),
										event.event_client,
										event.active,
										event.items,
										event.load_in.strftime("%m/%d/%Y"),
										event.load_out.strftime("%m/%d/%Y"),
										event.contact,
										event.notes]
	
	def return_max_barcode(self):
			max_barcode = int(max([item.barcode for item in self.items]))
			return max_barcode



class Scan:
	def __init__(self):
		pass


	def remove_func(self,item_id,event_id):

		item_id = int(item_id)

		event_to_update = Event.query.get(event_id)
		event_to_update_items = json.loads(event_to_update.items)

		if item_id in event_to_update_items['items']:

			event_to_update_items['items'].remove(int(item_id))

			setattr(event_to_update, "items", json.dumps(event_to_update_items))

			db.session.commit()

		else:
			flash(f'This item is not in the {event_to_update.event_name} event.')


	def add_scanned_items(self,items):
		dictionaries = Dictionaries()
		add_to_event_form = AddToEventForm()


		# get the selected event ID
		event_ID = dictionaries.eventdict[add_to_event_form.event_select.data][0] 

		# get the items that were scanned and added to the hidden form field
		items_to_add = items.split(",")

		print(items_to_add)

		# get the items from the selected event
		try:
			items_to_add_to = json.loads(Event.query.get(event_ID).items)['items']
		except TypeError:
			items_to_add_to = []


		# add the items that are already in the event to the items that were scanned.
		# if there were no items in the event, then create an empty list and add the scanned items to it.
		try:
			items_to_add_to.extend(items_to_add)
		except AttributeError:
			items_to_add_to = []
			items_to_add_to.extend(items_to_add)

		# converts all items in the list to int. Turn it into a set to remove duplicates,
		# then back to a list to make it JSON serializable. Then sort it. 
		try:
			int_list = list(set(map(int, items_to_add_to)))

			# create a new dict from the list of aggregated items
			new_dict = {'items' : int_list}

			# turn that dict into a JSON object
			json_object = json.dumps(new_dict, indent = 4)

			# query the db for the event that will be updated
			event_to_update = Event.query.get(event_ID)

			# update the event items column with the new JSON object
			setattr(event_to_update, "items", json_object)

			db.session.commit()

		# if no items were scanned flash a message and do not update db.
		except ValueError:
			if items_to_add[0] == '':
				flash("No items were scanned.")


		return redirect(url_for('homepage.home_page'))


	def add_items(self,items,event):
		dictionaries = Dictionaries()
		add_to_event_form = AddToEventForm()
		select_event_form = SelectEventForm()

		# get the selected event ID
		self.event_ID = event

		# get the items that were scanned and added to the hidden form field
		items_to_add = items.split(",")

		# get the items from the selected event
		try:
			items_to_add_to = json.loads(Event.query.get(self.event_ID).items)['items']
		except TypeError:
			items_to_add_to = []

		# add the items that are already in the event to the items that were scanned.
		# if there were no items in the event, then create an empty list and add the scanned items to it.
		try:
			items_to_add_to.extend(items_to_add)
		except AttributeError:
			items_to_add_to = []
			items_to_add_to.extend(items_to_add)

		# converts all items in the list to int. Turn it into a set to remove duplicates,
		# then back to a list to make it JSON serializable. Then sort it. 
		try:
			int_list = list(set(map(int, items_to_add_to)))

			# create a new dict from the list of aggregated items
			new_dict = {'items' : int_list}

			# turn that dict into a JSON object
			json_object = json.dumps(new_dict, indent = 4)

			# query the db for the event that will be updated
			event_to_update = Event.query.get(self.event_ID)

			# update the event items column with the new JSON object
			setattr(event_to_update, "items", json_object)

			db.session.commit()

		# if no items were scanned flash a message and do not update db.
		except ValueError:
			if items_to_add[0] == '':
				flash("No items were scanned.")


		return redirect(url_for('homepage.home_page'))


@json_routes.route("/itemdict2", methods=['GET', 'POST'])
def itemdict2():
	json_files = JSONFiles()
	return json_files.jsondict2

@json_routes.route("/barcodes", methods=['GET', 'POST'])
def barcodes():
	json_files = JSONFiles()
	return json_files.json_barcodes

@json_routes.route("/events", methods=['GET', 'POST'])
def events():
	json_files = JSONFiles()
	return json_files.json_events


class Funcs:
	def __init__(self):
		self.dictionaries = Dictionaries()

	def update_event_submitfields(self):
		# update the submitfield of events with the list of events including the newly created event
		events = Event.query.all()
		event_names = [x.event_name for x in events]
		event_names.insert(0, '')
		AddToEventForm.event_select = SelectField(label='Event',choices=event_names)
		SelectEventForm.event_field = SelectField(label='Event',choices=event_names)

		return events

	def update_item(self,inspector_form):
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

		print(item_to_update)


		item = Item.query.get(inspector_form.ID.data)


		for key, value in item_to_update.items():
			setattr(item, key, value)

		db.session.commit()

	def create_item(self,create_item_form):
		barcode = self.dictionaries.return_max_barcode()

		for _ in range(create_item_form.qty.data):
			item_to_create = Item(barcode=barcode + 1,
								  serial=create_item_form.serial.data,
								  manufacturer=create_item_form.manufacturer.data,
								  name=create_item_form.name.data,
								  category=create_item_form.category.data,
								  storage=create_item_form.storage.data,
								  status="OK",
								  notes=create_item_form.notes.data)
			db.session.add(item_to_create)

			barcode += 1
		
		db.session.commit()


	def create_event(self,create_event_form):
		contact_name = create_event_form.contact_name.data
		contact_phone = create_event_form.contact_phone.data
		contact_email = create_event_form.contact_email.data
		contact_json = f'"contact_name": "{contact_name}",\n"contact_phone": "{contact_phone}",\n"contact_email": "{contact_email}"'


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
					  """,
					  load_in=create_event_form.load_in.data,
					  load_out=create_event_form.load_out.data,
					  contact="{"+contact_json+"}",
					  notes=create_event_form.notes.data,)


		db.session.add(event_to_create)
		
		db.session.commit()



	def add_list_of_items_to_event(self,event,items):
		dictionaries = Dictionaries()

		# get the selected event ID
		event_ID = event

		# list of items to be added
		items_to_add = items

		# converts all items in the list to int. Turn it into a set to remove duplicates,
		# then back to a list to make it JSON serializable. Then sort it. 
		
		int_list = list(set(map(int, items_to_add)))

		# create a new dict from the list of aggregated items
		new_dict = {'items' : int_list}

		# turn that dict into a JSON object
		json_object = json.dumps(new_dict, indent = 4)

		# query the db for the event that will be updated
		event_to_update = Event.query.get(event_ID)

		# update the event items column with the new JSON object
		setattr(event_to_update, "items", json_object)

		db.session.commit()



		 
from datetime import datetime,timedelta
from inventory.resources import Dictionaries
import json

def intersection(lst1, lst2):
    return list(set(lst1) & set(lst2))

def get_conflicting_event_items(event):
	dictionaries = Dictionaries()

	# Current event
	# list to be populated with datetime objects
	eventdates = []

	# turn the start date and end date of event from db to a datetime object
	start = datetime.strptime(dictionaries.eventdict[event]['load_in'].replace("/","-"),"%m-%d-%Y")
	end = datetime.strptime(dictionaries.eventdict[event]['load_out'].replace("/","-"),"%m-%d-%Y")
	
	# get the timedelta
	delta = end - start

	# fill in the eventdates list with datetimes of the event
	for i in range(delta.days + 1):
		day = start + timedelta(days=i)
		eventdates.append(day)



	# Other Events

	other_eventdates = []

	datetime_event_dict = dict()

	# get a new dict that has all events except this one
	other_events = dictionaries.eventdict.copy()
	other_events.pop(event)

	# for each event that is not the current event
	for event in other_events:

		# get the start and end date of the current iteration event
		other_start = datetime.strptime(dictionaries.eventdict[event]['load_in'].replace("/","-"),"%m-%d-%Y")
		other_end = datetime.strptime(dictionaries.eventdict[event]['load_out'].replace("/","-"),"%m-%d-%Y")

		# get timedelta of current iteration
		other_delta = other_end - other_start

		# fill in all dates from the timedelta and add them to the
		# other_eventsdates list
		for i in range(other_delta.days + 1):
			other_day = other_start + timedelta(days=i)
			other_eventdates.append(other_day)

			# create a dictionary that has datetimes as keys
			# and event names as values (to help find the event
			# that has the intersecting date)
			datetime_event_dict[other_day] = event

	# get the dates that intersect with other events
	intersect = intersection(eventdates,other_eventdates)

	# print(f'INTERSECT {intersect}')

	conflicting_events = []

	# get the events that conflict with this event
	for datetime_obj in intersect:
		conflicting_events.append(datetime_event_dict[datetime_obj])	


	conflicting_event_items = []

	# use the datetime event dict to get the names of events
	# that are conflicting with the other events, and then
	# get their items
	for event in set(conflicting_events):
		for item in json.loads(dictionaries.eventdict[event]['items']):
			conflicting_event_items.append(item)


	return (list(set(conflicting_event_items)),list(set(conflicting_events)))






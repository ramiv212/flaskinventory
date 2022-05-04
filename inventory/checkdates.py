from datetime import datetime,timedelta
from inventory.resources import Dictionaries


def get_event_dates(event,item):
	dictionaries = Dictionaries()

	eventdates = []

	start = datetime.strptime(dictionaries.eventdict[event][1].replace("/","-"),"%m-%d-%Y")
	end = datetime.strptime(dictionaries.eventdict[event][2].replace("/","-"),"%m-%d-%Y")
	
	delta = end - start

	for i in range(delta.days + 1):
		day = start + timedelta(days=i)
		eventdates.append(day)



	







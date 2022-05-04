from flask_wtf import FlaskForm
from wtforms import StringField, DateField, PasswordField, SubmitField,IntegerField,TextAreaField,SelectField,HiddenField
from wtforms.validators import DataRequired,Length, ValidationError
from inventory.models import Event
from sqlalchemy.orm import load_only
from flask import Blueprint
import json


class CreateEventForm(FlaskForm):
	def validate_event_name(self, event_name_to_check):
		event = Event.query.filter_by(event_name=event_name_to_check.data).first()
		if event:
			raise ValidationError('Event already exists! Please use another event name.')

	event_name = StringField(label='Event Name', validators=[DataRequired(),Length(min=2,max=30)])
	event_date_start = DateField(label='Event Start',format='%Y-%m-%d')
	event_date_end = DateField(label='Event End',format='%Y-%m-%d')
	event_client = StringField(label='Event Client',validators=[DataRequired(),Length(min=2,max=30)])
	submit = SubmitField(label='Create')


class ItemInspectorForm(FlaskForm):
	ID = IntegerField(label='ID')
	name = StringField(label='Name')
	barcode = IntegerField(label='Barcode')
	serial = StringField(label='Serial')
	manufacturer = StringField(label='Manufacturer')
	category = SelectField(label='Category',choices=["Audio","Video","Lighting","Rigging","Other"])
	storage = StringField(label='Storage')
	status = SelectField(label='Status',choices=["OK","Broken","Sent For Repair","Loaned To Customer","See Notes"])
	notes = TextAreaField(label='Notes')
	submit = SubmitField(label='Update')
	delete = SubmitField(label='Delete')
	print_barcode = SubmitField(label='Barcode')


class CreateItemForm(FlaskForm):
	name = StringField(label='Name')
	serial = StringField(label='Serial')
	manufacturer = StringField(label='Manufacturer')
	category = SelectField(label='Category',choices=["Audio","Video","Lighting","Rigging","Other"])
	storage = StringField(label='Storage')
	qty = IntegerField(label='Qty')
	notes = TextAreaField(label='Notes')
	create = SubmitField(label='Create')


class AddToEventForm(FlaskForm):

	events = Event.query.all()

	fields = ['ID', 'event_name','event_date_start', 'event_date_end', 'event_client' ,'active']
		
	event_names = [x.event_name for x in events]

	event_names.insert(0,"")

	event_select = SelectField(label='Event',choices=event_names)
	hidden_scanned_items = HiddenField()
	add_scanned_items = SubmitField(label='Add')


class SelectEventForm(FlaskForm):
	events = Event.query.all()
	fields = ['ID', 'event_name','event_date_start', 'event_date_end', 'event_client' ,'active']
	event_names = [x.event_name for x in events]

	event_field = SelectField(label='Event',choices=event_names)
	submit = SubmitField(label='Select')



	


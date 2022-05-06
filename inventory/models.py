from inventory import db
from flask_login import UserMixin


class Item(db.Model):
    __tablename__ = 'item'
    ID = db.Column(db.Integer(), primary_key=True)
    barcode = db.Column(db.String(length=8), nullable=False, unique=True)
    serial = db.Column(db.String(length=8), nullable=True)
    manufacturer = db.Column(db.String(length=30), nullable=False)
    name = db.Column(db.String(length=30), nullable=False)
    category = db.Column(db.String(length=30), nullable=False)
    storage = db.Column(db.String(length=30), nullable=True)
    status = db.Column(db.String(length=30), nullable=True)
    notes = db.Column(db.String(length=1024), nullable=True)


class Event(db.Model):
    __tablename__ = 'event'
    ID = db.Column(db.Integer(), primary_key=True)
    event_name = db.Column(db.String(length=30),nullable=False,unique=True)
    event_date_start = db.Column(db.DateTime())
    event_date_end = db.Column(db.DateTime())
    event_client = db.Column(db.String(length=30),nullable=False)
    active = db.Column(db.String(length=30), nullable=False)
    items = db.Column(db.String(length=1024))


    def __repr__(self):
        return f"{self.ID} | {self.event_name} | {self.event_client} | {self.items}"



class User(UserMixin,db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))


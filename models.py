#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, jsonify, abort, session
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form, FlaskForm
from forms import *
from flask_migrate import Migrate
from sqlalchemy.dialects.postgresql import ARRAY
import sys
from datetime import datetime
from sqlalchemy import or_, and_, exc
from wtforms.validators import DataRequired
from wtforms import StringField, SelectField, TextAreaField

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

db = SQLAlchemy()
migrate = Migrate()

# TODO 1: connect to a local postgresql database (done in config.py)
# TODO 2: implement any missing fields, as a database migration using Flask-Migrate (completed)
# TODO 3: implement any missing fields, as a database migration using Flask-Migrate (completed)
# TODO 4 Implement Show and Artist models, and complete all model relationships and properties, as a database migration. (completed)
#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#
class Venue(db.Model):
  __tablename__ = 'Venue'
  id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  name = db.Column(db.String(120), unique=True, nullable=False)
  genres = db.Column(ARRAY(db.String), nullable=False)
  address = db.Column(db.String(120))
  city = db.Column(db.String(120))
  state = db.Column(db.String(120))
  phone = db.Column(db.String(120))
  website = db.Column(db.String(120))
  facebook_link = db.Column(db.String(120))
  seeking_talent = db.Column(db.Boolean, default=False)
  seeking_description = db.Column(db.String(500))
  image_link = db.Column(db.String(500))
  # r1a: a venue can hold many shows
  shows = db.relationship('Show', backref='Venue', uselist=True, foreign_keys='Show.venue_id', lazy="select")

class Artist(db.Model):
  __tablename__ = 'Artist'
  id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  name = db.Column(db.String, unique=True)
  city = db.Column(db.String(120))
  state = db.Column(db.String(120))
  phone = db.Column(db.String(120))
  genres = db.Column(ARRAY(db.String), nullable=False) 
  website = db.Column(db.String(120))
  image_link = db.Column(db.String(500), unique=True)
  facebook_link = db.Column(db.String(120))
  seeking_venue = db.Column(db.Boolean, default=False)
  seeking_description = db.Column(db.String(500))
  # r2a: an artist can play many shows
  shows = db.relationship('Show', backref='Artist', uselist=True, foreign_keys='Show.artist_id', lazy="select")

class Show(db.Model):
  __tablename__ = 'Show'
  id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  image_link = db.Column(db.String(500), db.ForeignKey('Artist.image_link'),nullable=False)
  start_time = db.Column(db.DateTime, nullable=False)
  # r1b:a show can only perform at one venue 
  venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
  # r2b:a show can only have one artist
  artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
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
from models import db, Venue, Artist, Show

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#
app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
migrate = Migrate()

db.init_app(app)
migrate.init_app(app, db)

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime


#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')

#-------------------------------------------------------------------------------------------------#
#  Part1: Venues
#-------------------------------------------------------------------------------------------------#

@app.route('/venues')
def venues():
  # TODO 5: replace with real venues data.(completed)
  venues = Venue.query.all()
  data = []
  areas = set((venue.city, venue.state) for venue in venues)
  for area in areas:
    city, state = area
    area_data = {
      'city': city,
      'state': state,
      'venues': []
    }

    for venue in venues:
      if venue.city == city and venue.state == state:
        venue_data = {
          'id': venue.id,
          'name': venue.name,
        }
        area_data['venues'].append(venue_data)
    data.append(area_data)
  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO 6: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  try:
    search_term = request.form.get('search_term', '')
    venues = Venue.query.filter(Venue.name.ilike(f'%{search_term}%')).all()
    num_results = len(venues)
    
    response = {
        'count': num_results,
        'data': venues
    }
    return render_template('pages/search_venues.html', results=response, search_term=search_term, num_results=num_results)
  except Exception as e:
    print(str(e))
    flash('An error occurred as: ' + str(e))
    return render_template('pages/home.html')
  
@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # Shows the venue page with the given venue_id
  # TODO 7: replace with real venue data from the venues table, using venue_id (completed)
  venue = Venue.query.get(venue_id)
  # If venue_id is not found, return 404
  if not venue:
    abort(404)

  # put the vunue name in the session for later use on the edit_venue page
  session['venue_name'] = venue.name

  # Prepare data model
  data = {
    'id': venue.id,
    'name': venue.name,
    'genres': venue.genres,
    'address': venue.address,
    'city': venue.city,
    'state': venue.state,
    'phone': venue.phone,
    'website': venue.website,
    'facebook_link': venue.facebook_link,
    'seeking_talent': venue.seeking_talent,
    'seeking_description': venue.seeking_description,
    'image_link': venue.image_link,
    'past_shows': [],
    'upcoming_shows': [],
    'past_shows_count': 0,
    'upcoming_shows_count': 0
  }

  # Query the past shows according to the time comparison
  past_shows = db.session.query(Artist, Show).join(Artist.shows).filter(
    and_(
      Show.venue_id == venue_id,
      Show.start_time < datetime.now()
    )
  ).all()
  # Query the upcoming shows according to the time comparison
  upcoming_shows = db.session.query(Artist, Show).join(Artist.shows).filter(
    and_(
      Show.venue_id == venue_id,
      Show.start_time >= datetime.now()
    )
  ).all()

  for artist, show in past_shows:
    data['past_shows'].append({
      'artist_id': artist.id,
      'artist_name': artist.name,
      'artist_image_link': artist.image_link,
      'start_time': show.start_time.strftime('%Y-%m-%dT%H:%M:%S.000Z')
    })
  data['past_shows_count'] = len(past_shows)

  for artist, show in upcoming_shows:
    data['upcoming_shows'].append({
      'artist_id': artist.id,
      'artist_name': artist.name,
      'artist_image_link': artist.image_link,
      'start_time': show.start_time.strftime('%Y-%m-%dT%H:%M:%S.000Z')
    })
  data['upcoming_shows_count'] = len(upcoming_shows)

  return render_template('pages/show_venue.html', venue=data)

#  ----------------------------------------------------------------
#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO 8: insert form data as a new Venue record in the db, instead (completed)
  # TODO 9: modify data to be the data object returned from db insertion (completed)
  # Collect data from the form (http://127.0.0.1:5000/venues/create)
  name = request.form.get('name')
  genres = request.form.getlist('genres')
  address = request.form.get('address')
  city = request.form.get('city')
  state = request.form.get('state')
  phone = request.form.get('phone')
  website = request.form.get('website')
  facebook_link = request.form.get('facebook_link')
  seeking_talent = True if request.form.get('seeking_talent') == 'True' else False
  seeking_description = request.form.get('seeking_description')
  image_link = request.form.get('image_link')

  try:
    # Create Venue objects and assign data to the corresponding properties
    venue = Venue(
      name=name,
      genres=genres,
      address=address,
      city=city,
      state=state,
      phone=phone,
      website=website,
      facebook_link=facebook_link,
      seeking_talent=seeking_talent,
      seeking_description=seeking_description,
      image_link=image_link
    )

    # Add Venue objects to a database session
    db.session.add(venue)
    db.session.commit()

    # on successful db insert, flash success
    flash('Venue ' + name + ' was successfully listed!')
    return render_template('pages/home.html')
  # TODO 10: on unsuccessful db insert, flash an error instead.(completed)
  except exc.SQLAlchemyError as e:
    flash('An error occurred. Venue ' + name + ' could not be listed.')
    db.session.rollback()
    print(str(e))
    return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO 11: Complete this endpoint for taking a venue_id, and using (completed)
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  try:
    venue = Venue.query.get(venue_id)
    if not venue:
      raise Exception('Venue not found.')

    db.session.delete(venue)
    db.session.commit()

    response = {'success': 1}
    return jsonify(response)

  except Exception as e:
    db.session.rollback()
    response = {'success': 0}
    return jsonify(response)


#-------------------------------------------------------------------------------------------------#
#  part 2: Artist
#-------------------------------------------------------------------------------------------------#

#  ----------------------------------------------------------------
#  The Results of The Artists Menu item (on the nav bar)
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO 12: replace with real data returned from querying the database (completed)
  data = Artist.query.all()
  return render_template('pages/artists.html', artists=data)

#  ----------------------------------------------------------------
#  The artists search box on the left side of menu
#  ----------------------------------------------------------------
@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO 13: implement search on artists with partial string search. Ensure it is case-insensitive. (completed)
  try:
    search_term = request.form.get('search_term', '')
    artists = Artist.query.filter(Artist.name.ilike(f'%{search_term}%')).all()
    num_results = len(artists)
    
    response = {
        'count': num_results,
        'data': artists
    }
    
    return render_template('pages/search_artists.html', results=response, search_term=search_term, num_results=num_results)

  except Exception as e:
    print(str(e))
    flash('An error occurred as: ' + str(e))
    return render_template('pages/home.html')

#  ----------------------------------------------------------------
#  The full search results of an artist 
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # Shows the artist page with the given artist_id
  # TODO 14: replace with real artist data from the artist table, using artist_id (completed)
  try:
    artist = Artist.query.get(artist_id)

    if not artist:
        raise Exception('Artist not found.')
    
    # Put the artist name in the session for later use on the edit_artist page
    session['artist_name'] = artist.name

    data = {  
      'id': artist.id,
      'name': artist.name,
      'genres': artist.genres,
      'city': artist.city,
      'state': artist.state,
      'phone': artist.phone,
      'website': artist.website,
      'facebook_link': artist.facebook_link,
      'seeking_venue': artist.seeking_venue,
      'seeking_description': artist.seeking_description,
      'image_link': artist.image_link,
      'past_shows': [],
      'upcoming_shows': [],
      'past_shows_count': 0,
      'upcoming_shows_count': 0,
      'upcoming_shows': [],
      'past_shows': []    
    }
  
    past_shows= db.session.query(Show).filter(
      Show.artist_id == artist.id,
      Show.start_time < datetime.now()
    ).all()

    upcoming_shows = db.session.query(Show).filter(
      Show.artist_id == artist_id,
      Show.start_time >= datetime.now()
    ).all()

    for show in past_shows:
      venue = db.session.query(Venue).filter(Venue.id == show.venue_id).first()
      data['past_shows'].append({
        'artist_id': artist.id,
        'artist_name': artist.name,
        'artist_image_link': artist.image_link,
        'start_time': show.start_time.strftime('%Y-%m-%dT%H:%M:%S.000Z'),
        'venue_id': venue.id,
        'venue_name': venue.name,
        'venue_image_link': venue.image_link
      })
    data['past_shows_count'] = len(past_shows)

    for show in upcoming_shows:
      venue = db.session.query(Venue).filter(Venue.id == show.venue_id).first()
      data['upcoming_shows'].append({
        'artist_id': artist.id,
        'artist_name': artist.name,
        'artist_image_link': artist.image_link,
        'start_time': show.start_time.strftime('%Y-%m-%dT%H:%M:%S.000Z'),
        'venue_id': venue.id,
        'venue_name': venue.name,
        'venue_image_link': venue.image_link
      })
    data['upcoming_shows_count'] = len(upcoming_shows)

    return render_template('pages/show_artist.html', artist=data)

  except Exception as e:
    flash('An error occurred as: ' + str(e))
    return render_template('pages/home.html')

#  ----------------------------------------------------------------
#  Update (Add a new artist record to the database table)
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  # TODO 15: populate form with fields from artist with ID <artist_id> (completed)
  form = ArtistForm()
  artist = Artist.query.get(artist_id)
  artist_name = session.get('artist_name')
  # print(artist_id)
  # print(artist_name)
  if not artist:
    flash('The artist is not found.')
    return redirect(url_for('home'))
  return render_template('forms/edit_artist.html', form=form, artist=artist, artist_name=artist_name)
  
@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO 16: take values from the form submitted, and update existing (completed)
  form = ArtistForm(request.form)  # Instantiate the form with the request data
  artist = Artist.query.get(artist_id)

  try:
    if not artist:
      flash('Artist not found.')
      return redirect(url_for('home'))
    
    # Validate the form data
    if form.validate():
      # Populate the artist object with the form data
      form.populate_obj(artist)  

      db.session.commit()
      flash('Artist information updated successfully!')
      return redirect(url_for('show_artist', artist_id=artist_id))
    else:
      # Handle form validation errors
      for field, errors in form.errors.items():
        for error in errors:
          flash(f'{field}: {error}')
      return redirect(url_for('edit_artist', artist_id=artist_id))

  except Exception as e:
        db.session.rollback()
        print(str(e))
        flash('An error occurred. Artist information could not be updated.')
        return redirect(url_for('show_artist', artist_id=artist_id))

  finally:
        db.session.close()


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.get(venue_id)
  venue_name = session.get('venue_name')
  if not venue:
    flash('The venue is not found.')
    return redirect(url_for('home'))
  # TODO 17: populate form with values from venue with ID <venue_id> (completed)
  return render_template('forms/edit_venue.html', form=form, venue=venue, venue_name=venue_name)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO 18: take values from the form submitted, and update existing (completed)
  form = VenueForm(request.form)  # Instantiate the form with the request data
  venue = Venue.query.get(venue_id)

  try:
    if not venue:
      flash('Venue not found.')
      return redirect(url_for('home'))
    
    if form.validate():
      # Populate the venue object with the form data
      form.populate_obj(venue)  

      db.session.commit()
      flash('Venue information updated successfully!')
      return redirect(url_for('show_venue', venue_id=venue_id))
    else:
      # Handle form validation errors
      for field, errors in form.errors.items():
        for error in errors:
          flash(f'{field}: {error}')
      return redirect(url_for('edit_venue', venue_id=venue_id))
  
  except Exception as e:
    db.session.rollback()
    print(str(e))
    flash('An error occurred. Venue information could not be updated.')
    return redirect(url_for('show_venue', venue_id=venue_id))
  
  finally:
    db.session.close()

#  ----------------------------------------------------------------
#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO 19: insert form data as a new Venue record in the db, instead (completed)
  # TODO 20: modify data to be the data object returned from db insertion (completed)
  # Collect data from the form (http://127.0.0.1:5000/artist/create)
  form = ArtistForm(request.form)
  try:
    if form.validate():
      # Populate the artist object with the form data
      artist = Artist()
      form.populate_obj(artist)

      db.session.add(artist)
      db.session.commit()
      flash('Artist ' + request.form['name'] + ' was successfully listed!')
      return render_template('pages/home.html')
    else:
      # Handle form validation errors
      for field, errors in form.errors.items():
        for error in errors:
          flash(f'{field}: {error}')
      return render_template('pages/home.html')
  
  except Exception as e:
    db.session.rollback()
    print(str(e))
    # TODO 21: on unsuccessful db insert, flash an error instead. (completed)
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
    return render_template('pages/home.html')
  
  finally:
    db.session.close()

#-------------------------------------------------------------------------------------------------#
#  Shows
#-------------------------------------------------------------------------------------------------#

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO 22: replace with real venues data.(conpleted)
  shows = Show.query.join(Artist, Show.artist_id == Artist.id).join(Venue, Show.venue_id == Venue.id).all()
  data = []
  for show in shows:
    # print(show.id, show.start_time, show.venue_id, show.artist_id)
    venue_name = Venue.query.get(show.venue_id).name
    artist_name = Artist.query.get(show.artist_id).name

    data.append({
      "venue_id": show.venue_id,
      "venue_name": venue_name,
      "artist_id": show.artist_id,
      "artist_name": artist_name,
      "artist_image_link": Artist.query.get(show.artist_id).image_link,
      "start_time": show.start_time.strftime('%Y-%m-%dT%H:%M:%S.000Z')
    })
 
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO 23: insert form data as a new Show record in the db, instead (completed)
  form = ShowForm(request.form)
  try:
    if form.validate():
      # Create a new show object with the form data
      show = Show(
        start_time=form.start_time.data,
        venue_id=form.venue_id.data,
        artist_id=form.artist_id.data
      )
      
      # Add a propertiy to the show object from fronted form,
      # the reason is that the form does not have the image_link field, but the show object shoud have
      if not show.image_link:
        artist = Artist.query.get(show.artist_id)
        if artist:
          # Set image_link to the artist's image_link
          show.image_link = artist.image_link
        else:
          flash('Artist not found.')

      db.session.add(show)
      db.session.commit()
      flash('Show was successfully listed!')
      return render_template('pages/home.html')
    else:
      # Handle form validation errors
      for field, errors in form.errors.items():
        for error in errors:
          flash(f'{field}: {error}')
      return render_template('pages/home.html')
  except Exception as e:
    # TODO24: on unsuccessful db insert, flash an error instead.(completed)
    db.session.rollback()
    print(str(e))
    flash('An error occurred. Show could not be listed.')
    return render_template('pages/home.html')
  finally:
    db.session.close()


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''

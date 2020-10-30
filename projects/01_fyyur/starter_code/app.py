#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, jsonify, abort
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import Bundle
from sqlalchemy import distinct, or_
import logging
from logging import Formatter, FileHandler
from flask_wtf import FlaskForm
from flask_wtf.csrf import CSRFProtect, CSRFError
from forms import *
from flask_migrate import Migrate
import sys

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app,db,compare_type=True)
csrf = CSRFProtect(app)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
  __tablename__ = 'venues'

  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String, nullable=False, unique=True)
  genres = db.Column(postgresql.ARRAY(db.String), nullable=False)
  address = db.Column(db.String(120), nullable=False, unique=True)
  city = db.Column(db.String(120), nullable=False)
  state = db.Column(db.String(120), nullable=False)
  phone = db.Column(db.String(12), nullable=False, unique=True)
  website = db.Column(db.String(120))
  facebook_link = db.Column(db.String(120))
  seeking_talent = db.Column(db.Boolean, nullable=False)
  seeking_description = db.Column(db.String(500))
  image_link = db.Column(db.String(500), nullable=False, unique=True)
  
  shows = db.relationship('Show', backref='venue', cascade='all, delete-orphan', lazy=True)

  def __repr__(self):
    return f'<Venue ID: {self.id}, name: {self.name}>'

class Artist(db.Model):
  __tablename__ = 'artists'

  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String, nullable=False, unique=True)
  genres = db.Column(postgresql.ARRAY(db.String), nullable=False)
  city = db.Column(db.String(120), nullable=False)
  state = db.Column(db.String(120), nullable=False)
  phone = db.Column(db.String(12), nullable=False, unique=True)
  website = db.Column(db.String(120))
  facebook_link = db.Column(db.String(120))
  seeking_venue = db.Column(db.Boolean, nullable=False)
  seeking_description = db.Column(db.String(500))
  image_link = db.Column(db.String(500), nullable=False, unique=True)
  
  shows = db.relationship('Show', backref='artist', cascade='all, delete-orphan', lazy=True)

  def __repr__(self):
    return f'<Artist ID: {self.id}, name: {self.name}>'

class Show(db.Model):
  __tablename__ = 'shows'

  id = db.Column(db.Integer, primary_key=True)
  artist_id = db.Column(db.Integer, db.ForeignKey('artists.id'), nullable=False)
  venue_id = db.Column(db.Integer, db.ForeignKey('venues.id'), nullable=False)
  start_time = db.Column(db.DateTime(timezone=False), nullable=False)

  def __repr__(self):
    return f'<Show ID: {self.id}, artist ID: {self.artist_id}, venue ID: {self.venue_id}>'

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  if isinstance(value, str):
    date = dateutil.parser.parse(value)
  else:
    date = value
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():

  data = []
  places = Bundle('places', Venue.city, Venue.state)

  for row in db.session.query(places).order_by(Venue.city).distinct():

    city = row.places.city
    state = row.places.state
    place = {}
    place['city'] = city
    place['state'] = state
    venues = []

    for venue_id, venue_name in db.session.query(Venue.id, Venue.name).filter_by(city=city).order_by(Venue.name):
      this_venue = {}
      this_venue['id'] = venue_id
      this_venue['name'] = venue_name

      num_upcoming_shows = db.session.query(Show.id).filter(
        Show.venue_id == venue_id, 
        Show.start_time > datetime.now()
      ).count()
      this_venue['num_upcoming_shows'] = num_upcoming_shows

      venues.append(this_venue)
    
    place['venues'] = venues
    data.append(place)
  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
@csrf.exempt
def search_venues():
  search_term = request.form.get('search_term')
  search_term_formatted = f'%{search_term}%'

  response = {}
  data = []
  count = 0

  for row in Venue.query.filter(Venue.name.ilike(search_term_formatted)):
    count += 1
    venue = {}
    venue['id'] = row.id
    venue['name'] = row.name

    num_upcoming_shows = db.session.query(Show.id).filter(
        Show.venue_id == row.id, 
        Show.start_time > datetime.now()
    ).count()
    venue['num_upcoming_shows'] = num_upcoming_shows

    data.append(venue)
  
  response['count'] = count
  response['data'] = data
  return render_template('pages/search_venues.html', results=response, search_term=search_term)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  this_venue = Venue.query.get(venue_id)

  data = {}
  data['id'] = venue_id
  data['name'] = this_venue.name
  data['genres'] = this_venue.genres
  data['address'] = this_venue.address
  data['city'] = this_venue.city
  data['state'] = this_venue.state
  data['phone'] = this_venue.phone
  data['website'] = this_venue.website
  data['facebook_link'] = this_venue.facebook_link
  data['seeking_talent'] = this_venue.seeking_talent
  data['seeking_description'] = this_venue.seeking_description
  data['image_link'] = this_venue.image_link

  past_shows = []
  past_shows_count = 0
  for artist_id, artist_name, artist_image_link, show_start_time in db.session.query(
    Artist.id, Artist.name, Artist.image_link
    ).join(Artist.shows
    ).add_columns(Show.start_time
    ).filter(Show.venue_id==venue_id
    ).filter(Show.start_time<datetime.now()):
    
    show = {}
    show['artist_id'] = artist_id
    show['artist_name'] = artist_name
    show['artist_image_link'] = artist_image_link
    show['start_time'] = show_start_time

    past_shows.append(show)
    past_shows_count += 1
  data['past_shows'] = past_shows
  data['past_shows_count'] = past_shows_count

  upcoming_shows = []
  upcoming_shows_count = 0
  for artist_id, artist_name, artist_image_link, show_start_time in db.session.query(
    Artist.id, Artist.name, Artist.image_link
    ).join(Artist.shows
    ).add_columns(Show.start_time
    ).filter(Show.venue_id==venue_id
    ).filter(Show.start_time>datetime.now()):

    show = {}
    show['artist_id'] = artist_id
    show['artist_name'] = artist_name
    show['artist_image_link'] = artist_image_link
    show['start_time'] = show_start_time

    upcoming_shows.append(show)
    upcoming_shows_count += 1
  data['upcoming_shows'] = upcoming_shows
  data['upcoming_shows_count'] = upcoming_shows_count

  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET', 'POST'])
def create_venue_form():
  form = VenueForm()

  if form.validate_on_submit():
    error = False

    name = request.form.get('name')
    genres = request.form.getlist('genres')
    address = request.form.get('address')
    city = request.form.get('city')
    state = request.form.get('state')
    phone = request.form.get('phone')
    website = request.form.get('website')
    facebook_link = request.form.get('facebook_link')
    
    talent = request.form.get('seeking_talent')
    if talent == 'y':
      seeking_talent = True
    else:
      seeking_talent = False
    
    seeking_description = request.form.get('seeking_description')
    image_link = request.form.get('image_link')

    try:
      new_venue = Venue(
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
      db.session.add(new_venue)
      db.session.commit()
    except:
      error = True
      db.session.rollback()
      print(sys.exc_info())
    finally:
      db.session.close()
    if error:
      flash('An error occurred. Venue ' + name + ' could not be listed.')
    else:
      flash('Venue ' + name + ' was successfully listed!')
    
    return render_template('pages/home.html')
  else:
    for key in form.errors:
      flash(form.errors[key])
    
    return render_template('forms/new_venue.html', form=form)

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  data = []

  for artist_id, artist_name in db.session.query(Artist.id, Artist.name).order_by(Artist.name):
    artist = {}
    artist['id'] = artist_id
    artist['name'] = artist_name
    data.append(artist)
  
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
@csrf.exempt
def search_artists():
  search_term = request.form.get('search_term')
  search_term_formatted = f'%{search_term}%'

  response = {}
  data = []
  count = 0

  for row in Artist.query.filter(Artist.name.ilike(search_term_formatted)):
    count += 1
    artist = {}
    artist['id'] = row.id
    artist['name'] = row.name

    num_upcoming_shows = db.session.query(Show.id).filter(
        Show.artist_id == row.id, 
        Show.start_time > datetime.now()
    ).count()
    artist['num_upcoming_shows'] = num_upcoming_shows

    data.append(artist)
  
  response['count'] = count
  response['data'] = data

  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  this_artist = Artist.query.get(artist_id)

  data = {}
  data['id'] = artist_id
  data['name'] = this_artist.name
  data['genres'] = this_artist.genres
  data['city'] = this_artist.city
  data['state'] = this_artist.state
  data['phone'] = this_artist.phone
  data['website'] = this_artist.website
  data['facebook_link'] = this_artist.facebook_link
  data['seeking_venue'] = this_artist.seeking_venue
  data['seeking_description'] = this_artist.seeking_description
  data['image_link'] = this_artist.image_link

  past_shows = []
  past_shows_count = 0
  for venue_id, venue_name, venue_image_link, show_start_time in db.session.query(
    Venue.id, Venue.name, Venue.image_link
    ).join(Venue.shows
    ).add_columns(Show.start_time
    ).filter(Show.artist_id==artist_id
    ).filter(Show.start_time<datetime.now()):
  
    show = {}
    show['venue_id'] = venue_id
    show['venue_name'] = venue_name
    show['venue_image_link'] = venue_image_link
    show['start_time'] = show_start_time
    past_shows.append(show)
    past_shows_count += 1
  data['past_shows'] = past_shows
  data['past_shows_count'] = past_shows_count

  upcoming_shows = []
  upcoming_shows_count = 0
  for venue_id, venue_name, venue_image_link, show_start_time in db.session.query(
    Venue.id, Venue.name, Venue.image_link
    ).join(Venue.shows
    ).add_columns(Show.start_time
    ).filter(Show.artist_id==artist_id
    ).filter(Show.start_time>datetime.now()):

    show = {}
    show['venue_id'] = venue_id
    show['venue_name'] = venue_name
    show['venue_image_link'] = venue_image_link
    show['start_time'] = show_start_time
    upcoming_shows.append(show)
    upcoming_shows_count += 1
  data['upcoming_shows'] = upcoming_shows
  data['upcoming_shows_count'] = upcoming_shows_count

  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  this_artist = Artist.query.get(artist_id)

  artist = {
    'id': artist_id,
    'name': this_artist.name,
    'genres': this_artist.genres,
    'city': this_artist.city,
    'state': this_artist.state,
    'phone': this_artist.phone,
    'website': this_artist.website,
    'facebook_link': this_artist.facebook_link,
    'seeking_venue': this_artist.seeking_venue,
    'seeking_description': this_artist.seeking_description,
    'image_link': this_artist.image_link
  }

  form = ArtistForm()
  form.name.data = artist['name']
  form.genres.data = artist['genres']
  form.city.data = artist['city']
  form.state.data = artist['state']
  form.phone.data = artist['phone']
  form.website.data = artist['website']
  form.facebook_link.data = artist['facebook_link']
  form.seeking_venue.data = artist['seeking_venue']
  form.seeking_description.data = artist['seeking_description']
  form.image_link.data = artist['image_link']
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  this_artist = Artist.query.get(artist_id)
  form = ArtistForm()

  if form.validate_on_submit():
    error = False
    try:
      this_artist.name = request.form.get('name')
      this_artist.genres = request.form.getlist('genres')
      this_artist.city = request.form.get('city')
      this_artist.state = request.form.get('state')
      this_artist.phone = request.form.get('phone')
      this_artist.website = request.form.get('website')
      this_artist.facebook_link = request.form.get('facebook_link')

      seeking_venue = request.form.get('seeking_venue')
      if seeking_venue == 'y':
        this_artist.seeking_venue = True
      else:
        this_artist.seeking_venue = False

      this_artist.seeking_description = request.form.get('seeking_description')
      this_artist.image_link = request.form.get('image_link')

      db.session.commit()
    except:
      error = True
      db.session.rollback()
      print(sys.exc_info())
    finally:
      db.session.close()
    if error:
      flash('An error occurred. Artist ' + request.form.get('name') + ' could not be updated.')
      return redirect(url_for('edit_artist_submission', artist_id=artist_id))
    else:
      flash('Artist ' + request.form.get('name') + ' was updated successfully!')
    
    return redirect(url_for('show_artist', artist_id=artist_id))
  else:
    for key in form.errors:
      flash(form.errors[key])
    return redirect(url_for('edit_artist_submission', artist_id=artist_id))
    
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  this_venue = Venue.query.get(venue_id)

  venue = {
    'id': venue_id,
    'name': this_venue.name,
    'genres': this_venue.genres,
    'address': this_venue.address,
    'city': this_venue.city,
    'state': this_venue.state,
    'phone': this_venue.phone,
    'website': this_venue.website,
    'facebook_link': this_venue.facebook_link,
    'seeking_talent': this_venue.seeking_talent,
    'seeking_description': this_venue.seeking_description,
    'image_link': this_venue.image_link
  }

  form = VenueForm()
  form.name.data = venue['name']
  form.genres.data = venue['genres']
  form.address.data = venue['address']
  form.city.data = venue['city']
  form.state.data = venue['state']
  form.phone.data = venue['phone']
  form.website.data = venue['website']
  form.facebook_link.data = venue['facebook_link']
  form.seeking_talent.data = venue['seeking_talent']
  form.seeking_description.data = venue['seeking_description']
  form.image_link.data = venue['image_link']

  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  this_venue = Venue.query.get(venue_id)
  form = VenueForm()

  if form.validate_on_submit():
    error = False
    try:
      this_venue.name = request.form.get('name')
      this_venue.genres = request.form.getlist('genres')
      this_venue.address = request.form.get('address')
      this_venue.city = request.form.get('city')
      this_venue.state = request.form.get('state')
      this_venue.phone = request.form.get('phone')
      this_venue.website = request.form.get('website')
      this_venue.facebook_link = request.form.get('facebook_link')

      seeking_talent = request.form.get('seeking_talent')
      if seeking_talent == 'y':
        this_venue.seeking_talent = True
      else:
        this_venue.seeking_talent = False

      this_venue.seeking_description = request.form.get('seeking_description')
      this_venue.image_link = request.form.get('image_link')

      db.session.commit()
    except:
      error = True
      db.session.rollback()
      print(sys.exc_info())
    finally:
      db.session.close()
    if error:
      flash('An error occurred. Venue ' + request.form.get('name') + ' could not be updated.')
      return redirect(url_for('edit_venue_submission', venue_id=venue_id))
    else:
      flash('Venue ' + request.form.get('name') + ' was updated successfully!')
    
    return redirect(url_for('show_venue', venue_id=venue_id))
  else:
    for key in form.errors:
      flash(form.errors[key])
    
    return redirect(url_for('edit_venue_submission', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET', 'POST'])
def create_artist_form():
  form = ArtistForm()

  if form.validate_on_submit():
    error = False

    name = request.form.get('name')
    genres = request.form.getlist('genres')
    city = request.form.get('city')
    state = request.form.get('state')
    phone = request.form.get('phone')
    website = request.form.get('website')
    facebook_link = request.form.get('facebook_link')
    
    venue = request.form.get('seeking_venue')
    if venue == 'y':
      seeking_venue = True
    else:
      seeking_venue = False

    seeking_description = request.form.get('seeking_description')
    image_link = request.form.get('image_link')

    try:
      new_artist = Artist(
        name=name,
        genres=genres,
        city=city,
        state=state,
        phone=phone,
        website=website,
        facebook_link=facebook_link,
        seeking_venue=seeking_venue,
        seeking_description=seeking_description,
        image_link=image_link
      )
      db.session.add(new_artist)
      db.session.commit()
    except:
      error = True
      db.session.rollback()
      print(sys.exc_info())
    finally:
      db.session.close()
    if error:
      flash('An error occurred. Artist ' + name + ' could not be listed.')
    else:
      flash('Artist ' + name + ' was successfully listed!')
    
    return render_template('pages/home.html')
  else:
    for key in form.errors:
      flash(form.errors[key])
    
    return render_template('forms/new_artist.html', form=form)

#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  data = []

  for row in db.session.query(Artist.id, Artist.name, Artist.image_link
   ).join(Artist.shows
   ).add_columns(Show.start_time, Show.venue_id
   ).filter(Show.start_time > datetime.now()
   ).order_by(Show.start_time).all():

    show = {}
    show['venue_id'] = row.venue_id
    show['venue_name'] = Venue.query.get(row.venue_id).name
    show['artist_id'] = row.id
    show['artist_name'] = row.name
    show['artist_image_link'] = row.image_link
    show['start_time'] = format_datetime(row.start_time)
    data.append(show)

  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create', methods=['GET', 'POST'])
def create_shows():
  form = ShowForm()

  if form.validate_on_submit():
    error = False

    artist_id = request.form.get('artist_id')
    venue_id = request.form.get('venue_id')
    start_time = request.form.get('start_time')

    try:
      new_show = Show(
        artist_id=artist_id,
        venue_id=venue_id,
        start_time=start_time
      )
      db.session.add(new_show)
      db.session.commit()
    except:
      error = True
      db.session.rollback()
      print(sys.exc_info())
    finally:
      db.session.close()
    if error:
      flash('An error occurred. Show could not be listed.')
    else:
      flash('Show was successfully listed!')
    
    return render_template('pages/home.html')
  else:
    for key in form.errors:
      flash(form.errors[key])
    
    return render_template('forms/new_show.html', form=form)

@app.route('/shows/search', methods=['POST'])
@csrf.exempt
def search_shows():
  search_term = request.form.get('search_term')
  search_term_formatted = f'%{search_term}%'

  response = {}
  data = []
  count = 0

  for artist_name, show_id, show_start_time, venue_name in db.session.query(Artist.name
   ).join(Artist.shows
   ).join(Venue
   ).add_columns(Show.id, Show.start_time, Venue.name
   ).filter(Show.start_time > datetime.now()
   ).filter(or_(Artist.name.ilike(search_term_formatted), Venue.name.ilike(search_term_formatted))
   ).order_by(Show.start_time):
    count += 1
    show = {}
    show['id'] = show_id
    show['artist_name'] = artist_name
    show['venue_name'] = venue_name
    show['start_time'] = format_datetime(show_start_time)
    data.append(show)
  
  response['count'] = count
  response['data'] = data

  return render_template('pages/search_shows.html', results=response, search_term=search_term)

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500

@app.errorhandler(CSRFError)
def handle_csrf_error(e):
  return render_template('errors/csrf_error.html', reason=e.description), 400


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

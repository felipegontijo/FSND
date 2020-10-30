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

# TODO: connect to a local database

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

  # TODO: implement any missing fields, as a database migration using Flask-Migrate

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

  # TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

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
  # date = dateutil.parser.parse(value)
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
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  data = []
  places = Bundle('places', Venue.city, Venue.state)
  for row in db.session.query(places).distinct():
    city = row.places.city
    state = row.places.state
    place = {}
    place['city'] = city
    place['state'] = state
    venues = []
    for venue_id, venue_name in db.session.query(Venue.id, Venue.name).filter_by(city=city):
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
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
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
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id

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
  for artist_id, artist_name, artist_image_link, show_start_time in db.session.query(Artist.id, Artist.name, Artist.image_link).join(Artist.shows).add_columns(Show.start_time).filter(Show.venue_id==venue_id).filter(Show.start_time<datetime.now()):
    show = {}
    show['artist_id'] = artist_id
    show['artist_name'] = artist_name
    show['artist_image_link'] = artist_image_link
    show['start_time'] = show_start_time
    past_shows.append(show)
  data['past_shows'] = past_shows

  upcoming_shows = []
  for artist_id, artist_name, artist_image_link, show_start_time in db.session.query(Artist.id, Artist.name, Artist.image_link).join(Artist.shows).add_columns(Show.start_time).filter(Show.venue_id==venue_id).filter(Show.start_time>datetime.now()):
    show = {}
    show['artist_id'] = artist_id
    show['artist_name'] = artist_name
    show['artist_image_link'] = artist_image_link
    show['start_time'] = show_start_time
    upcoming_shows.append(show)
  data['upcoming_shows'] = upcoming_shows

  data['past_shows_count'] = db.session.query(Show.id).filter(
    Show.venue_id == venue_id, 
    Show.start_time < datetime.now()
  ).count()

  data['upcoming_shows_count'] = db.session.query(Show.id).filter(
    Show.venue_id == venue_id, 
    Show.start_time > datetime.now()
  ).count()

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
  # TODO: replace with real data returned from querying the database
  data = []
  for artist_id, artist_name in db.session.query(Artist.id, Artist.name):
    artist = {}
    artist['id'] = artist_id
    artist['name'] = artist_name
    data.append(artist)
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
@csrf.exempt
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
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
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id

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
  for venue_id, venue_name, venue_image_link, show_start_time in db.session.query(Venue.id, Venue.name, Venue.image_link).join(Venue.shows).add_columns(Show.start_time).filter(Show.artist_id==artist_id).filter(Show.start_time<datetime.now()):
    show = {}
    show['venue_id'] = venue_id
    show['venue_name'] = venue_name
    show['venue_image_link'] = venue_image_link
    show['start_time'] = show_start_time
    past_shows.append(show)
  data['past_shows'] = past_shows

  upcoming_shows = []
  for venue_id, venue_name, venue_image_link, show_start_time in db.session.query(Venue.id, Venue.name, Venue.image_link).join(Venue.shows).add_columns(Show.start_time).filter(Show.artist_id==artist_id).filter(Show.start_time>datetime.now()):
    show = {}
    show['venue_id'] = venue_id
    show['venue_name'] = venue_name
    show['venue_image_link'] = venue_image_link
    show['start_time'] = show_start_time
    upcoming_shows.append(show)
  data['upcoming_shows'] = upcoming_shows

  data['past_shows_count'] = db.session.query(Show.id).filter(
    Show.artist_id == artist_id, 
    Show.start_time < datetime.now()
  ).count()

  data['upcoming_shows_count'] = db.session.query(Show.id).filter(
    Show.artist_id == artist_id, 
    Show.start_time > datetime.now()
  ).count()

  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist={
    "id": 4,
    "name": "Guns N Petals",
    "genres": ["Rock n Roll"],
    "city": "San Francisco",
    "state": "CA",
    "phone": "326-123-5000",
    "website": "https://www.gunsnpetalsband.com",
    "facebook_link": "https://www.facebook.com/GunsNPetals",
    "seeking_venue": True,
    "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
    "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
  }
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue={
    "id": 1,
    "name": "The Musical Hop",
    "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
    "address": "1015 Folsom Street",
    "city": "San Francisco",
    "state": "CA",
    "phone": "123-123-1234",
    "website": "https://www.themusicalhop.com",
    "facebook_link": "https://www.facebook.com/TheMusicalHop",
    "seeking_talent": True,
    "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
    "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
  }
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  return redirect(url_for('show_venue', venue_id=venue_id))

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
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  data = []

  for row in db.session.query(Artist.id, Artist.name, Artist.image_link).join(Artist.shows).add_columns(Show.start_time, Show.venue_id).filter(Show.start_time > datetime.now()).order_by(Show.start_time).all():
    show = {}
    show['venue_id'] = row.venue_id
    show['venue_name'] = Venue.query.get(row.venue_id).name
    show['artist_id'] = row.id
    show['artist_name'] = row.name
    show['artist_image_link'] = row.image_link
    show['start_time'] = format_datetime(row.start_time)
    print(show)
    data.append(show)

  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create', methods=['GET', 'POST'])
def create_shows():
  # renders form. do not touch.
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

  for artist_name, show_id, show_start_time, venue_name in db.session.query(Artist.name).join(Artist.shows).join(Venue).add_columns(Show.id, Show.start_time, Venue.name).filter(Show.start_time > datetime.now()).filter(or_(Artist.name.ilike(search_term_formatted), Venue.name.ilike(search_term_formatted))):
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

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''

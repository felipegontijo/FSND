import json
import dateutil.parser
import babel
from flask import (
  Flask,
  render_template, 
  request, Response, 
  flash, 
  redirect, 
  url_for, 
  jsonify, 
  abort)
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import Bundle
from sqlalchemy import distinct, or_
import logging
from logging import Formatter, FileHandler
from flask_wtf import FlaskForm
from flask_wtf.csrf import CSRFProtect, CSRFError
from forms import *
from flask_migrate import Migrate
import sys
from models import app, db, Venue, Artist, Show
from datetime import datetime

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app.config.from_object('config.Config')
moment = Moment(app)
db.init_app(app)

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

  locals = []
  venues = Venue.query.all()
  for place in Venue.query.distinct(Venue.city, Venue.state).all():
    locals.append({
      'city': place.city,
      'state': place.state,
      'venues': [{
        'id': venue.id,
        'name': venue.name,
      } for venue in venues if
          venue.city == place.city and venue.state == place.state]
    })
  return render_template('pages/venues.html', areas=locals)

@app.route('/venues/search', methods=['POST'])
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

  past_shows = db.session.query(Artist, Show).join(Show).join(Venue).\
    filter(
      Show.venue_id == venue_id,
      Show.artist_id == Artist.id,
      Show.start_time < datetime.now()
    ).\
      all()

  upcoming_shows = db.session.query(Artist, Show).join(Show).join(Venue).\
    filter(
      Show.venue_id == venue_id,
      Show.artist_id == Artist.id,
      Show.start_time > datetime.now()
    ).\
      all()

  venue = Venue.query.get(venue_id)

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
    'past_shows': [{
      'artist_id': artist.id,
      'artist_name': artist.name,
      'artist_image_link': artist.image_link,
      'start_time': show.start_time
    } for artist, show in past_shows],
    'upcoming_shows': [{
      'artist_id': artist.id,
      'artist_name': artist.name,
      'artist_image_link': artist.image_link,
      'start_time': show.start_time
    } for artist, show in upcoming_shows],
    'past_shows_count': len(past_shows),
    'upcoming_shows_count': len(upcoming_shows)
  }

  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET', 'POST'])
def create_venue_form():
  form = VenueForm(request.form)

  if form.validate_on_submit():
    error = False

    try:
      venue = Venue()
      form.populate_obj(venue)
      
      talent = request.form.get('seeking_talent')
      if talent == 'y':
        venue.seeking_talent = True
      else:
        venue.seeking_talent = False
      
      db.session.add(venue)
      db.session.commit()
    except:
      error = True
      db.session.rollback()
      print(sys.exc_info())
    finally:
      db.session.close()
    if error:
      flash('An error occurred. Venue could not be listed.')
    else:
      flash('Venue was successfully listed!')
    
    return render_template('pages/home.html')
  else:
    for field, err in form.errors.items():
      flash('Error: ' + field + ' ' + '|'.join(err))
    
    return render_template('forms/new_venue.html', form=form)

@app.route('/venues/<int:venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  error = False
  try:
    venue = Venue.query.get(venue_id)
    name = venue.name
    db.session.delete(venue)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    flash('An error occurred. Venue ' + name + ' could not be deleted')
  else:
    flash('Venue ' + name + ' has been deleted successfully.')
    return jsonify({ 'success': True })

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

  past_shows = db.session.query(Venue, Show).join(Show).join(Artist).\
    filter(
      Show.venue_id == Venue.id,
      Show.artist_id == artist_id,
      Show.start_time < datetime.now()
    ).\
      all()

  upcoming_shows = db.session.query(Venue, Show).join(Show).join(Artist).\
    filter(
      Show.venue_id == Venue.id,
      Show.artist_id == artist_id,
      Show.start_time > datetime.now()
    ).\
      all()

  artist = Artist.query.get(artist_id)

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
    'past_shows': [{
      'venue_id': venue.id,
      'venue_name': venue.name,
      'venue_image_link': venue.image_link,
      'start_time': show.start_time
    } for venue, show in past_shows],
    'upcoming_shows': [{
      'venue_id': venue.id,
      'venue_name': venue.name,
      'venue_image_link': venue.image_link,
      'start_time': show.start_time
    } for venue, show in upcoming_shows],
    'past_shows_count': len(past_shows),
    'upcoming_shows_count': len(upcoming_shows)
  }

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
  artist = Artist.query.get(artist_id)
  form = ArtistForm(request.form)

  if form.validate_on_submit():
    error = False
    try:
      form.populate_obj(artist)

      seeking_venue = request.form.get('seeking_venue')
      if seeking_venue == 'y':
        artist.seeking_venue = True
      else:
        artist.seeking_venue = False

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
    for field, err in form.errors.items():
      flash('Error: ' + field + ' ' + '|'.join(err))
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
    for field, err in form.errors.items():
      flash('Error: ' + field + ' ' + '|'.join(err))
    
    return redirect(url_for('edit_venue_submission', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET', 'POST'])
def create_artist_form():
  form = ArtistForm(request.form)

  if form.validate_on_submit():
    error = False

    try:
      artist = Artist()
      form.populate_obj(artist)
    
      venue = request.form.get('seeking_venue')
      if venue == 'y':
        artist.seeking_venue = True
      else:
        artist.seeking_venue = False

      db.session.add(artist)
      db.session.commit()
    except:
      error = True
      db.session.rollback()
      print(sys.exc_info())
    finally:
      db.session.close()
    if error:
      flash('An error occurred. Artist could not be listed.')
    else:
      flash('Artist was successfully listed!')
    
    return render_template('pages/home.html')
  else:
    for field, err in form.errors.items():
      flash('Error: ' + field + ' ' + '|'.join(err))
    
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

    try:
      show = Show()
      form.populate_obj(show)

      db.session.add(show)
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
    for field, err in form.errors.items():
      flash('Error: ' + field + ' ' + '|'.join(err))
    
    return render_template('forms/new_show.html', form=form)

@app.route('/shows/search', methods=['POST'])
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

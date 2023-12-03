#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
import collections
import collections.abc
collections.Callable = collections.abc.Callable
import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

# TODO: connect to a local postgresql database
migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    genres = db.Column(db.String(120))
    web = db.Column(db.String(120))
    seeking_talent = db.Column(db.String(120))
    seeking_description = db.Column(db.String(120))
    shows = db.relationship("Show", backref="venues")
with app.app_context():
  db.create_all()

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    genres = db.Column(db.String(120))
    web = db.Column(db.String(120))
    seeking_venue = db.Column(db.String(120))
    seeking_description = db.Column(db.String(120))
    shows = db.relationship("Show", backref="artists")
with app.app_context():
  db.create_all()

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
class Show(db.Model):
    __tablename__ = 'Show'
    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey("Venue.id"))
    artist_id = db.Column(db.Integer, db.ForeignKey("Artist.id"))
    start_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
with app.app_context(): 
  db.create_all()
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


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  data = []
  now = datetime.now()
  venues = Venue.query.all()
  for venue in venues:
      venue_shows = Show.query.filter_by(venue_id=venue.id).all()
      num_upcoming_shows = 0
      for show in venue_shows:
          if show.start_time > now:
              num_upcoming_shows += 1
      data.append({         
        "city": venue.city,
        "state": venue.state,
        "venues": [{
            "id": venue.id,
            "name": venue.name,
            "num_upcoming_shows": num_upcoming_shows,
            }]
        })
  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on venues with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_term = request.form.get('search_term', '')
  responses = {}
  data = []
  searchs = Venue.query.filter(Venue.name.ilike(f'%{search_term}%')).all()
  responses["count"] = len(searchs)
  responses["data"] = []
  for search in searchs:
    data = {
      "id": search.id,
      "name": search.name,
    }   
    responses["data"].append(data)
  return render_template('pages/search_venues.html', results=responses, search_term=search_term)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  venue = Venue.query.filter_by(id = venue_id).first()
  past_shows_query = db.session.query(Show).join(Artist).filter(Show.venue_id==venue_id).filter(Show.start_time<datetime.now()).all()   
  past_shows = []
  past_shows_count = 0
  for show in past_shows_query:
    past_shows_count+=1
    past_shows.append({
              "artist_id": show.artist_id,
              "artist_name": show.artists.name,
              "artist_image_link": show.artists.image_link,
              "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')
          })
    
  upcoming_shows_query = db.session.query(Show).join(Venue).filter(Show.venue_id==venue_id).filter(Show. start_time>datetime.now()).all()   
  upcoming_shows = []
  upcoming_shows_count = 0
  for show in upcoming_shows_query:
    upcoming_shows_count+=1
    upcoming_shows.append({
              "artist_id": show.artist_id,
              "artist_name": show.artists.name,
              "artist_image_link": show.artists.image_link,
              "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')
      })
  data={
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres.split(','),
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "web": venue.web,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": past_shows_count,
    "upcoming_shows_count": upcoming_shows_count,
  }
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  # on successful db insert, flash success
  # flash('Venue ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  venue = Venue()
  form = VenueForm(request.form, meta={'csrf': False})
  if form.validate_on_submit():
    try:
      venue.name = form['name'].data
      venue.state = form['state'].data
      venue.city = form['city'].data
      venue.address = form['address'].data
      venue.phone = form['phone'].data
      venue.genres = ",".join(form['genres'].data)
      venue.image_link = form['image_link'].data
      venue.facebook_link = form['facebook_link'].data
      venue.web = form['website_link'].data
      venue.seeking_talent = form['seeking_talent'].data
      venue.seeking_description = form['seeking_description'].data
      db.session.add(venue)
      db.session.commit()
      flash('Venue ' + form['name'].data + ' was successfully listed!')
    except Exception:
      db.session.rollback()
      flash('An error occurred. Venue ' + form['name'].data + ' could not be listed.')
    finally:
      db.session.close()
  else:
    for field, message in form.errors.items():
      flash(field + ' - ' + str(message), 'danger')  
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):  
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  venue = Venue.query.get(venue_id)
  try:
    db.session.delete(venue)
    db.session.commit()
    flash(venue.name + " was deleted successfully!")
  except Exception:
    db.session.rollback()
    flash(venue.name + " was not deleted successfully!")
  finally:
    db.session.close()  
  return render_template('pages/home.html')   

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  data = []
  artists = Artist.query.all()
  for artist in artists:
      data.append({         
        "id": artist.id,
        "name": artist.name,
        })
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_term = request.form.get('search_term', '')
  responses = {}
  data = []
  searchs = Artist.query.filter(Artist.name.ilike(f'%{search_term}%')).all()
  responses["count"] = len(searchs)
  responses["data"] = []
  for search in searchs:
    data = {
      "id": search.id,
      "name": search.name,
    }   
    responses["data"].append(data)
  return render_template('pages/search_venues.html', results=responses, search_term=search_term)

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
    artist = Artist.query.filter_by(id = artist_id).first()
    past_shows_query = db.session.query(Show).join(Venue).filter(Show.artist_id==artist_id).filter(Show.start_time<datetime.now()).all()   
    past_shows = []
    past_shows_count = 0
    for show in past_shows_query:
      past_shows_count+=1
      past_shows.append({
                "venue_id": show.venue_id,
                "venue_name": show.venues.name,
                "venue_image_link": show.venues.image_link,
                "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')
            })
      
    upcoming_shows_query = db.session.query(Show).join(Venue).filter(Show.artist_id==artist_id).filter(Show. start_time>datetime.now()).all()   
    upcoming_shows = []
    upcoming_shows_count = 0
    for show in upcoming_shows_query:
      upcoming_shows_count+=1
      upcoming_shows.append({
                "venue_id": show.venue_id,
                "venue_name": show.venues.name,
                "venue_image_link": show.venues.image_link,
                "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')
        })
    data = {
        "id": artist.id,
        "name": artist.name,
        "genres": artist.genres.split(','),
        "city": artist.city,
        "state": artist.state,
        "phone": artist.phone,
        "web": artist.web,
        "facebook_link": artist.facebook_link,
        "seeking_venue": artist.seeking_venue,
        "seeking_description": artist.seeking_description,
        "image_link": artist.image_link,
        "past_shows": past_shows,
        "past_shows_count": past_shows_count,
        "upcoming_shows": upcoming_shows,
        "upcoming_shows_count": upcoming_shows_count
    }

    return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  # # TODO: populate form with fields from artist with ID <artist_id>
  # return render_template('forms/edit_artist.html', form=form, artist=artist)
    Artist_form = ArtistForm()  
    artist = Artist.query.get(artist_id)
    Artist_form.genres.data = artist.genres.split(",")
    return render_template('forms/edit_artist.html', form=Artist_form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
    form = ArtistForm(request.form)
    try:
        artist = Artist.query.get(artist_id)
        artist.name = form['name'].data
        artist.city=form['city'].data
        artist.state=form['state'].data
        artist.phone=form['phone'].data
        artist.genres=",".join(form['genres'].data)
        artist.facebook_link=form['facebook_link'].data
        artist.image_link=form['image_link'].data
        artist.seeking_venue=form['seeking_venue'].data
        artist.seeking_description=form['seeking_description'].data
        artist.web=form['website_link'].data
        db.session.add(artist)
        db.session.commit()
        flash("Artist " + form['name'].data + " was successfully edited!")
    except:
        db.session.rollback()
        flash("Artist " +  form['name'].data + "was not edited successfully.")
    finally:
        db.session.close()
    return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  # # TODO: populate form with values from venue with ID <venue_id>
  # return render_template('forms/edit_venue.html', form=form, venue=venue)
    Venue_form = VenueForm()
    venue = Venue.query.get(venue_id)
    Venue_form.genres.data = venue.genres.split(",")
    return render_template('forms/edit_venue.html', form=Venue_form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  # return redirect(url_for('show_venue', venue_id=venue_id))
    form = VenueForm(request.form)
    try:
        venue = Venue.query.get(venue_id)
        venue.name = form['name'].data
        venue.city=form['city'].data
        venue.state=form['state'].data
        venue.address=form['address'].data
        venue.phone=form['phone'].data
        venue.genres=",".join(form['genres'].data)
        venue.facebook_link=form['facebook_link'].data
        venue.image_link=form['image_link'].data
        venue.seeking_talent=form['seeking_talent'].data
        venue.seeking_description=form['seeking_description'].data
        venue.web=form['website_link'].data
        db.session.add(venue)
        db.session.commit()
        flash("Venue " + form['name'].data + " edited successfully")
        
    except Exception:
        db.session.rollback()
        flash("Venue " + form['name'].data + " was not edited successfully.")
    finally:
        db.session.close()
    return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  artist = Artist()
  # on successful db insert, flash success
  form = ArtistForm(request.form, meta={'csrf': False})
  if form.validate_on_submit():
    try:
      artist.name = form['name'].data
      artist.state = form['state'].data
      artist.city = form['city'].data
      artist.phone = form['phone'].data
      artist.genres = ",".join(form['genres'].data)
      artist.image_link = form['image_link'].data
      artist.facebook_link = form['facebook_link'].data
      artist.web = form['website_link'].data
      artist.seeking_venue = form['seeking_venue'].data
      artist.seeking_description = form['seeking_description'].data
      db.session.add(artist)
      db.session.commit()
      flash("Artist " + form["name"].data + " was successfully listed!")
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
    except Exception:
      db.session.rollback()
      flash('An error occurred. Artist ' + form["name"].data + ' could not be listed.')
    finally:
      db.session.close()
  else:
    for field, message in form.errors.items():
      flash(field + ' - ' + str(message), 'danger')  
  return render_template('pages/home.html')

#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
    data_show = []
    shows = Show.query.all()
    for show in shows:
        data_show.append({
            "artist_id": show.artists.id,
            "artist_name": show.artists.name,
            "venue_id": show.venues.id,
            "venue_name": show.venues.name,
            "artist_image_link": show.artists.image_link,
            "start_time": format_datetime(str(show.start_time))
        })
    
    return render_template('pages/shows.html', shows=data_show)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  # on successful db insert, flash success
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
    Show_form = ShowForm()
    artist_id = Show_form.artist_id.data
    venue_id = Show_form.venue_id.data
    start_time = Show_form.start_time.data
    try:
        create_show = Show(start_time=start_time, artist_id=artist_id, venue_id=venue_id)
        db.session.add(create_show)
        db.session.commit()
        flash('Show was listed successfully')
    except Exception:
        db.session.rollback()
        flash('An error occurred. Show could not be listed.')
    finally:
        db.session.close()
    return render_template('pages/home.html')

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

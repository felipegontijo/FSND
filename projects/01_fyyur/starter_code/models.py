from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects import postgresql
from flask_migrate import Migrate

app = Flask(__name__)
db = SQLAlchemy()
migrate = Migrate(app, db, compare_type=True)

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

    pass
    

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
    
    pass

class Show(db.Model):
    __tablename__ = 'shows'

    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('artists.id'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('venues.id'), nullable=False)
    start_time = db.Column(db.DateTime(timezone=False), nullable=False)

    def __repr__(self):
        return f'<Show ID: {self.id}, artist ID: {self.artist_id}, venue ID: {self.venue_id}>'
    
    pass
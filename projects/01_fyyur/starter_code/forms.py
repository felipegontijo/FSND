from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SelectMultipleField, DateTimeField, BooleanField
from wtforms.validators import DataRequired, AnyOf, URL, length, NumberRange, Optional

genres_choices=[
    ('Alternative', 'Alternative'),
    ('Blues', 'Blues'),
    ('Classical', 'Classical'),
    ('Country', 'Country'),
    ('Electronic', 'Electronic'),
    ('Folk', 'Folk'),
    ('Funk', 'Funk'),
    ('Hip-Hop', 'Hip-Hop'),
    ('Heavy Metal', 'Heavy Metal'),
    ('Instrumental', 'Instrumental'),
    ('Jazz', 'Jazz'),
    ('Musical Theatre', 'Musical Theatre'),
    ('Pop', 'Pop'),
    ('Punk', 'Punk'),
    ('R&B', 'R&B'),
    ('Reggae', 'Reggae'),
    ('Rock n Roll', 'Rock n Roll'),
    ('Soul', 'Soul'),
    ('Other', 'Other'),
]

state_choices=[
    ('AL', 'AL'),
    ('AK', 'AK'),
    ('AZ', 'AZ'),
    ('AR', 'AR'),
    ('CA', 'CA'),
    ('CO', 'CO'),
    ('CT', 'CT'),
    ('DE', 'DE'),
    ('DC', 'DC'),
    ('FL', 'FL'),
    ('GA', 'GA'),
    ('HI', 'HI'),
    ('ID', 'ID'),
    ('IL', 'IL'),
    ('IN', 'IN'),
    ('IA', 'IA'),
    ('KS', 'KS'),
    ('KY', 'KY'),
    ('LA', 'LA'),
    ('ME', 'ME'),
    ('MT', 'MT'),
    ('NE', 'NE'),
    ('NV', 'NV'),
    ('NH', 'NH'),
    ('NJ', 'NJ'),
    ('NM', 'NM'),
    ('NY', 'NY'),
    ('NC', 'NC'),
    ('ND', 'ND'),
    ('OH', 'OH'),
    ('OK', 'OK'),
    ('OR', 'OR'),
    ('MD', 'MD'),
    ('MA', 'MA'),
    ('MI', 'MI'),
    ('MN', 'MN'),
    ('MS', 'MS'),
    ('MO', 'MO'),
    ('PA', 'PA'),
    ('RI', 'RI'),
    ('SC', 'SC'),
    ('SD', 'SD'),
    ('TN', 'TN'),
    ('TX', 'TX'),
    ('UT', 'UT'),
    ('VT', 'VT'),
    ('VA', 'VA'),
    ('WA', 'WA'),
    ('WV', 'WV'),
    ('WI', 'WI'),
    ('WY', 'WY'),
]

class ShowForm(FlaskForm):
    class Meta:
        csrf = False
    
    artist_id = StringField(
        'artist_id', validators=[DataRequired()]
    )
    venue_id = StringField(
        'venue_id', validators=[DataRequired()]
    )
    start_time = DateTimeField(
        'start_time',
        validators=[DataRequired()],
        default= datetime.today()
    )

class VenueForm(FlaskForm):
    class Meta:
        csrf = False
    
    name = StringField(
        'name', validators=[DataRequired()]
    )
    genres = SelectMultipleField(
        'genres', 
        validators=[DataRequired()],
        choices=genres_choices
    )
    address = StringField(
        'address', validators=[DataRequired(), length(max=120)]
    )
    city = StringField(
        'city', validators=[DataRequired(), length(max=120)]
    )
    state = SelectField(
        'state',
        validators=[DataRequired()],
        choices=state_choices
        
    )
    phone = StringField(
        'phone', validators=[DataRequired(), length(max=12)]
    )
    website = StringField(
        'website', validators=[Optional(), URL(), length(max=120)]
    )
    facebook_link = StringField(
        'facebook_link', validators=[Optional(), URL(), length(max=120)]
    )
    seeking_talent = BooleanField(
        'seeking_talent',
        validators=[Optional()],
        default= False
    )
    seeking_description = StringField(
        'seeking_description', validators=[Optional(), length(max=500)]
    )
    image_link = StringField(
        'image_link', validators=[URL(), length(max=500)]
    )
    
class ArtistForm(FlaskForm):
    class Meta:
        csrf = False
    
    name = StringField(
        'name', validators=[DataRequired()]
    )
    genres = SelectMultipleField(
        'genres', 
        validators=[DataRequired()],
        choices=genres_choices
    )
    city = StringField(
        'city', validators=[DataRequired(), length(max=120)]
    )
    state = SelectField(
        'state', validators=[DataRequired()],
        choices=state_choices
    )
    phone = StringField(
        'phone', validators=[DataRequired(), length(max=12)]
    )
    website = StringField(
        'website', validators=[Optional(), URL(), length(max=120)]
    )
    facebook_link = StringField(
        'facebook_link', validators=[Optional(), URL(), length(max=120)]
    )
    seeking_venue = BooleanField(
        'seeking_venue',
        validators=[Optional()],
        default= False
    )
    seeking_description = StringField(
        'seeking_description', validators=[Optional(), length(max=500)]
    )
    image_link = StringField(
        'image_link', validators=[URL(), length(max=500)]
    )

"""
This file defines the database models
"""

import datetime
from .common import db, Field, auth
from pydal.validators import *


def get_user_email():
    return auth.current_user.get('email') if auth.current_user else None

def get_time():
    return datetime.datetime.utcnow()

def get_user():
    return auth.current_user.get('id') if auth.current_user else None


### Define your table below
#
# db.define_table('thing', Field('name'))
#
## always commit your models to avoid problems later

db.define_table(
    'counties',
    Field('county_name'),
    Field('county_id')
)

db.define_table(
    'beaches',
    Field('beach_name'),
    Field('beach_id'),
    Field('beach_longitude'),
    Field('beach_latitude'),
    Field('county_reference_id', 'reference counties')
)

db.define_table(
    'reviews',
    Field('review'),
    Field('review_title'),
    Field('beach_id'),
    Field('user', default=get_user_email),
    Field('num_likes', type='integer', default=0),
    Field('image', type='text')
)

db.define_table(
    'likes',
    Field('review', 'reference reviews'),
    Field('liker', 'reference auth_user', default=get_user)
)

db.commit()

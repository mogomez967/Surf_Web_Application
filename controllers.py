"""
This file defines actions, i.e. functions the URLs are mapped into
The @action(path) decorator exposed the function at URL:

    http://127.0.0.1:8000/{app_name}/{path}

If app_name == '_default' then simply

    http://127.0.0.1:8000/{path}

If path == 'index' it can be omitted:

    http://127.0.0.1:8000/

The path follows the bottlepy syntax.

@action.uses('generic.html')  indicates that the action uses the generic.html template
@action.uses(session)         indicates that the action uses the session
@action.uses(db)              indicates that the action uses the db
@action.uses(T)               indicates that the action uses the i18n & pluralization
@action.uses(auth.user)       indicates that the action requires a logged in user
@action.uses(auth)            indicates that the action requires the auth object

session, db, T, auth, and tempates are examples of Fixtures.
Warning: Fixtures MUST be declared with @action.uses({fixtures}) else your app will result in undefined behavior
"""

from py4web import action, request, abort, redirect, URL
from yatl.helpers import A
from .common import db, session, T, cache, auth, logger, authenticated, unauthenticated, flash
from py4web.utils.url_signer import URLSigner
from .models import get_user_email, get_user
url_signer = URLSigner(session)




@action('index')
@action.uses(db, auth, 'index.html')
def index():
    return dict(
        # COMPLETE: return here any signed URLs you need.
        my_callback_url = URL('my_callback', signer=url_signer),
        load_counties_url = URL('load_counties', signer=url_signer),
        load_beaches_url = URL('load_beaches', signer=url_signer),
        load_reviews_url = URL('load_reviews', signer=url_signer),
        add_review_url = URL('add_review', signer=url_signer),
        get_likes_url = URL('get_likes', signer=url_signer),
        set_liked_url = URL('set_likes', signer=url_signer),
        get_user_url = URL('get_user', signer=url_signer),
        edit_contact_url = URL('edit_contact', signer=url_signer),
        search_url = URL('search', signer=url_signer),
        delete_review_url = URL('delete_review', signer=url_signer),
    )
    


@action('load_counties')
@action.uses(db, url_signer.verify())
def load_counties():
    counties = db(db.counties).select().as_list()
    return dict(counties=counties)

@action('load_beaches')
@action.uses(db, url_signer.verify())
def load_beaches():
    cid = request.params.get('id')
    county_beaches = db(db.beaches.county_reference_id == cid).select().as_list()
    return dict(county_beaches=county_beaches)

@action('load_reviews')
@action.uses(db, url_signer.verify())
def load_reviews():
    id = request.params.get('id')
    beach_reviews = db(db.reviews.beach_id == id).select().as_list()
    return dict(beach_reviews=beach_reviews)


@action('add_review', method="POST")
@action.uses(db, url_signer.verify(), auth)
def add_review():
    id = db.reviews.insert(
        review_title=request.json.get('review_title'),
        review=request.json.get('review'),
        beach_id=request.json.get('beach_id'),
        image=request.json.get('image')
    )

    user = get_user_email()

    return dict(id=id, user=user)


@action('set_likes', method="POST")
@action.uses(db, url_signer.verify(), auth.user)
def set_likes():
    review_id = int(request.json.get('review_id'))
    assert review_id is not None

    if db(db.likes).isempty():
        '''
        db.likes.update_or_insert(
            ((db.likes.review == review_id) & (db.likes.liker == get_user())),
            review=review_id,
            liker=get_user
        )'''

        db.likes.insert(review=review_id)

        row = db(db.reviews.id == review_id).select().first()
        new_num_likes = row.num_likes + 1

        db.reviews.update_or_insert(
            (db.reviews.id == review_id),
            num_likes=new_num_likes
        )

        return dict(liked=True, num_likes=new_num_likes)
    else:
        email = get_user_email()
        id = db(db.auth_user.email == email).select(db.auth_user.id).first()
        row = db((db.likes.review == review_id) & (db.likes.liker == id)).select().as_list()

        if row == []:
            print("in here")
            email = get_user_email()
            id = db(db.auth_user.email == email).select(db.auth_user.id).first()

            print("i here")
            db.likes.update_or_insert(
                ((db.likes.review == review_id) & (db.likes.liker == id)),
                review=review_id,
                liker=id
            )
            print("i hee")

            row = db(db.reviews.id == review_id).select().first()
            new_num_likes = row.num_likes + 1

            print(" hee")
            db.reviews.update_or_insert(
                (db.reviews.id == review_id),
                num_likes=new_num_likes
            )
            print(" he")

            return dict(liked=True, num_likes=new_num_likes)
        else:
            db((db.likes.review == review_id) & (db.likes.liker == id)).delete()

            row = db(db.reviews.id == review_id).select().first()
            new_num_likes = row.num_likes - 1

            db.reviews.update_or_insert(
                (db.reviews.id == review_id),
                num_likes=new_num_likes
            )

            return dict(liked=False, num_likes=new_num_likes)


@action('get_likes')
@action.uses(db, url_signer.verify(), auth)
def get_likes():
    review_id = int(request.params.get('review_id'))
    if db(db.likes).isempty():
        return dict(liked=False)
    else:
        email = get_user_email()
        id = db(db.auth_user.email == email).select(db.auth_user.id).first()
        # row = db((db.likes.review == review_id) & (db.likes.liker == get_user())).select().first()
        row = db((db.likes.review == review_id) & (db.likes.liker == id)).select().first()
        liked = True if row is not None else False
        return dict(liked=liked)


@action('get_user')
@action.uses(db, url_signer.verify())
def get_user():
    email = get_user_email()
    return dict(current_user=email)


@action('edit_contact', method="POST")
@action.uses(db, url_signer.verify(), auth.user)
def edit_contact():
    id = request.json.get('id')
    title = request.json.get('title')
    review = request.json.get('review')

    db(db.reviews.id == id).update(
        review_title=title,
        review=review
    )

@action('search')
@action.uses(db, url_signer.verify())
def search():
    # beach_list = db(db.beaches).select(db.beaches.beach_name)
    county_beaches = db(db.beaches).select().as_list()

    # search_list = []
    # for beach in beach_list:
    #     search_list.append(beach.beach_name)

    return dict(results=county_beaches)


@action('delete_review')
@action.uses(db, url_signer.verify())
def delete_review():
    id = request.params.get('id')
    assert id is not None
    db(db.reviews.id == id).delete()
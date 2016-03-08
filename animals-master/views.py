import os
import base64
import flask
from init import app, db
import models

@app.route('/')
def index():
    # rendering 'index.html' template with jinja variable 'animals'
    # assigned to Python object in 'animals'

    # make a cross-site request forgery preventing token
    if 'csrf_token' not in flask.session:
        flask.session['csrf_token'] = base64.b64encode(os.urandom(32)).decode('ascii')

    # make a response that we can add a cookie to
    # this is only for our little cookie example, it isn't needed if you are using
    # sessions.
    animals = models.Animal.query.all()
    resp = flask.make_response(flask.render_template('index.html', animals=animals,
                                                     csrf_token=flask.session['csrf_token']))
    return resp


# function that handles URLs of the form /animals/number/
@app.route('/animals/<int:aid>/')
def animal(aid):
    # try to get animal by ID
    animal = models.Animal.query.get(aid)
    if animal is None:
        # no animal, we're done
        flask.abort(404)
    else:
        return flask.render_template('animal.html', animal=animal)


@app.route('/a/<int:aid>')
def short_animal(aid):
    return flask.redirect(flask.url_for('animal', aid=aid), code=301)


@app.route('/search')
def search():
    query = flask.request.args['query']
    animal = models.Animal.query.filter_by(name=query).first()
    if animal is None:
        flask.abort(404)
    else:
        return flask.redirect(flask.url_for('animal', aid=animal.id))


@app.route('/add', methods=['POST'])
def add_animal():
    if 'auth_user' not in flask.session:
        app.logger.warn('unauthorized user tried to add animal')
        flask.abort(401)
    if flask.request.form['_csrf_token'] != flask.session['csrf_token']:
        app.logger.debug('invalid CSRF token in animal form')
        flask.abort(400)

    name = flask.request.form['name']
    home = flask.request.form['home']
    # create a new animal
    animal = models.Animal()
    # set its properties
    animal.name = name
    animal.location = home
    # add it to the database
    db.session.add(animal)
    # commit the database session
    db.session.commit()
    return flask.redirect(flask.url_for('animal', aid=animal.id), code=303)


@app.route('/login')
def login_form():
    # GET request to /login - send the login form
    return flask.render_template('login.html')

@app.route('/login', methods=['POST'])
def handle_login():
    # POST request to /login - check user
    user = flask.request.form['user']
    password = flask.request.form['password']
    if user == 'admin' and password == app.config['ADMIN_PASSWORD']:
        # User is good! Save in the session
        flask.session['auth_user'] = user
        # And redirect to '/', since this is a successful POST
        return flask.redirect(flask.request.form['url'], 303)
    else:
        # For an error in POST, we'll just re-show the form with an error message
        return flask.render_template('login.html', state='bad')

@app.route('/logout')
def handle_logout():
    # user wants to say goodbye, just forget about them
    del flask.session['auth_user']
    # redirect to specfied source URL, or / if none is present
    return flask.redirect(flask.request.args.get('url', '/'))

@app.errorhandler(404)
def not_found(err):
    return (flask.render_template('404.html', path=flask.request.path), 404)
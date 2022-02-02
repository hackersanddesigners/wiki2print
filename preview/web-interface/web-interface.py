import flask
import urllib, json
import os
from update import *
from api import *


# ---

PROJECT_NAME   = 'Wiki2Print'
PORTNUMBER     = 5522

WIKI           = 'https://wiki2print.hackersanddesigners.nl/wiki/mediawiki' # remove tail slash '/'
SUBJECT_NS     = { 'name': 'Publishing', 'id': 3000 }
STYLES_NS      = { 'name': 'PublishingCSS', 'id': 3001 }

# ---

# Create the application.
APP = flask.Flask(__name__)

@APP.route('/', methods=['GET'])
def index():
	data = get_index(WIKI, SUBJECT_NS)
	return flask.render_template(
    'index.html', 
    title     = PROJECT_NAME,
    wiki      = WIKI,
    allpages  = data,
    namespace = SUBJECT_NS['name']
  )

@APP.route('/update/', methods=['GET', 'POST'])
def update():
	data = create_index(WIKI, SUBJECT_NS)
	return flask.render_template(
    'index.html', 
    title     = PROJECT_NAME,
    wiki      = WIKI,
    allpages  = data,
    namespace = SUBJECT_NS['name']
  )

@APP.route('/inspect/<string:pagename>', methods=['GET', 'POST'])
def inspect(pagename):
	publication = get_publication(
		pagename, 
		SUBJECT_NS['name'],
		WIKI
	)
	return flask.render_template(
		'inspect.html', 
		publication = publication
	)

@APP.route('/pagedjs/<string:pagename>', methods=['GET', 'POST'])
def pagedjs(pagename):
	publication = get_publication(
		pagename, 
		SUBJECT_NS['name'],
		WIKI
	)
	return flask.render_template(
    'pagedjs.html', 
    publication = publication
  )

if __name__ == '__main__':
	APP.debug=True
	APP.run(port=f'{ PORTNUMBER }')

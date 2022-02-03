import flask
import urllib, json
import os
from update import *
from api import *

import sys
sys.path.insert(0, '..')
from config import config as conf

# CONFIG VARIABLES
PROJECT_NAME   = conf['project_name']
PORTNUMBER     = conf['port']
WIKI           = conf['wiki']['base_url']
SUBJECT_NS     = conf['wiki']['subject_ns']
STYLES_NS      = conf['wiki']['styles_ns']

APP = flask.Flask(__name__)

@APP.route('/', methods=['GET'])
def index():
	data = get_index(
		WIKI, 
		SUBJECT_NS
	)
	return flask.render_template(
    'index.html', 
    title     = PROJECT_NAME,
    wiki      = WIKI,
    namespace = SUBJECT_NS['name'],
    allpages  = data
  )

@APP.route('/inspect/<string:pagename>', methods=['GET', 'POST'])
def inspect(pagename):
	publication = get_publication(
		WIKI,
		SUBJECT_NS,
		STYLES_NS,
		pagename
	)
	return flask.render_template(
		'inspect.html', 
		publication = publication
	)

@APP.route('/pagedjs/<string:pagename>', methods=['GET', 'POST'])
def pagedjs(pagename):
	template = conf.get('custom_pagedjs_template')
	if template == None:
		template = 'pagedjs.html'
	
	publication = get_publication(
		WIKI,
		SUBJECT_NS,
		STYLES_NS,
		pagename
	)
	return flask.render_template(
    template, 
    publication = publication
  )

@APP.route('/update/<string:pagename>', methods=['GET', 'POST'])
def update(pagename):
	if pagename == 'index':
		create_index(
			WIKI,
			SUBJECT_NS
		)
	else:
		create_publication(
			WIKI,
			SUBJECT_NS,
			STYLES_NS,
			pagename 
		)
	return flask.redirect(flask.url_for('index'))

if __name__ == '__main__':
	APP.debug=True
	APP.run(port=f'{ PORTNUMBER }')

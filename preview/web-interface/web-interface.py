import flask
from flask import Response
from api import *

import sys
sys.path.insert(0, '..')
from config import config as conf


# We configure our constants

PROJECT_NAME   = conf['project_name']
PORTNUMBER     = conf['port']
WIKI           = conf['wiki']['base_url']
SUBJECT_NS     = conf['wiki']['subject_ns']
STYLES_NS      = conf['wiki']['styles_ns']


# We initiate the Flask app

APP = flask.Flask(__name__)


# Get the index of publications 

@APP.route('/', methods=['GET'])
def index():
	index = get_index(
		WIKI, 
		SUBJECT_NS
	)
	return flask.render_template(
		'index.html', 
		title      = PROJECT_NAME,
		wiki       = WIKI,
		subject_ns = SUBJECT_NS,
		styles_ns  = STYLES_NS,
		pages      = index['pages'],
		updated    = index['updated'],
	)


# Get a publication's HTML and CSS to inspect it closer

@APP.route('/html/<string:pagename>', methods=['GET', 'POST'])
def inspect(pagename):
	publication = get_publication(
		WIKI,
		SUBJECT_NS,
		STYLES_NS,
		pagename
	)
	return flask.render_template(
		'inspect.html', 
		title = pagename,
		html = publication['html'],
		css = publication['css']
	)


# Get a publication's CSS to inspect it closer

@APP.route('/css/<string:pagename>', methods=['GET', 'POST'])
def css(pagename):	
	css = get_css(
		WIKI, 
		STYLES_NS, 
		pagename
	)
	return Response(
		flask.render_template(
			"dynamic_css.css", 
			css = css
		), 
		mimetype='text/css'
	)


# Get a publication rendered as a PDF with PagedJS

@APP.route('/pdf/<string:pagename>', methods=['GET', 'POST'])
def pagedjs(pagename):	
	publication = get_publication(
		WIKI,
		SUBJECT_NS,
		STYLES_NS,
		pagename
	)
	template = customTemplate(pagename) or 'pagedjs.html'
	print( "using template: ", template)
	return flask.render_template(
		template, 
		title = pagename,
		html = publication['html'],
	)
 
 
# Recreate / update a publication's the HTML and CSS files

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

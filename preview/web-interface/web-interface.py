import flask
from api import *

import sys
sys.path.insert(0, '..')
from config import config as conf

# CONFIG VARIABLES
<<<<<<< HEAD
=======

>>>>>>> 64a2360 (trtied to integrate heerkos changes)
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
    title      = PROJECT_NAME,
    wiki       = WIKI,
    subject_ns = SUBJECT_NS,
    styles_ns  = STYLES_NS,
    allpages   = data,
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
		title = pagename,
		html = publication['html'],
		css = publication['css']
	)

@APP.route('/pagedjs/<string:pagename>', methods=['GET', 'POST'])
def pagedjs(pagename):
	template = conf.get('custom_pagedjs_template') or 'pagedjs.html'
	
	publication = get_publication(
		WIKI,
		SUBJECT_NS,
		STYLES_NS,
		pagename
	)
	return flask.render_template(
    template, 
		title = pagename,
		html = publication['html'],
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

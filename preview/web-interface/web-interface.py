import flask
from flask import Response
from api import *
from flask import request

import sys
sys.path.insert(0, '..')
from config import config as conf
from flask_plugin import PluginManager


# We configure our constants

PROJECT_NAME = conf['project_name']
PORTNUMBER   = conf['port']
WIKI         = conf['wiki']['base_url']
SUBJECT_NS   = conf['wiki']['subject_ns']
STYLES_NS    = conf['wiki']['styles_ns']
SCRIPTS_NS   = conf['wiki']['scripts_ns']


# We initiate the Flask app

APP = flask.Flask(__name__)
manager = PluginManager(APP)

for plugin in manager.plugins:
	manager.load(plugin)
	manager.start(plugin)
	print(plugin)

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
		scripts_ns = SCRIPTS_NS,
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
		SCRIPTS_NS,
		pagename,
	)
	return flask.render_template(
		'html.html',
		title = pagename,
		html  = publication['html'],
		css   = publication['css'],
		js    = publication['js']
	)


# Get a publication's CSS to inspect it closer

@APP.route('/css/<string:pagename>.css', methods=['GET', 'POST'])
def css(pagename):
	css = create_css(
		WIKI,
		STYLES_NS,
		pagename
	)
	# print(pagename)
	# print(css)
	return Response(
		flask.render_template(
			"css.css",
			css = css
		),
		mimetype='text/css'
	)

# Get a publication's CSS to inspect it closer

@APP.route('/js/<string:pagename>.js', methods=['GET', 'POST'])
def js(pagename):
	js = create_js(
		WIKI,
		SCRIPTS_NS,
		pagename
	)
	# print(pagename)
	# print(css)
	return Response(
		flask.render_template(
			"js.js",
			js = js
		),
		mimetype='text/javascript'
	)


# Get a publication rendered as a PDF with PagedJS

@APP.route('/pdf/<string:pagename>', methods=['GET', 'POST'])
def pagedjs(pagename):
	publication = get_publication(
		WIKI,
		SUBJECT_NS,
		STYLES_NS,
		SCRIPTS_NS,
		pagename,
	)
	if( publication_has_plugin( pagename ) ):
		return flask.redirect(flask.url_for('plugins.'+pagename+'.pagedjs',pagename = pagename))
	template = customTemplate(pagename) or 'pdf.html'
	print( "using template: ", template)
	return flask.render_template(
		template,
		title = pagename,
		html  = publication['html'],
	)


# Recreate / update a publication's HTML and CSS files

@APP.route('/update/<string:pagename>', methods=['GET', 'POST'])
def update(pagename):
	full_update = request.form.get('full_update')
	parsoid = request.form.get('parsoid')
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
			SCRIPTS_NS,
			pagename,
			full_update,
			parsoid
		)
	return flask.redirect(flask.url_for('index'))


def has_no_empty_params(rule):
	defaults = rule.defaults if rule.defaults is not None else ()
	arguments = rule.arguments if rule.arguments is not None else ()
	return len(defaults) >= len(arguments)

def publication_has_plugin(pubname):
	for plugin in manager.plugins:
		if( plugin.name == pubname ):
			print("Found plugin for publication " + pubname )
			return True
	return False

if __name__ == '__main__':
	APP.debug=True
	APP.run(port=PORTNUMBER)

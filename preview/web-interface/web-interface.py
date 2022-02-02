import flask
import urllib, json
import os
from update import *
from api import *


# ---

PROJECT_NAME   = 'Wiki2Print'
PORTNUMBER     = 5522

DIR_PATH       = '.' # without trailing slash
WIKI           = 'https://wiki2print.hackersanddesigners.nl/wiki/mediawiki' # remove tail slash '/'
SUBJECT_NS     = { 'name': 'Publishing', 'id': 3000 }
STYLES_NS      = { 'name': 'PublishingCSS', 'id': 3001 }

PAGENAME       = 'Making_Matters_Lexicon'

SUBJECT_PAGE   = SUBJECT_NS['name'] + ':' + PAGENAME
SUBJECT_PAGE   = STYLES_NS['name']  + ':' + PAGENAME

# STYLESHEET_PAD = 'test-project.css'
# STYLESHEET     = 'print.css'

PROJ_HTML_PATH = f'{ DIR_PATH }/static/{ PAGENAME }.html'

# ---

# Create the application.
APP = flask.Flask(__name__)

@APP.route('/', methods=['GET'])
def index():
	data = get_index(WIKI, SUBJECT_NS)
	return flask.render_template(
    'index.html', 
    title = PROJECT_NAME,
		wiki  = WIKI,
		allpages = data,
		namespace = SUBJECT_NS['name']
  )

@APP.route('/update/', methods=['GET', 'POST'])
def update():
	data = create_index(WIKI, SUBJECT_NS)
	return flask.render_template(
    'index.html', 
    title = PROJECT_NAME,
		wiki  = WIKI,
		allpages = data,
		namespace = SUBJECT_NS['name']
  )

def dlCSS():
	# download the stylesheet pad
	# using etherpump
	os.system(f'{ DIR_PATH }/venv/bin/etherpump gettext { STYLESHEET_PAD } > { DIR_PATH }/static/css/{ STYLESHEET }')


# @APP.route('/', methods=['GET'])
# def pad():
# 	if not os.path.exists(PROJ_HTML_PATH):
# 		dlCSS() 
# 		pulication = update_material_now(
# 			PAGENAME, 
# 			WIKI
# 		) 
#     # download the latest version of the page
# 		with open(PROJ_HTML_PATH, 'w') as out:
# 			out.write(pulication) # save the html (without <head>) to file
# 	else:
# 		pulication = open(PROJ_HTML_PATH, 'r').read()
# 	return flask.render_template(
#     'index.html', 
#     title = PROJECT_NAME,
# 		wiki  = WIKI,
#     page  = PAGENAME
#   )


@APP.route('/notes/', methods=['GET'])
def notes():
  return flask.render_template('notes.html')


# @APP.route('/update/', methods=['GET', 'POST'])
# def update():
# 	publication = update_material_now(
#     PAGENAME, 
#     WIKI
#   ) 
#   # download the latest version of the page
# 	save(
#     publication, 
#     PROJECT_NAME
#   ) 
#   # save the html to file (without <head>) to file
# 	return flask.render_template(
#     'index.html', 
#     title = PROJECT_NAME,
# 		wiki  = WIKI,
#     page  = PAGENAME
#   )


@APP.route('/pagedjs/', methods=['GET', 'POST'])
def pagedjs():
	dlCSS() # download the stylesheet pad
	publication = open(PROJ_HTML_PATH, 'r').read()
	return flask.render_template(
    'pagedjs.html', 
    publication = publication
  )


@APP.route('/inspect/', methods=['GET', 'POST'])
def inspect():
	dlCSS() # download the stylesheet pad
	publication = open(PROJ_HTML_PATH, 'r').read()
	return flask.render_template(
    'inspect.html', 
    publication = publication
  )

@APP.route('/stylesheet/', methods=['GET'])
def stylesheet():
	return flask.render_template('stylesheet.html')

if __name__ == '__main__':
	APP.debug=True
	APP.run(port=f'{ PORTNUMBER }')

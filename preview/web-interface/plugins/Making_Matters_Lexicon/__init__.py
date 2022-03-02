import flask
from flask_plugin import Plugin
from flask import redirect, url_for
from api import *
# this madness is apparently necessary to import web-interface.py
import os,sys,inspect
current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir) 
import importlib  
app = importlib.import_module("web-interface")

plugin = Plugin(
		static_folder='static',
		template_folder='template'
)
  
@plugin.route('/pdf/<string:pagename>', methods=['GET', 'POST'])
def pagedjs(pagename):	
	publication = get_publication(
		app.WIKI,
		app.SUBJECT_NS,
		app.STYLES_NS,
		pagename,
		app.manager
	)
	return flask.render_template(
		'Making_Matters_Lexicon.html', 
		title = pagename,
		html  = publication['html'],
	)
	
def filter(html):
	print("filtering...")
	return html
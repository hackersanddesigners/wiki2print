import datetime
import json
import os
import re
import sys
import urllib.error
import urllib.request
from pprint import pprint

import jinja2
from bs4 import BeautifulSoup

STATIC_FOLDER_PATH = './static'        # without trailing slash
STATIC_IMAGE_FOLDER_PATH = os.path.join( STATIC_FOLDER_PATH, 'images' ) # where to save images
PUBLIC_IMAGE_FOLDER_PATH = os.path.join( '/static', 'images' ) # what to change <img /> src attribute to
STATIC_PUBLICATION_FOLDER_PATH = os.path.join( STATIC_FOLDER_PATH, 'publications' )

# check if 'images/' already exists
if not os.path.exists( STATIC_IMAGE_FOLDER_PATH ):
	os.makedirs( STATIC_IMAGE_FOLDER_PATH )

# make publications folder
if not os.path.exists( STATIC_PUBLICATION_FOLDER_PATH ):
	os.makedirs( STATIC_PUBLICATION_FOLDER_PATH )

TEMPLATES_DIR = None

# This uses a low quality copy of all the images
# (using a folder with the name "images-small",
# which stores a copy of all the images generated with:
# $ mogrify -quality 5% -adaptive-resize 25% -remap pattern:gray50 * )

fast = False


# gets or creates index of publications in namespace

def get_index(wiki, subject_ns):
	"""
		wiki = string
		subject_ns = object
	"""
	return load_file('index', 'json') or create_index(
		wiki,
		subject_ns
	)


# gets publication's HTML and CSS

def get_publication(wiki, subject_ns, styles_ns, scripts_ns, pagename):
	"""
		wiki = string
		subject_ns = object
		styles_ns = object
		pagename = string
	"""
	return {
		'html': get_html(wiki, subject_ns, pagename),
		'css': get_css(wiki, styles_ns, pagename),
		'js': get_js(wiki, scripts_ns, pagename)
	}


# gets or creates HTML file for a publication

def get_html(wiki, subject_ns, pagename):
	"""
		wiki = string
		subject_ns = object
		pagename = string
	"""
	return load_file(pagename, 'html') or create_html(
		wiki,
		subject_ns,
		pagename,
		False,
		False
	)


# gets or creates CSS file for a publication

def get_css(wiki, styles_ns, pagename):
	"""
		wiki = string
		styles_ns = object
		pagename = string
	"""
	return load_file(pagename, 'css') or create_css(
		wiki,
		styles_ns,
		pagename
	)


# gets or creates JS file for a publication

def get_js(wiki, scripts_ns, pagename):
	"""
		wiki = string
		scripts_ns = object
		pagename = string
	"""
	return load_file(pagename, 'js') or create_js(
		wiki,
		scripts_ns,
		pagename
	)

# makes API call to create/update index of publications

def create_index(wiki, subject_ns):
	"""
		wiki = string
		subject_ns = object
	"""
	url = f'{ wiki }/api.php?action=query&format=json&list=allpages&aplimit=100&apnamespace={ subject_ns["id"] }'
	data = do_API_request(url)
	pages = data['query']['allpages']
	# exclude subpages
	pages = [page for page in pages if '/' not in page['title']]
	for page in pages:
		# removing the namespace from title
		page['title'] = page['title'].replace(subject_ns['name'] + ':', '')
		page['slug'] = page['title'].replace(' ', '_')  # slugifying title
		pageJSON = load_file(page['slug'], 'json')
		page['updated'] = pageJSON and pageJSON['updated'] or '--'
	now = str(datetime.datetime.now())
	index = {
		'pages': pages,
		'updated': now
	}
	save_file('index', 'json', index)
	return index


# Creates/updates a publication object

def create_publication(wiki, subject_ns, styles_ns, scripts_ns, pagename, full_update, parsoid):
	"""
		wiki = string
		subject_ns = object
		styles_ns = object
		scripts_ns = object
		pagename = string
		full_update = None or string. Full update when not None
		parsoid = Use parsoid parser for html sections
	"""
	return {
		'html': create_html(wiki, subject_ns, pagename, full_update, parsoid),
		'css': create_css(wiki, styles_ns, pagename),
		'js': create_js(wiki, scripts_ns, pagename)
	}


# makes API call to create/update a publication's HTML

def create_html(wiki, subject_ns, pagename, full_update, parsoid):
	"""
		wiki = string
		subject_ns = object
		pagename = string
		full_update = None or string. Full update when not None
		parsoid = Use parsoid parser for html sections
	"""
	url = f'{ wiki }/api.php?action=parse&page={ subject_ns["name"] }:{ pagename }&pst=True&format=json&disableeditsection'
	# or maybe https://wiki2print.hackersanddesigners.nl/wiki/mediawiki/rest.php/v1/page/Publishing:TheNewSocial/html?body=1
	data = do_API_request(url, subject_ns["name"]+":"+pagename, wiki)
	# pprint(data)
	now = str(datetime.datetime.now())
	data['updated'] = now

	save_file(pagename, 'json', data)

	update_publication_date(   # we add the last updated of the publication to our index
		wiki,
		subject_ns,
		pagename,
		now
	)

	if 'parse' in data:
		html = data['parse']['text']['*']
		imgs = data['parse']['images']

		html = remove_comments(html)
		html = download_media(html, imgs, wiki, full_update)
		html = clean_up(html)
		# html = add_item_inventory_links(html)

		if fast == True:
			html = fast_loader(html)

		soup = BeautifulSoup(html, 'html.parser')
		# soup = remove_edit(soup)
		soup = inlineCiteRefs(soup)
		html = str(soup)
		# html = inlineCiteRefs(html)
		# html = add_author_names_toc(html)

		if ( parsoid ):
			print( 'DOING A PARSOID PARSE' )

			# get TOC from previous parser soup output since Parsoid doesnt make one
			toc = get_toc(soup)

			# get html output of parsoid
			html_url = f'{ wiki }/rest.php/v1/page/{ subject_ns["name"] }:{ pagename }/html'
			html_data = do_API_request(html_url, subject_ns["name"]+":"+pagename, wiki)
			html = html_data.decode('utf-8')

			# make new soup
			soup = BeautifulSoup(html)
			soup = parsoid_output_cleanup(soup)
			soup.insert(0, toc)

			html = str(soup)

			# repeat above steps

			html = remove_comments(html)
			html = download_media(html, imgs, wiki, full_update)
			html = clean_up(html)
			# html = add_item_inventory_links(html)

			if fast == True:
				html = fast_loader(html)

			soup = BeautifulSoup(html, 'html.parser')
			# soup = remove_edit(soup)
			# soup = inlineCiteRefs(soup)
			html = str(soup)

		# print(html)

	else:
		html = None

	save_file(pagename, 'html', html)

	return html


# makes API call to create/update a publication's CSS

def create_css(wiki, styles_ns, pagename):
	"""
		wiki = string
		styles_ns = object
		pagename = string
	"""
	css_url = f'{ wiki }/api.php?action=parse&page={ styles_ns["name"] }:{ pagename }&prop=wikitext&pst=True&format=json'
	css_data = do_API_request(css_url)
	if css_data and 'parse' in css_data:
		css = css_data['parse']['wikitext']['*']
		save_file(pagename, 'css', css)
		return css


# makes API call to create/update a publication's JS

def create_js(wiki, scripts_ns, pagename):
	"""
		wiki = string
		scripts_ns = object
		pagename = string
	"""
	js_url = f'{ wiki }/api.php?action=parse&page={ scripts_ns["name"] }:{ pagename }&prop=wikitext&pst=True&format=json'
	js_data = do_API_request(js_url)
	if js_data and 'parse' in js_data:
		js = js_data['parse']['wikitext']['*']
		save_file(pagename, 'js', js)
		return js


# Load file from disk

def load_file(pagename, ext):
	"""
		pagename = string
		ext = string
	"""
	path = os.path.join( STATIC_PUBLICATION_FOLDER_PATH, f'{ pagename }.{ ext }' )
	if os.path.exists(path):
		print(f'Loading { ext }:', path)
		with open(path, 'r') as out:
			if ext == 'json':
				data = json.load(out)
			else:
				data = out.read()
			out.close()
		return data


# Save file to disk

def save_file(pagename, ext, data):
	"""
		pagename = string
		ext = string
		data = object
	"""
	path = os.path.join( STATIC_PUBLICATION_FOLDER_PATH,  f'{ pagename }.{ ext }' )
	print(f'Saving { ext }:', path)
	try:
		out = open(path, 'w')
	except OSError:
			print("Could not open/write file:", path)
			sys.exit()

	with out: #open(path, 'w') as out:
		if ext == 'json':
			out.write( json.dumps(data, indent = 2) )
		else:
			out.write( data )
		out.close()
	return data


# do API request and return JSON

def do_API_request(url, filename="", wiki=""):
	"""
		url = API request url (string)
		data =  { 'query':
					'pages' :
						pageid : {
							'links' : {
								'?' : '?'
								'title' : 'pagename'
							}
						}
					}
				}
	"""
	purge(filename, wiki)
	print('Loading from wiki: ', url)
	response = urllib.request.urlopen(url)
	response_type = response.getheader('Content-Type')

	if response.status == 200:
		contents = response.read()
		if "json" in response_type:
			return json.loads(contents)
		else:
			return contents

# api calls seem to be cached even when called with maxage
# So call purge before doing the api call.
# https://www.mediawiki.org/wiki/API:Purge
def purge(filename, wiki):
	if(filename=="" or wiki==""): return
	print("purge " + filename )

	import requests
	S = requests.Session()
	URL = f'{ wiki }/api.php'
	# url = f'{ wiki }/api.php?action=query&list=allimages&aifrom={ filename }&format=json'
	PARAMS = {
			"action": "purge",
			"titles": filename,
			"format": "json",
			"generator": "alltransclusions",
	}
	R = S.post(url=URL, params=PARAMS)
	# DATA = R.text

# updates a publication's last updated feild in the index

def update_publication_date(wiki, subject_ns, pagename, updated):
	"""
		wiki = string
		subject_ns = object
		pagename = string
		updated = string
	"""
	index = get_index(wiki, subject_ns)
	for page in index['pages']:
		if page['slug'] == pagename:
			page['updated'] = updated
	save_file('index', 'json', index)

def customTemplate(name):
	path = "custom/%s.html" % name
	if os.path.isfile(os.path.join(os.path.dirname(__file__), "templates/", path)):
		return path
	else:
		return None




# Beautiful soup seems to have a problem with some comments,
# so lets remove them before parsing.

def remove_comments( html ):
	"""
		html = string (HTML)
	"""
	pattern = r'(<!--.*?-->)|(<!--[\S\s]+?-->)|(<!--[\S\s]*?$)'
	return re.sub(pattern, "", html)


# Downloading images referenced in the html

def download_media(html, images, wiki, full_update):
	"""
		html = string (HTML)
		images = list of filenames (str)
	"""

	# download media files
	for filename in images:
		filename = filename.replace(' ', '_') # safe filenames
		# check if the image is already downloaded
		# if not, then download the file
		if (not os.path.isfile( os.path.join( STATIC_IMAGE_FOLDER_PATH, filename ) ) ) or full_update:
			# first we search for the full filename of the image
			url = f'{ wiki }/api.php?action=query&list=allimages&aifrom={ filename }&format=json'
			# url = f'{ wiki }/api.php?action=query&titles=File:{ filename }&format=json'
			data = do_API_request(url)
			# timestamp = data.query.pages.

			# print(json.dumps(data, indent=2))

			if data and data['query']['allimages']:

			# we select the first search result
			# (assuming that this is the image we are looking for)
				image = data['query']['allimages'][0]

				if image:
					# then we download the image
					image_url = image['url']
					image_filename = image['name']

					if image_filename == filename:
						print('Downloading:', image_filename)
						image_response = urllib.request.urlopen(image_url).read()

						# and we save it as a file
						image_path = os.path.join( STATIC_IMAGE_FOLDER_PATH, image_filename )
						out = open(image_path, 'wb')
						out.write(image_response)
						out.close()
						print(image_path)

						import time
						time.sleep(3) # do not overload the server

					else:
						print('Not Downloading:', image_filename)


		# replace src links
		e_filename = re.escape( filename )  # needed for filename with certain characters
		image_path = f'{ PUBLIC_IMAGE_FOLDER_PATH }/{ filename }' # here the images need to link to the / of the domain, for flask :/// confusing! this breaks the whole idea to still be able to make a local copy of the file
		matches = re.findall(rf'src=\"/wiki/mediawiki/images/.*?px-{ e_filename }\"', html) # for debugging
		# pprint(matches)
		if matches:
			html = re.sub(rf'src=\"/wiki/mediawiki/images/.*?px-{ e_filename }\"', f'src=\"{ image_path }\"', html)
		else:
			matches = re.findall(rf'src=\"/wiki/mediawiki/images/.*?{ e_filename }\"', html) # for debugging
			# print(matches, e_filename, html)
			html = re.sub(rf'src=\"/wiki/mediawiki/images/.*?{ e_filename }\"', f'src=\"{ image_path }\"', html)
		print(f'Debug: {filename}: {matches}\n------') # for debugging: each image should have the correct match!

	return html




# def add_item_inventory_links(html):
# 	"""
# 		html = string (HTML)
# 	"""
# 	# Find all references in the text to the item index
# 	pattern = r'Item \d\d\d'
# 	matches = re.findall(pattern, html)
# 	index = {}
# 	new_html = ''
# 	from nltk.tokenize import sent_tokenize
# 	for line in sent_tokenize(html):
# 		for match in matches:
# 			if match in line:
# 				number = match.replace('Item ', '').strip()
# 				if not number in index:
# 					index[number] = []
# 					count = 1
# 				else:
# 					count = index[number][-1] + 1
# 				index[number].append(count)
# 				item_id = f'ii-{ number }-{ index[number][-1] }'
# 				line = line.replace(match, f'Item <a id="{ item_id }" href="#Item_Index">{ number }</a>')

# 		# the line is pushed back to the new_html
# 		new_html += line + ' '

# 	# Also add a <span> around the index nr to style it
# 	matches = re.findall(r'<li>\d\d\d', new_html)
# 	for match in matches:
# 		new_html = new_html.replace(match, f'<li><span class="item_nr">{ match }</span>')

# 	# import json
# 	# print(json.dumps(index, indent=4))

# 	return new_html


def clean_up(html):
	"""
		html = string (HTML)
	"""
	# html = re.sub(r'\[.*edit.*\]', '', html) # remove the [edit] # Heerko: this somehow caused problems. Removing it solves it, seeming without side effects...
	html = re.sub(r'href="/index.php\?title=', 'href="#', html) # remove the internal wiki links
	html = re.sub(r'&#91;(?=\d)', '', html) # remove left footnote bracket [
	html = re.sub(r'(?<=\d)&#93;', '', html) # remove right footnote bracket ]
	html = re.sub(r"srcset=", "loading=\"lazy\" xsrcset=", html) # lazy loading
	return html

def remove_edit(soup):
	"""
		soup = BeautifSoup (HTML)
	"""
	es = soup.find_all(class_="mw-editsection")
	for s in es:
		s.decompose()
	return soup


# inline citation references in the html for pagedjs
# Turns: <sup class="reference" id="cite_ref-1"><a href="#cite_note-1">[1]</a></sup>
# into: <span class="footnote">The cite text</span>

def inlineCiteRefs(soup):
	"""
		soup = BeautifSoup (HTML)
	"""
	refs = soup.find_all("sup", class_="reference")
	for ref in refs:
		href = ref.a['href']
		res = re.findall('[0-9]+', href)
		if(res):
			cite = soup.find_all(id="cite_note-"+res[0])
			text = cite[0].find(class_="reference-text")
			text['class'] = 'footnote'
			ref.replace_with(text)
	# remove the  reference from the bottom of the document
	for item in soup.find_all(class_="references"):
		item.decompose()
	return soup


def get_toc(soup):
	"""
		get TOC from soup
	"""
	return soup.find( id="toc" )


def parsoid_output_cleanup(soup):
	body = soup.find('body')
	body.name = 'div'
	sections = soup.find_all( 'section' )
	for section in sections:
		first_child = section.find([ 'h1', 'h2', 'h3', 'h4', 'h5', 'h6' ], recursive=False )
		if first_child and first_child ['id']:
			section['id'] = first_child['id']
			first_child['id'] = first_child['id'] + '_header'
	return body


def fast_loader(html):
	"""
		html = string (HTML)
	"""
	html = html.replace('/images/', '/images-small/')
	print('--- rendered in FAST mode ---')

	return html



# ---

# if __name__ == "__main__":

	# wiki = 'https://volumetricregimes.xyz' # remove tail slash '/'
	# pagename = 'Unfolded'

	# publication_unfolded = update_material_now(pagename, wiki) # download the latest version of the page
	# save(publication_unfolded, pagename) # save the page to file

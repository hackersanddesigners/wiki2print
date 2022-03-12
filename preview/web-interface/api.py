import urllib.request
import urllib.error
import os
import re
import json
import jinja2
import datetime
from bs4 import BeautifulSoup

STATIC_FOLDER_PATH = './static'        # without trailing slash
PUBLIC_STATIC_FOLDER_PATH = '/static'  # without trailing slash
TEMPLATES_DIR = None


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

def get_publication(wiki, subject_ns, styles_ns, pagename):
	"""
		wiki = string
		subject_ns = object
		styles_ns = object
		pagename = string
	"""
	return {
		'html' : get_html( wiki, subject_ns, pagename ),
		'css' : get_css( wiki, styles_ns, pagename )
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


# makes API call to create/update index of publications 

def create_index(wiki, subject_ns):
	"""
		wiki = string
		subject_ns = object
	"""
	url  = f'{ wiki }/api.php?action=query&format=json&list=allpages&apnamespace={ subject_ns["id"] }'
	data = do_API_request(url)
	pages = data['query']['allpages']
	pages = [ page for page in pages if '/' not in page['title'] ]
	for page in pages:
		page['title'] = page['title'].replace(subject_ns['name'] + ':' , '')
		page['slug'] = page['title'].replace(' ' , '_')
		pageJSON = load_file(page['slug'], 'json')
		page['updated'] = pageJSON and pageJSON['updated'] or '--'
	updated =  str(datetime.datetime.now())
	index = {
		'pages': pages,
		'updated': updated
	}
	save_file('index', 'json', index)
	return index


# Creates/updates a publication object

def create_publication(wiki, subject_ns, styles_ns, pagename, magager):
	"""
		wiki = string
		subject_ns = object
		styles_ns = object
		pagename = string
	"""
	return {
		'html' : create_html( wiki, subject_ns, pagename, magager ),
		'css' : create_css( wiki, styles_ns, pagename )
	}


# makes API call to create/update a publication's HTML 

def create_html(wiki, subject_ns, pagename):
	"""
		wiki = string
		subject_ns = object
		pagename = string
	"""
	url = f'{ wiki }/api.php?action=parse&page={ subject_ns["name"] }:{ pagename }&pst=True&format=json'
	data = do_API_request(url)
	now = str(datetime.datetime.now())
	data['updated'] = now
	save_file(pagename, 'json', data)
	
	update_publication_date(
		wiki,
		subject_ns, 
		pagename, 
		now
	)

	# print(json.dumps(data['parse']['sections'], indent=4))
	if 'parse' in data:
		html = data['parse']['text']['*']
		imgs = data['parse']['images']
		html = remove_comments(html)
		html = download_media(html, imgs, wiki)
		html = clean_up(html)
		html = add_item_inventory_links(html)
		html = fast_loader(html)

		soup = BeautifulSoup(html, 'html.parser')
		soup = remove_edit(soup)
		soup = inlineCiteRefs(soup)
		html = soup.prettify()
		# html = inlineCiteRefs(html)
		# html = add_author_names_toc(html)

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
	print(css_data)
	if css_data and 'parse' in css_data:
		print(json.dumps(css_data, indent=4))
		css = css_data['parse']['wikitext']['*']
		save_file(pagename, 'css', css)
		return css


# Load file from disk

def load_file(pagename, ext):
	"""
		pagename = string
		ext = string
	"""
	path = f'{ STATIC_FOLDER_PATH }/{ pagename }.{ ext }'
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
	path = f'{ STATIC_FOLDER_PATH }/{ pagename }.{ ext }'
	print(f'Saving { ext }:', path)
	with open(path, 'w') as out:
		if ext == 'json':
			out.write( json.dumps(data, indent = 2) )
		else:
			out.write(data)
		out.close()
	return data


# do API request and return JSON

def do_API_request(url):
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
	print('Loading from wiki: ', url)
	response = urllib.request.urlopen(url)
	response_type = response.getheader('Content-Type')
	# print(response_type, response.status)
	if response.status == 200 and "json" in response_type:
		contents = response.read()
		data = json.loads(contents)
		return data


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



# This uses a low quality copy of all the images 
# (using a folder with the name "images-small",
# which stores a copy of all the images generated with:
# $ mogrify -quality 5% -adaptive-resize 25% -remap pattern:gray50 * )
fast = False

def download_media(html, images, wiki):
	"""
		html = string (HTML)
		images = list of filenames (str)
	"""
	# check if 'images/' already exists
	if not os.path.exists(f'{ STATIC_FOLDER_PATH }/images'):
		os.makedirs(f'{ STATIC_FOLDER_PATH }/images')
	
	# download media files
	for filename in images:
		filename = filename.replace(' ', '_') # safe filenames
		
		# check if the image is already downloaded
		# if not, then download the file
		if not os.path.isfile(f'{ STATIC_FOLDER_PATH }/images/{ filename }'):

			# first we search for the full filename of the image
			url = f'{ wiki }/api.php?action=query&list=allimages&aifrom={ filename }&format=json'
			data = do_API_request(url)

			if data and data['query']['allimages']:

			# we select the first search result
			# (assuming that this is the image we are looking for)
				image = data['query']['allimages'][0] 

				if image:
					# then we download the image
					image_url = image['url']
					image_filename = image['name']
					print('Downloading:', image_filename)
					image_response = urllib.request.urlopen(image_url).read()

					# and we save it as a file
					image_path = f'{ STATIC_FOLDER_PATH }/images/{ image_filename }'
					out = open(image_path, 'wb') 
					out.write(image_response)
					out.close()
					print(image_path)

					import time
					time.sleep(3) # do not overload the server

		# replace src link
		e_filename = re.escape( filename )  # needed for filename with certain characters
		# e_filename = filename
		image_path = f'{ PUBLIC_STATIC_FOLDER_PATH }/images/{ filename }' # here the images need to link to the / of the domain, for flask :/// confusing! this breaks the whole idea to still be able to make a local copy of the file
		matches = re.findall(rf'src=\"/wiki/mediawiki/images/.*?px-{ e_filename }\"', html) # for debugging
		if matches:
			html = re.sub(rf'src=\"/wiki/mediawiki/images/.*?px-{ e_filename }\"', f'src=\"{ image_path }\"', html)
		else:
			matches = re.findall(rf'src=\"/wiki/mediawiki/images/.*?{ e_filename }\"', html) # for debugging
			# print(matches, e_filename, html)
			html = re.sub(rf'src=\"/wiki/mediawiki/images/.*?{ e_filename }\"', f'src=\"{ image_path }\"', html) 
		# print(f'{filename}: {matches}\n------') # for debugging: each image should have the correct match!

	return html

def add_item_inventory_links(html):
	"""
		html = string (HTML)
	"""
	# Find all references in the text to the item index
	pattern = r'Item \d\d\d'
	matches = re.findall(pattern, html)
	index = {}
	new_html = ''
	from nltk.tokenize import sent_tokenize
	for line in sent_tokenize(html):
		for match in matches:
			if match in line:
				number = match.replace('Item ', '').strip()
				if not number in index:
					index[number] = []
					count = 1
				else:
					count = index[number][-1] + 1
				index[number].append(count)
				item_id = f'ii-{ number }-{ index[number][-1] }'
				line = line.replace(match, f'Item <a id="{ item_id }" href="#Item_Index">{ number }</a>')

		# the line is pushed back to the new_html
		new_html += line + ' '
		
	# Also add a <span> around the index nr to style it
	matches = re.findall(r'<li>\d\d\d', new_html)
	for match in matches:
		new_html = new_html.replace(match, f'<li><span class="item_nr">{ match }</span>')

	# import json
	# print(json.dumps(index, indent=4))
	
	return new_html

def clean_up(html):
	"""
		html = string (HTML)
	"""
	# html = re.sub(r'\[.*edit.*\]', '', html) # remove the [edit] # Heerko: this somehow caused problems. Removing it solves it, seeming without side effects...
	html = re.sub(r'href="/index.php\?title=', 'href="#', html) # remove the internal wiki links
	html = re.sub(r'&#91;(?=\d)', '', html) # remove left footnote bracket [
	html = re.sub(r'(?<=\d)&#93;', '', html) # remove right footnote bracket ]
	return html

# Beautiful soup seems to have a problem with some comments, 
# so lets remove them before parsing.
def remove_comments( html ):
	"""
		html = string (HTML)
	"""
	pattern = r'(<!--.*?-->)|(<!--[\S\s]+?-->)|(<!--[\S\s]*?$)'
	return re.sub(pattern, "", html)

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
	#remove the  reference from the bottom of the document
	for item in soup.find_all(class_="references"):
		item.decompose()
	return soup


def fast_loader(html):
	"""
		html = string (HTML)
	"""
	if fast == True:
		html = html.replace('/images/', '/images-small/')
		print('--- rendered in FAST mode ---')

	return html



# ---

# if __name__ == "__main__":

	# wiki = 'https://volumetricregimes.xyz' # remove tail slash '/'
	# pagename = 'Unfolded'
	
	# publication_unfolded = update_material_now(pagename, wiki) # download the latest version of the page
	# save(publication_unfolded, pagename) # save the page to file

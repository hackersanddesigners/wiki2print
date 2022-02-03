import urllib.request
import os
import re
import json
import jinja2
import datetime

STATIC_FOLDER_PATH = './static' # without trailing slash
PUBLIC_STATIC_FOLDER_PATH = '/static' # without trailing slash
TEMPLATES_DIR = None

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
	response = urllib.request.urlopen(url).read()
	data = json.loads(response)
	return data

# Save response as JSON file to disk
def save_JSON_file(pagename, data):
	json_file = f'{ STATIC_FOLDER_PATH }/{ pagename }.json'
	print('Saving JSON:', json_file)
	with open(json_file, 'w') as out:
		out.write( json.dumps(data, indent = 2) )
		out.close()
	return data

# Load former response as JSON from disk
def load_JSON_file(pagename):
	json_file = f'{ STATIC_FOLDER_PATH }/{ pagename }.json'
	if os.path.exists(json_file):
		print('Loading JSON:', json_file)
		with open(json_file, 'r') as out:
			data = json.load(out)
			out.close()
		return data

# Save generated HTML file to disk
def save_HTML_file(pagename, html):
	html_file = f'{ STATIC_FOLDER_PATH }/{ pagename }.html'
	print('Saving HTML file to disk:', html_file)
	with open(html_file, 'w') as out:
		out.write(html)
		out.close()
	return html

# Load former HTML file from disk
def load_HTML_file(pagename):
	html_file = f'{ STATIC_FOLDER_PATH }/{ pagename }.html'
	if os.path.exists(html_file):
		print('Loading HTML file from disk:', html_file)
		with open(html_file, 'r') as out:
			html = out.read()
			out.close()
		return html

# Save generated CSS file to disk
def save_CSS_file(pagename, css):
	css_file = f'{ STATIC_FOLDER_PATH }/{ pagename }.css'
	print('Saving CSS file to disk:', css_file)
	with open(css_file, 'w') as out:
		out.write(css)
		out.close()
	return css

# Load former CSS file from disk
def load_CSS_file(pagename):
	css_file = f'{ STATIC_FOLDER_PATH }/{ pagename }.css'
	if os.path.exists(css_file):
		print('Loading CSS file from disk:', css_file)
		with open(css_file, 'r') as out:
			css = out.read()
			out.close()
		return css

# makes API call to create/update index 
def create_index(wiki, subject_ns):
	url  = f'{ wiki }/api.php?action=query&format=json&list=allpages&apnamespace={ subject_ns["id"] }'
	data = do_API_request(url)
	data = data['query']['allpages']
	for page in data:
		page['title'] = page['title'].replace(subject_ns['name'] + ':' , '')
		page['slug'] = page['title'].replace(' ' , '_')
		pageJSON = load_JSON_file(page['slug'])
		page['updated'] = pageJSON and pageJSON['updated'] or '--'
	save_JSON_file('index', data)
	return data

# get index of publications in namespace
def get_index(wiki, subject_ns):
	"""
	  wiki = string
		subject_ns = object
	"""
	data = load_JSON_file('index') or create_index(
		wiki,
		subject_ns	
	)
	return data

def update_publication_date(wiki, subject_ns, pagename, updated):
	index = get_index(wiki, subject_ns)
	for page in index['pages']:
		if page['slug'] == pagename:
			page['updated'] = updated
	save_JSON_file('index', index)

# makes API call to create/update a publication 
def create_publication(wiki, subject_ns, styles_ns, pagename):
	url = f'{ wiki }/api.php?action=parse&page={ subject_ns["name"] }:{ pagename }&pst=True&format=json'
	data = do_API_request(url)
	now = str(datetime.datetime.now())
	data['updated'] = now
	save_JSON_file(pagename, data)
	
	update_publication_date(
		wiki,
		subject_ns, 
		pagename, 
		now
	)

	if 'parse' in data:
		html = data['parse']['text']['*']
		images = data['parse']['images']
		html = download_media(html, images, wiki)
		html = clean_up(html)
		html = add_item_inventory_links(html)
		html = tweaking(html)
		html = fast_loader(html)
	else: 
		html = None

	save_HTML_file(pagename, html)

	css_url = f'{ wiki }/api.php?action=parse&page={ styles_ns["name"] }:{ pagename }&prop=wikitext&pst=True&format=json'
	css_data = do_API_request(css_url)
	if 'parse' in css_data:
		print(json.dumps(css_data, indent=4))
		css = css_data['parse']['wikitext']['*']
		save_CSS_file(pagename, css)



	return html

# get publication in namespace
def get_publication(wiki, subject_ns, styles_ns, pagename):
	"""
	  wiki = string
		subject_ns = object
		styles_ns = object
		pagename = string
	"""
	publication = {
		'html': load_HTML_file(pagename) or create_publication(
			wiki,
			subject_ns,
			styles_ns,
			pagename
		),
		'css': load_CSS_file(pagename)
	}
	return publication











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
			response = urllib.request.urlopen(url).read()
			data = json.loads(response)

			# we select the first search result
			# (assuming that this is the image we are looking for)
			image = data['query']['allimages'][0] 

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

			import time
			time.sleep(3) # do not overload the server

		# replace src link
		image_path = f'{ PUBLIC_STATIC_FOLDER_PATH }/images/{ filename }' # here the images need to link to the / of the domain, for flask :/// confusing! this breaks the whole idea to still be able to make a local copy of the file
		matches = re.findall(rf'src="/images/.*?px-{ filename }"', html) # for debugging
		if matches:
			html = re.sub(rf'src="/images/.*?px-{ filename }"', f'src="{ image_path }"', html)
		else:
			matches = re.findall(rf'src="/images/.*?{ filename }"', html) # for debugging
			html = re.sub(rf'src="/images/.*?{ filename }"', f'src="{ image_path }"', html) 
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

def tweaking(html):
	"""
		html = string (HTML)
	"""
	html = html.replace('<a href="#X,_y,_z_(4_filmstills)"', '<a href="#x,_y,_z_(4_filmstills)"') # change the anchor link in the TOC to lowercase
	html = html.replace('<a href="#Rehearsal_as_the_%E2%80%98Other%E2%80%99_to_Hypercomputation"', '<a href="#Rehearsal_as_the_‘Other’_to_Hypercomputation"') # change the anchor link in the TOC to lowercase
	html = html.replace('<a href="#We_hardly_encounter_anything_that_didn%E2%80%99t_really_matter"', '<a href="#We_hardly_encounter_anything_that_didn’t_really_matter"') # change the anchor link in the TOC to lowercase
	html = re.sub(r'''<h3><span class="mw-headline" id="References.*?">References</span><span class="mw-editsection"><span class="mw-editsection-bracket"></span></span></h3>
<ul>''', '''<h3 class="references"><span class="mw-headline" id="References">References</span><span class="mw-editsection"><span class="mw-editsection-bracket"></span></span></h3>
<ul class="references">''', html) # add id="references" to h3 and ul, so the elements can be selected with CSS
	html = html.replace('src="./images/Userinfo.jpg"', 'src="./images/Userinfo.svg"') # This image is not on the wiki
	html = html.replace('src="./images/Topology-typography-1A.png"', 'src="./images/Topology-typography-1A.svg"') # This image is not on the wiki
	html = html.replace('src="./images/Topology-typography-1B.png"', 'src="./images/Topology-typography-1B.svg"') # This image is not on the wiki
	html = html.replace('src="./images/Topology-typography-2A.png"', 'src="./images/Topology-typography-2A.svg"') # This image is not on the wiki
	html = html.replace('src="./images/Topology-typography-2B.png"', 'src="./images/Topology-typography-2B.svg"') # This image is not on the wiki
	html = html.replace('trans*feminis', 'trans✶feminis') # changing stars
	html = html.replace('Trans*feminis', 'Trans✶feminis') # changing stars
	html = html.replace('star (*)', 'star (✶)') # changing stars
	html = html.replace('Our trans*feminist lens is sharpened by queer and anti-colonial sensibilities, and oriented towards (but not limited to) trans*generational, trans*media, trans*disciplinary, trans*geopolitical, trans*expertise, and trans*genealogical forms of study.', 'Our trans✶feminist lens is sharpened by queer and anti-colonial sensibilities, and oriented towards (but not limited to) trans✶generational, trans✶media, trans✶disciplinary, trans✶geopolitical, trans✶expertise, and trans✶genealogical forms of study.') # changing stars
	html = html.replace('<h2><span class="mw-headline" id="Invasive_imagination_and_its_agential_cuts">Invasive imagination and its agential cuts</span><span class="mw-editsection"><span class="mw-editsection-bracket"></span></span></h2>', '<h2><span class="mw-headline" id="Invasive_imagination_and_its_agential_cuts">Invasive imagination <br>and its agential cuts</span><span class="mw-editsection"><span class="mw-editsection-bracket"></span></span></h2>') 
	html = html.replace('<h2><span class="mw-headline" id="Volumetric_Regimes:_Material_cultures_of_quantified_presence">Volumetric Regimes: Material cultures of quantified presence</span><span class="mw-editsection"><span class="mw-editsection-bracket"></span></span></h2>', '<h2><span class="mw-headline" id="Volumetric_Regimes:_Material_cultures_of_quantified_presence">Volumetric Regimes:<br>Material cultures of<br>quantified presence</span><span class="mw-editsection"><span class="mw-editsection-bracket"></span></span></h2>') 
	html = html.replace('<h2><span id="Somatopologies_(materials_for_a_movie_in_the_making)"></span><span class="mw-headline" id="Somatopologies_.28materials_for_a_movie_in_the_making.29">Somatopologies (materials for a movie in the making)</span><span class="mw-editsection"><span class="mw-editsection-bracket"></span></span></h2>', '<h2><span id="Somatopologies_(materials_for_a_movie_in_the_making)"></span><span class="mw-headline" id="Somatopologies_.28materials_for_a_movie_in_the_making.29">Somatopologies (materials<br> for a movie in the making)</span><span class="mw-editsection"><span class="mw-editsection-bracket"></span></span></h2>') 
	html = html.replace('<h1><span class="mw-headline" id="Signs_of_clandestine_disorder:_The_continuous_aftermath_of_3D-computationalism"><a href="#Clandestine_disorder" title="Clandestine disorder">Signs of clandestine disorder: The continuous aftermath of 3D-computationalism</a></span><span class="mw-editsection"><span class="mw-editsection-bracket"></span></span></h1>', '<h1><span class="mw-headline" id="Signs_of_clandestine_disorder:_The_continuous_aftermath_of_3D-computationalism"><a href="#Clandestine_disorder" title="Clandestine disorder">Signs of clandestine disorder:<br>The continuous<br>aftermath of 3D-<br>computationalism</a></span><span class="mw-editsection"><span class="mw-editsection-bracket"></span></span></h1>') 
	html = html.replace('<h2><span class="mw-headline" id="The_Industrial_Continuum_of_3D">The Industrial Continuum of 3D</span><span class="mw-editsection"><span class="mw-editsection-bracket"></span></span></h2>', '<h2><span class="mw-headline" id="The_Industrial_Continuum_of_3D">The Industrial Continuum<br>of 3D</span><span class="mw-editsection"><span class="mw-editsection-bracket"></span></span></h2>') 
	html = html.replace('src="./images/Continuum_brighton.png"', 'src="./images/Continuum_brighton.svg"') # This image is not on the wiki
	html = html.replace('<h1><span class="mw-headline" id="Depths_and_Densities:_Accidented_and_dissonant_spacetimes"><a href="#Depths_and_densities" title="Depths and densities">Depths and Densities: Accidented and dissonant spacetimes</a></span><span class="mw-editsection"><span class="mw-editsection-bracket"></span></span></h1>', '<h1><span class="mw-headline" id="Depths_and_Densities:_Accidented_and_dissonant_spacetimes"><a href="#Depths_and_densities" title="Depths and densities">Depths and Densities:<br>Accidented<br>and dissonant<br>spacetimes</a></span><span class="mw-editsection"><span class="mw-editsection-bracket"></span></span></h1>') 
	html = html.replace('<h2><span class="mw-headline" id="Open_Boundary_Conditions:_a_grid_for_intensive_study">Open Boundary Conditions: a grid for intensive study</span><span class="mw-editsection"><span class="mw-editsection-bracket"></span></span></h2>', '<h2><span class="mw-headline" id="Open_Boundary_Conditions:_a_grid_for_intensive_study">Open Boundary Conditions:<br>a grid for intensive study</span><span class="mw-editsection"><span class="mw-editsection-bracket"></span></span></h2>') 
	html = html.replace('<h2><span class="mw-headline" id="Depths_and_Densities:_A_Bugged_Report">Depths and Densities: A Bugged Report</span><span class="mw-editsection"><span class="mw-editsection-bracket"></span></span></h2>', '<h2><span class="mw-headline" id="Depths_and_Densities:_A_Bugged_Report">Depths and Densities:<br>A Bugged Report</span><span class="mw-editsection"><span class="mw-editsection-bracket"></span></span></h2>') 
	html = html.replace('trans*generational, trans*media, trans*disciplinary, trans*geopolitical, trans*expertise, and trans*genealogical concerns', 'trans✶generational, trans✶media, trans✶disciplinary, trans✶geopolitical, trans✶expertise, and trans✶genealogical concerns') 
	html = html.replace('(*) all intersectional and ''intra-sectional ''aspects that are possibly needed.<ref name="ftn23">“The asterisk hold off the certainty of diagnosis.” Jack Halberstam, ''Trans*: A Quick and Quirky Account of Gender Variability'' (Berkeley: University of California Press, 2018), 4.</ref> Our trans*feminist lens is sharpened by queer and anti-colonial sensibilities, and oriented towards (but not limited to) trans*generational, trans*media, trans*disciplinary, trans*geopolitical, trans*expertise, and trans*genealogical forms of study.', '(✶) all intersectional and ''intra-sectional ''aspects that are possibly needed.<ref name="ftn23">“The asterisk hold off the certainty of diagnosis.” Jack Halberstam, ''Trans✶: A Quick and Quirky Account of Gender Variability'' (Berkeley: University of California Press, 2018), 4.</ref>') 
	html = html.replace('trans*generational', 'trans*generational') 
	html = html.replace('trans*media', 'trans✶media') 
	html = html.replace('trans*disciplinary', 'trans✶disciplinary') 
	html = html.replace('trans*geopolitical', 'trans✶geopolitical') 
	html = html.replace('trans*expertise', 'trans✶expertise') 
	html = html.replace('trans*genealogical', 'trans✶genealogical') 
	html = html.replace('✶', '<span class="star">✶</span>') 
	html = html.replace('<p><a href="#File', '<p class="image"><a href="#File') # give <p>'s that contain an non-thumb image a .image class
	# html = html.replace('', '') 
	
	return html

def clean_up(html):
	"""
		html = string (HTML)
	"""
	html = re.sub(r'\[.*edit.*\]', '', html) # remove the [edit]
	html = re.sub(r'href="/index.php\?title=', 'href="#', html) # remove the internal wiki links
	html = re.sub(r'&#91;(?=\d)', '', html) # remove left footnote bracket [
	html = re.sub(r'(?<=\d)&#93;', '', html) # remove right footnote bracket ]
	return html

def fast_loader(html):
	"""
		html = string (HTML)
	"""
	if fast == True:
		html = html.replace('/images/', '/images-small/')
		print('--- rendered in FAST mode ---')

	return html



def save(html, pagename):
	"""
		html = string (HTML)
		pagename = string
	"""
	print("saving " + pagename)
	if __name__ == "__main__":
		# command-line

		# save final page that will be used with PagedJS
		template_file = open(f'{ STATIC_FOLDER_PATH }/{ TEMPLATES_DIR }/template.html').read()
		template = jinja2.Template(template_file)
		doc = template.render(publication_unfolded=html, title=pagename)
		
		html_file = f'{ STATIC_FOLDER_PATH }/{ pagename }.html'
		print('Saving HTML:', html_file)
		with open(html_file, 'w') as out:
			out.write(doc)
			out.close()

		# save extra html page for debugging (CLI only)
		template_file = open(f'{ STATIC_FOLDER_PATH }/{ TEMPLATES_DIR }/template.inspect.html').read()
		template = jinja2.Template(template_file)
		doc = template.render(publication_unfolded=html, title=pagename)

		html_file = f'{ STATIC_FOLDER_PATH }/{ pagename }.inspect.html'
		print('Saving HTML:', html_file)
		with open(html_file, 'w') as out:
			out.write(doc)
			out.close()

	else:
		# Flask application 

		with open(f'{ STATIC_FOLDER_PATH }/{ pagename }.html', 'w') as out:
			out.write(html) # save the html to a file (without <head>)

# ---

# if __name__ == "__main__":

	# wiki = 'https://volumetricregimes.xyz' # remove tail slash '/'
	# pagename = 'Unfolded'
	
	# publication_unfolded = update_material_now(pagename, wiki) # download the latest version of the page
	# save(publication_unfolded, pagename) # save the page to file

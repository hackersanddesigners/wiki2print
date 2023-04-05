// Any JavaScript here will be loaded for all
// users on every page load.

console.log('hello from common.js')

// rename 'Discussion' tab or context menu button
// to 'CSS' in the 'Publishing' namespace.

const
	url    = window.location.href,
	NS     = 'Publishing',         // content namespace
	cssNS  = NS + 'CSS',           // css namespace
	jsNS   = NS + 'JS'             // js namespace


const parent = document.querySelector('#left-navigation .vector-menu-content-list')
// '#p-views ul'

if (url.includes(NS + ':')) {
	console.log('this page is in namespace', NS)

	const contentButton = document.createElement('li')
	contentButton.classList.add('collapsible', 'mw-list-item')
	contentButton.id = 'ca-content'
	contentButton.innerHTML = '<a href="' + url + '">Content!</a>'
	parent.appendChild(contentButton)

	const talkAnchor = document.querySelector('#ca-talk a')
	const talkLink = talkAnchor.href
	const cssButton  = document.createElement('li')
	cssButton.classList.add('collapsible', 'mw-list-item')
	cssButton.id = 'ca-css'
	cssButton.innerHTML = '<a href="' + talkLink + '">CSS!</a>'
	parent.appendChild(cssButton)

	const jsLink = talkAnchor.href.replace( cssNS, jsNS )
	const jsButton  = document.createElement('li')
	jsButton.classList.add('collapsible', 'mw-list-item')
	jsButton.id = 'ca-js'
	jsButton.innerHTML = '<a href="' + jsLink + '">JS!</a>'
	parent.appendChild(jsButton)


} else if (url.includes(cssNS + ':')) {
	console.log('this page is in namespace', cssNS)

	const contentAnchor = document.querySelector('#ca-nstab-publishing a')
	const contentLink = contentAnchor.href
	const contentButton = document.createElement('li')
	contentButton.classList.add('collapsible', 'mw-list-item')
	contentButton.id = 'ca-content'
	contentButton.innerHTML = '<a href="' + contentLink + '">Content!</a>'
	parent.appendChild(contentButton)

	const cssButton  = document.createElement('li')
	cssButton.classList.add('collapsible', 'mw-list-item')
	cssButton.id = 'ca-css'
	cssButton.innerHTML = '<a href="' + url + '">CSS!</a>'
	parent.appendChild(cssButton)

	const jsLink = contentAnchor.href.replace( NS, jsNS )
	const jsButton  = document.createElement('li')
	jsButton.classList.add('collapsible', 'mw-list-item')
	jsButton.id = 'ca-js'
	jsButton.innerHTML = '<a href="' + jsLink + '">JS!</a>'
	parent.appendChild(jsButton)

	const addTopicButton = document.querySelector('#ca-addsection')
	parent.removeChild(addTopicButton)


} else if (url.includes(jsNS + ':')) {
	console.log('this page is in namespace', jsNS)

	const contentLink = url.replace( jsNS, NS )
	const contentButton = document.createElement('li')
	contentButton.classList.add('collapsible', 'mw-list-item')
	contentButton.id = 'ca-content'
	contentButton.innerHTML = '<a href="' + contentLink + '">Content!</a>'
	parent.appendChild(contentButton)

	const cssLink = url.replace( jsNS, cssNS )
	const cssButton  = document.createElement('li')
	cssButton.classList.add('collapsible', 'mw-list-item')
	cssButton.id = 'ca-css'
	cssButton.innerHTML = '<a href="' + cssLink + '">CSS!</a>'
	parent.appendChild(cssButton)

	const jsLink = url
	const jsButton  = document.createElement('li')
	jsButton.classList.add('collapsible', 'mw-list-item')
	jsButton.id = 'ca-js'
	jsButton.innerHTML = '<a href="' + jsLink + '">JS!</a>'
	parent.appendChild(jsButton)

}

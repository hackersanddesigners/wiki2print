// Any JavaScript here will be loaded for all 
// users on every page load. 

console.log('hello from common.js')

// rename 'Discussion' tab or context menu button 
// to 'CSS' in the 'Publishing' namespace.

const 
	url    = window.location.href,
	NS     = 'Publishing',         // content namespace
	cssNS  = NS + 'CSS'            // css namespace

if (url.includes(NS + ':')) {
	console.log('this page is in namespace', NS)
	
	const talkAnchor = document.querySelector('#ca-talk a')
	const talkLink = talkAnchor.href
	
	talkAnchor.innerText = 'CSS'
	
	const pageViews  = document.querySelector('#p-views ul')
	const cssButton  = document.createElement('li')
		
	cssButton.classList.add('collapsible', 'mw-list-item')
	cssButton.id = 'ca-css'
	cssButton.innerHTML = '<a href="' + talkLink + '">CSS!</a>'
	pageViews.appendChild(cssButton)

} else if (url.includes(cssNS + ':')) {
	console.log('this page is in namespace', cssNS)
	
	const contentAnchor = document.querySelector('#ca-nstab-publishing a')
	const contentLink = contentAnchor.href
	
	contentAnchor.innerText = 'Content'
	
	const pageViews = document.querySelector('#p-views ul')
	const addTopicButton = document.querySelector('#ca-addsection')
		
	pageViews.removeChild(addTopicButton)	
		
	const contentButton = document.createElement('li')
		
	contentButton.classList.add('collapsible', 'mw-list-item')
	contentButton.id = 'ca-content'
	contentButton.innerHTML = '<a href="' + contentLink + '">Content!</a>'
	pageViews.appendChild(contentButton)
		
}

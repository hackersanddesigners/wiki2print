this.ready = new Promise(function ($) {
	document.addEventListener("DOMContentLoaded", $, { once: true });
});


class MM_Handler extends Paged.Handler {
	constructor(chunker, polisher, caller) {
		super(chunker, polisher, caller);
		this.chunker = chunker;
		this.polisher = polisher;
		this.caller = caller;
	}

	beforeParsed(content) {
		let c = content.querySelector(".mw-parser-output");
		let n = document.createElement("span")
		n.setAttribute("class", 'book-title');
		n.innerHTML = "Making Matters<br/>A Vocabulary for Collective Arts";
		c.prepend(n);
		// remove toc heading
		content.querySelector("#mw-toc-heading").remove();
	}
}

ready.then(async function () {
	// TODO: move to separate function
	// add url params as class to body for debugging. 
	// example: add `?debug` to uri, body gets class 'debug', write class .debug
	let params = new URLSearchParams(window.location.search);
	for(var par of params.entries()) {
		document.body.classList.add(par[0]); //key
 	}
		
	let flowText = document.querySelector("#source");
	
	let t0 = performance.now();
	Paged.registerHandlers(MM_Handler);
	let paged = new Paged.Previewer();

	paged.preview(flowText.content).then((flow) => {
		let t1 = performance.now();
		console.log( 
			"Rendering Pagedjs " +
			flow.total +
			" pages took " +
			(t1 - t0) +
			" milliseconds."
		);
		t0 = performance.now();
		const no_p5 = new URLSearchParams(window.location.search).has("no_p5"); // save some time by disabling the p5js backgrounds
		if (!no_p5) {
			let numChapters = document.querySelectorAll("h1 .mw-headline").length;
			let currChapter = 0;
			for (const i in flow.pages) { 
				let page = flow.pages[i]; console.log(page)
				let hasH1 = page.area.querySelector("h1");
				if (hasH1) currChapter++;
				this.renderSketch(
					page,
					parseInt(i) + 1,
					flow.pages.length,
					numChapters,
					currChapter
				);
			}
		}
		t1 = performance.now();
		console.log(
			"Rendering backgrounds for " +
			flow.total +
			" pages took " +
			(t1 - t0) +
			" milliseconds."
		);
	});

	let resizer = () => {
		let pages = document.querySelector(".pagedjs_pages");

		if (pages) {
			let scale = (window.innerWidth * 0.9) / pages.offsetWidth;
			if (scale < 1) {
				pages.style.transform = `scale(${scale}) translate(${window.innerWidth / 2 - (pages.offsetWidth * scale) / 2
					}px, 0)`;
			} else {
				pages.style.transform = "none";
			}
		}
	};
	resizer();

	window.addEventListener("resize", resizer, false);

	paged.on("rendering", () => {
		resizer();
	});
});


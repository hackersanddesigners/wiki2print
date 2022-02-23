this.ready = new Promise(function ($) {
	document.addEventListener("DOMContentLoaded", $, { once: true });
});

ready.then(async function () {
	let flowText = document.querySelector("#source");

	let t0 = performance.now();
	// Paged.registerHandlers(MyHandler);
	let paged = new Paged.Previewer()

	paged.preview(flowText.content).then((flow) => {
		let t1 = performance.now();
		console.log("Rendering Pagedjs " + flow.total + " pages took " + (t1 - t0) + " milliseconds.");
		t0 = performance.now();
		const no_p5 = new URLSearchParams(window.location.search).has("no_p5"); // save some time by disabling the p5js backgrounds
		if( ! no_p5 ){
			let numChapters = document.querySelectorAll('h1 .mw-headline').length;
			let currChapter = 0;
			for(const i in flow.pages){
				let page = flow.pages[i];
				let hasH1 = page.area.querySelector("h1")
				if ( hasH1 ) currChapter++;
				this.renderSketch(page, parseInt(i)+1, flow.pages.length,numChapters, currChapter)
			}
		}
		t1 = performance.now();
		console.log("Rendering backgrounds for " + flow.total + " pages took " + (t1 - t0) + " milliseconds.");
		
	});

	let resizer = () => {
		let pages = document.querySelector(".pagedjs_pages");

		if (pages) {
			let scale = ((window.innerWidth * .9 ) / pages.offsetWidth);
			if (scale < 1) {
				pages.style.transform = `scale(${scale}) translate(${(window.innerWidth / 2) - ((pages.offsetWidth * scale / 2) ) }px, 0)`;
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

/*
	class MyHandler extends Paged.Handler {
		constructor(chunker, polisher, caller) {
			super(chunker, polisher, caller);
			this.chunker = chunker;
			this.polisher = polisher;
			this.caller = caller;
		}

		// onAtPage(atPageNode) {
		// 	console.log(atPageNode);
		// }

		// afterPageLayout(pageFragment, page) {
		// 	pageFragment.style.position = "relative";
		// 	console.log(this.chunker.pages);
		// 	// this.renderSketch(page)
		// }

		// onBreakToken(breakToken, overflow, rendered){
		// 	console.log(breakToken, overflow, rendered);
		// }


		layoutNode(node) {
			// console.log(node);
		}		
	}
	*/
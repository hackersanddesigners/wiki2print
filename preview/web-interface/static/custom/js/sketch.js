function renderSketch(page, num, total, numChapters, currChapter){
	let isRight = page.element.classList.contains("pagedjs_right_page");
	

	const s = (sketch) => {
		let canvas;
		let colors = {
			'green': sketch.color(90,106,92), //#5A6A5C
			'brown': sketch.color(185,108,54), //#B96C36
			'blue': sketch.color(98,128,148), // #628094
			'default': sketch.color(98,128,148), // #628094
		};
		sketch.setup = () => {
			let el = page.element.querySelector(".pagedjs_pagebox");
			canvas = sketch.createCanvas(el.offsetWidth, el.offsetHeight, sketch.SVG);
			canvas.parent(el);
			canvas.position(0, 0);
			canvas.style("z-index", "-1");
			// sketch.background(220);
			if(!page.element.querySelector("h1")){
			let c = getComputedStyle(page.element).getPropertyValue('--base-color').trim() || 'default';
			let color = colors[c] || colors["default"];
			sketch.drawPageBorder(color);
			sketch.drawPageTop(color);
			}
		};

		sketch.drawPageBorder = (color) => {
			// sketch.fill(color);
			// sketch.noStroke();
			let step = sketch.height / numChapters;
			let left = 0;
			if (isRight) {
				left = sketch.width;
			} 
			// sketch.rect( left, 0, 10, step * ( currChapter - 1 ) );
			// sketch.rect( left, step * ( currChapter ), 10 , sketch.height );
			sketch.strokeWeight(20);
			sketch.stroke(color);	
			let t1 = 0;
			let b1 = step * ( currChapter - 1 );
			let t2 = step * currChapter;
			let b2 = sketch.height;
			sketch.line(left, t1, left, b1 );
			sketch.line(left, t2, left, b2 );
		
			for(let i = 0; i < 4; i++ ){
				let l = left + i * 3;
				if (isRight) {
					l = left - i * 3;
				}
				let b = sketch.random(t1,b1);
				let t = sketch.random(t1,b);
				sketch.line(l, t, l, b );
				b = sketch.random(t2,b2);
				t = sketch.random(t2,b);
				sketch.line(l, t, l, b );
			}
			// Alternatively, convert the sketch to on image and set it as background of the page
			// let dataurl = canvas.canvas.toDataURL('image/png');
			// canvas.parent().style.backgroundImage = dataurl;
			// canvas.style.display = "none";
		}

		sketch.drawPageTop = (color) => {
			sketch.stroke(color);	
			if( isRight ) {
				sketch.borderLine(".pagedjs_margin-top-left", 0);
				sketch.borderLine(".pagedjs_margin-top-right", 0);
			} else {
				// modified the css a bit so the .pagedjs_margin-content is not 100%
				sketch.borderLine(".pagedjs_margin-top-center .pagedjs_margin-content", 0);
			}
			sketch.borderLine(".pagedjs_margin-bottom-center .pagedjs_margin-content", sketch.height);
		}

		sketch.borderLine = (selector, y) => {
			/* Feels like I'm going to lose my mind */
			const tc = page.element.querySelector(selector);
			if(tc.offsetWidth > 0) {
				/* You just keep on pushin' my love
				Over the borderline (borderline) */
				sketch.line(tc.offsetLeft, y, tc.offsetLeft+tc.offsetWidth, y );
			}	
				
		}

		// sketch.draw = () => {};
	};

	let myp5 = new p5(s); 
}
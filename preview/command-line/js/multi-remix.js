
/* 

The cover image is derived from Multi Remix, 
an Open Source and cross-platform interpretation 
by Winnie Soon and Geoff Cox of the software app 
Multi by David Reinfurt. Multi updates the idea 
of the multiple from industrial production to the 
dynamics of the information age. Each cover 
presents an iteration of a possible 1,728 
arrangements, each a face built from minimal 
typographic furniture, and from the same source 
code.

https://o-r-g.com/apps/multi

https://aesthetic-programming.net/pages/2-variable-geometry.html

*/

/* --- Variable Geometry 1 (cover) --- */

/*Inspired by David Reinfurt's work - Multi*/
function setup() {
  var c = createCanvas(600, 600);
  c.parent('variable-geometry');
}

function draw() {
  //left
  noStroke()
  fill(0);
  // x, y, w, h
  rect(77, 169, 100, 16);

  //right
  rect(395, 184, 32, 25);
  fill(0);

  beginShape();
  vertex(395, 209);
  vertex(427, 209);
  vertex(407, 241);
  vertex(383, 241);
  endShape(CLOSE);

  //bottom
  noFill();
  stroke(0);
  strokeWeight(8);
  ellipse(255, 400, 100, 100);

}
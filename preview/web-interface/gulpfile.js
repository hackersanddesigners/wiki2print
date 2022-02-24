const { src, dest, watch, series, parallel } = require('gulp');
const sass = require('gulp-sass')(require('sass'));
const postcss = require('gulp-postcss');
const cssnano = require('cssnano');
const terser = require('gulp-terser');
const browsersync = require('browser-sync').create();
var exec = require('child_process').exec;

// Sass Task
function scssTask(){
  return src('./static/custom/sass/Making_Matters_Lexicon.scss', { sourcemaps: true })
      .pipe(sass())
      .pipe(postcss([cssnano()]))
      .pipe(dest('./static/custom/css', { sourcemaps: '.' }));
}

// JavaScript Task
// function jsTask(){
//   return src('app/js/script.js', { sourcemaps: true })
//     .pipe(terser())
//     .pipe(dest('dist', { sourcemaps: '.' }));
// }

function browsersyncServe(cb){
  browsersync.init({
    proxy: "127.0.0.1:5522/"   
  });
  cb();
}

function browsersyncReload(cb){
  browsersync.reload();
  cb();
}

// Watch Task
function watchTask(){
  // watch('*.html', browsersyncReload);
  watch(['**/*.scss', '**/*.js'], series(scssTask, browsersyncReload));
}

// Run Flask server
function runServer () {
	// 
  exec('python3 web-interface.py', function (err, stdout, stderr) {
    console.log(stdout);
    console.log(stderr);
		process.stdout.write(stdout);
  });
}

// Default Gulp Task
exports.serve = parallel(
	runServer,
	series(
		scssTask,
		// jsTask,
		browsersyncServe,
		watchTask
	)
);

exports.default = series(
	scssTask,
	// jsTask,
	browsersyncServe,
	watchTask
)




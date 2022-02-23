const { src, dest, watch, series } = require('gulp');
const sass = require('gulp-sass')(require('sass'));
const postcss = require('gulp-postcss');
const cssnano = require('cssnano');
const terser = require('gulp-terser');
const browsersync = require('browser-sync').create();

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

// Default Gulp Task
exports.default = series(
  scssTask,
  // jsTask,
  browsersyncServe,
  watchTask
);




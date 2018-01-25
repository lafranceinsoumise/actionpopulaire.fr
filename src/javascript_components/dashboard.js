import Masonry from 'masonry-layout';

var elem = document.querySelector('.masonry');
var msnry = new Masonry( elem, {
  itemSelector: '.col-md-6',
  percentPosition: true,
});

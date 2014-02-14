docviewer.Schema = function() {
  this.models       = {};
  this.views        = {};
  this.states       = {};
  this.helpers      = {};
  this.events       = {};
  this.elements     = {};
  this.text         = {};
  this.data         = {
    zoomLevel               : 700,
    pageWidthPadding        : 20,
    additionalPaddingOnPage : 30,
    state                   : { page: { previous: 0, current: 0, next: 1 } }
  };
};

// Imports the document's JSON representation into the docviewer.Schema form that
// the models expect.
docviewer.Schema.prototype.importCanonicalDocument = function(json) {
  // Ensure that IDs start with 1 as the lowest id.
  _.uniqueId();
  // Ensure at least empty arrays for sections.
  json.sections               = _.sortBy(json.sections || [], function(sec){ return sec.page; });
  json.annotations            = json.annotations || [];
  json.canonicalURL           = json.canonical_url;
  
  json.editions            = json.editions || [];

  this.document               = docviewer.jQuery.extend(true, {}, json);
  // Everything after this line is for back-compatibility.
  this.data.title             = json.title;
  this.data.totalPages        = json.pages;
  this.data.totalAnnotations  = json.annotations.length;
  this.data.sections          = json.sections;
  this.data.chapters          = [];
  this.data.annotationsById   = {};
  this.data.annotationsByPage = {};
  
  this.data.totalEditions  = json.editions.length;
  this.data.editionsById   = {};
  this.data.editionsByPage = {};
  _.each(json.annotations, docviewer.jQuery.proxy(this.loadAnnotation, this));
  _.each(json.editions, docviewer.jQuery.proxy(this.loadEdition, this));
};

// Load an annotation into the Schema, starting from the canonical format.
docviewer.Schema.prototype.loadAnnotation = function(anno) {
  if (anno.id) anno.server_id = anno.id;
  var idx     = anno.page - 1;
  anno.id     = anno.id || _.uniqueId();
  anno.title  = anno.title || 'Untitled Note';
  anno.text   = anno.content || '';
  anno.author = anno.author.username || 'no-author';
  anno.access = anno.access || 'public';
  anno.type   = anno.location && anno.location.image ? 'region' : 'page';
  anno.user_url = anno.user_url || '';
  if (anno.type === 'region') {
    var loc = docviewer.jQuery.map(anno.location.image.split(','), function(n, i) { return parseInt(n, 10); });
    anno.y1 = loc[0]; anno.x2 = loc[1]; anno.y2 = loc[2]; anno.x1 = loc[3];
  }else if(anno.type === 'page'){
    anno.y1 = 0; anno.x2 = 0; anno.y2 = 0; anno.x1 = 0;
  }
  this.data.annotationsById[anno.id] = anno;
  var page = this.data.annotationsByPage[idx] = this.data.annotationsByPage[idx] || [];
  var insertionIndex = _.sortedIndex(page, anno, function(a){ return a.y1; });
  page.splice(insertionIndex, 0, anno);
  return anno;
};

// Load an edition into the Schema
docviewer.Schema.prototype.loadEdition = function(edit) {
  if (edit.id) edit.server_id = edit.id;
  var idx              = edit.page - 1;
  edit.id              = edit.id || _.uniqueId();
  edit.modified_pages  = edit.modified_pages || [];
  edit.date            = edit.date || '';
  edit.author          = edit.author.username || 'no-author';
  edit.comment         = edit.comment || 'no-comment';
  edit.user_url        = edit.user_url || '';
  
  this.data.editionsById[edit.id] = edit;
  return edit;
};

// Remove an edition from the Schema
docviewer.Schema.prototype.removeEdition = function(edit_id) {
  delete this.data.editionsById[edit_id];
};

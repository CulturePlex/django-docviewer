docviewer.Schema.events.ViewText = {
  next: function(e){
    var viewer = this.elements._viewer;
    if (viewer.openEditor == 'editText') {
      var currentPage = this.models.document.currentPage();
      var text = $('#plain-text-area-'+currentPage).text();
      viewer.schema.text[currentPage-1] = text;
    }
    var nextPage = this.models.document.nextPage();
    this.loadText(nextPage);
  },
  previous: function(e){
    var viewer = this.elements._viewer;
    if (viewer.openEditor == 'editText') {
      var currentPage = this.models.document.currentPage();
      var text = $('#plain-text-area-'+currentPage).text();
      viewer.schema.text[currentPage-1] = text;
    }
    var previousPage = this.models.document.previousPage();
    this.loadText(previousPage);
  },
  search: function(e){
    e.preventDefault();
    this.viewer.open('ViewSearch');

    return false;
  }
};

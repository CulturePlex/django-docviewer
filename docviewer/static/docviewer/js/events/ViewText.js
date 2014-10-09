docviewer.Schema.events.ViewText = {
  next: function(e){
    var nextPage = this.models.document.nextPage();
    this.loadText(nextPage);
    
    currentPage = this.models.document.currentPage()
    if (mydocviewer.hiddenPages.indexOf(currentPage) != -1) {
        $('span.docviewer-next').click()
    }
  },
  previous: function(e){
    var previousPage = this.models.document.previousPage();
    this.loadText(previousPage);
    
    currentPage = this.models.document.currentPage()
    if (mydocviewer.hiddenPages.indexOf(currentPage) != -1) {
        $('span.docviewer-previous').click()
    }
  },
  search: function(e){
    e.preventDefault();
    this.viewer.open('ViewSearch');

    return false;
  }
};

docviewer.Schema.events.ViewDocument = {
  next: function(){
    var nextPage = this.models.document.nextPage();
    this.helpers.jump(nextPage);
    
    currentPage = this.models.document.currentPage()
    totalPages = this.models.document.totalPages
    if (mydocviewer.hiddenPages.indexOf(currentPage) != -1 && currentPage < totalPages) {
        $('span.docviewer-next').click()
    }

    // this.viewer.history.save('document/p'+(nextPage+1));
  },
  previous: function(e){
    var previousPage = this.models.document.previousPage();
    this.helpers.jump(previousPage);
    
    currentPage = this.models.document.currentPage()
    totalPages = this.models.document.totalPages
    if (mydocviewer.hiddenPages.indexOf(currentPage) != -1 && 1 < currentPage) {
        $('span.docviewer-previous').click()
    }

    // this.viewer.history.save('document/p'+(previousPage+1));
  },
  search: function(e){
    e.preventDefault();

    this.viewer.open('ViewSearch');
    return false;
  }
}

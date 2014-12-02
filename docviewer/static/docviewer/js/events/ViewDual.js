docviewer.Schema.events.ViewDual = {
  next: function(){
    var nextPage = this.models.document.nextPage();
    this.helpers.jump(nextPage);
    this.loadText(nextPage);
    
    currentPage = this.models.document.currentPage()
    if (mydocviewer.hiddenPages.indexOf(currentPage) != -1) {
        totalPages = this.models.document.totalPages
        if (currentPage == totalPages)
            $('span.docviewer-previous').click()
        else
            $('span.docviewer-next').click()
    }
  },
  previous: function(e){
    var previousPage = this.models.document.previousPage();
    this.helpers.jump(previousPage);
    this.loadText(previousPage);
    
    currentPage = this.models.document.currentPage()
    if (mydocviewer.hiddenPages.indexOf(currentPage) != -1) {
        totalPages = this.models.document.totalPages
        if (currentPage == 1)
            $('span.docviewer-next').click()
        else
            $('span.docviewer-previous').click()
    }
  },
  search: function(e){
    e.preventDefault();
    this.viewer.open('ViewSearch');
    return false;
  }
}

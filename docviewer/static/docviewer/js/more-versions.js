$(document).ready(function() {
    var moreLink = $(".docviewer-historyLink#more")
    var moreVersions = $(".docviewer-historyLink.docviewer-historyLink-more")
    var moreVersionsCount = moreVersions.length
    if (moreVersionsCount > 0)
        moreLink.show()
    
    moreLink.live("click", function(ev) {
        moreLink.hide()
        moreVersions.show()
    })
    
    var saveEditionButton = $("#edition-button.docviewer-editButton")
    saveEditionButton.live("click", function() {
        var maxShow = 4
        var allVersions = $(".docviewer-historyLink")
        var allVersionsCount = allVersions.length
        if (allVersionsCount + 1 > maxShow)
            moreLink.show()
    })
})

$(document).ready(function(){

(function ($) {
      $.each(['show', 'hide'], function (i, ev) {
        var el = $.fn[ev];
        $.fn[ev] = function () {
          this.trigger(ev);
          return el.apply(this, arguments);
        };
      });
    })(jQuery);


    pickers = $( ".picker" )
    if ( pickers.length){
        $( ".picker" ).autocomplete({
          source: function(request, response) {
                adata = { }
                adata['term'] = $(this).attr('element').val()
                $.ajax({
                 type: "POST",
                 dataType: 'json',
                 url: "autocomplete_users/",
                 async: false,
                 data: adata,
                 success: function(data) {
                      response(data)
                   },
               });
             },
          //$('.picker').data('url'),
          minLength: 1,
          select: function (ev, ui){
            adata = { }
            adata['doc_id'] = $(ev.target).parents(".document-row").data('id')
            adata['username'] = ui.item.value
            $.ajax({
              url: "add_sharer/",
              data: adata,
              dataType: 'json',
              type: 'GET',
              success: function(payload) {
                var user = adata['username']
                $(ev.target).prev().append("<a class=\"nolink\" href=\"#\"><span class=\"sharer\" data-id=\""+ user +"\">@" + user + "</span></a>")
              }})
          }
        });
    }
    
    
    pickers2 = $( ".picker2" )
    if ( pickers2.length){
        $( ".picker2" ).autocomplete({
          source: function(request, response) {
                adata = { }
                adata['term'] = $(this).attr('element').val()
                $.ajax({
                 type: "POST",
                 dataType: 'json',
                 url: "autocomplete_taggit_tags/",
                 async: false,
                 data: adata,
                 success: function(data) {
                      response(data)
                   },
               });
             },
          //$('.picker').data('url'),
          minLength: 1,
          select: function (ev, ui){
            adata = { }
            adata['doc_id'] = $(ev.target).parents(".document-row").data('id')
            adata['tag'] = ui.item.value
            $.ajax({
              url: "add_taggit_tag/",
              data: adata,
              dataType: 'json',
              type: 'POST',
              success: function(payload){
                //location.reload();
                if (payload.added) {
                    var tag = adata['tag']
                    $(ev.target).prev().append("<a class=\"nolink\" href=\"#\"><span class=\"taggit_tag\" data-id=\""+ tag +"\">" + tag + "</span></a>")
                }
              }})
          }
      });
      
      $("input#id_taggit_tags").bind("enterKey",function(ev){
        if ($(this).val() != "") {
            adata = { }
            adata['doc_id'] = $(ev.target).parents(".document-row").data('id')
            adata['tag'] = $(this).val()
            $.ajax({
              url: "add_taggit_tag/",
              data: adata,
              dataType: 'json',
              type: 'POST',
              success: function(payload){
                //location.reload();
                if (payload.added) {
                    var tag = adata['tag']
                    $(ev.target).prev().append("<a class=\"nolink\" href=\"#\"><span class=\"taggit_tag\" data-id=\""+ tag +"\">" + tag + "</span></a>")
                }
              }})
        }
      });
      
      $("input#id_taggit_tags").keypress(function(e){
          if(e.keyCode == 13)
          {
              $(this).trigger("enterKey");
          }
      });
  }

    $(".docviewer-textLink .nolink .sharer").live('click', function (ev) {
        ev.preventDefault()
        //var url = $(ev.currentTarget).data("remove-collaborator-url")
        var collaborator = $(ev.currentTarget).data("id")
        var doc = $(ev.currentTarget).data("doc-id")
        var data = {}
        data["doc_id"] = doc
        data["username"] = collaborator
        $.ajax({
            type: "POST",
            url: "remove_sharer/",
            dataType: "json",
            data: data,
            success: function(payload){
                var user = ev.target.textContent
                var user_list = []
                var collaborators = $(ev.target).parents('#sharers')
                collaborators.find(".sharer").each(function(index, data) {
                    user_list.push(data.textContent)
                })
                var index = user_list.indexOf(user) + 1
                var collaborator = collaborators.children().filter(":nth-child("+ index +")")
                collaborator.remove()
            }
        })
    });
    
    
    
    $(".docviewer-textLink .nolink .taggit_tag").live('click', function (ev) {
        ev.preventDefault()
        //var url = $(ev.currentTarget).data("remove-tag-url")
        var tag = $(ev.currentTarget).data("id")
        var doc = $(ev.currentTarget).data("doc-id")
        var data = {}
        data["doc_id"] = doc
        data["tag"] = tag
        $.ajax({
            type: "POST",
            url: 'remove_taggit_tag/',
            dataType: "json",
            data: data,
            success: function(payload){
                var tag = ev.target.textContent
                var tag_list = []
                var tags = $(ev.target).parents('#taggit_tags')
                tags.find(".taggit_tag").each(function(index, data) {
                    tag_list.push(data.textContent)
                })
                var index = tag_list.indexOf(tag) + 1
                var tag2 = tags.children().filter(":nth-child("+ index +")")
                tag2.remove()
            }
        })
    });
    
    
    
    var my_top
    var my_left
    var my_parent
    
    $(".picker.ui-autocomplete-input, .picker2.ui-autocomplete-input").live('click', function (ev) {
//        my_top = $(ev.target).offset().top + $(ev.target).outerHeight() - $(window).scrollTop();
//        my_left = $(ev.target).offset().left - $(window).scrollLeft();
//        my_top = 0
//        my_left = 0
//        my_parent = $(ev.target).offsetParent()
    })
    
    $("ul.ui-autocomplete.ui-menu.ui-widget.ui-widget-content.ui-corner-all").live('show', function (ev) {
        $(ev.target).offset({top: my_top, left: my_left})
//        var element = $(ev.target).detached()
//        my_parent.append($(ev.target))
    })
    
    $("ul.ui-autocomplete.ui-menu.ui-widget.ui-widget-content.ui-corner-all").live('hide', function (ev) {
        $(ev.target).offset({top: 0, left: 0})
    })

})

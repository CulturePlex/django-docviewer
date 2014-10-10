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
//            adata['doc_id'] = $(ev.target).parents(".document-row").data('id')
            adata['username'] = ui.item.value
            $.ajax({
              url: "add_sharer/",
              data: adata,
              dataType: 'json',
              type: 'POST',
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
//            adata['doc_id'] = $(ev.target).parents(".document-row").data('id')
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
              $(this).val("")
          }
      });
  }

    $(".docviewer-textLink #sharers a.nolink").live('click', function (ev) {
        ev.preventDefault()
        //var url = $(ev.currentTarget).data("remove-collaborator-url")
        var user1 = $(ev.currentTarget.children[0]).data("id")
        var doc = $(ev.currentTarget.children[0]).data("doc-id")
        var data = {}
        data["doc_id"] = doc
        data["username"] = user1
        $.ajax({
            type: "POST",
            url: "remove_sharer/",
            dataType: "json",
            data: data,
            success: function(payload){
                var user2 = "@"+user1
                var user_list = []
                var collaborators = $(ev.target).parents('#sharers')
                collaborators.find(".sharer").each(function(index, data) {
                    user_list.push(data.textContent)
                })
                var index = user_list.indexOf(user2) + 1
                var user3 = collaborators.children().filter(":nth-child("+ index +")")
                user3.remove()
            }
        })
    });
    
    
    
    $(".docviewer-textLink #taggit_tags a.nolink").live('click', function (ev) {
        ev.preventDefault()
        //var url = $(ev.currentTarget).data("remove-tag-url")
        var tag1 = $(ev.currentTarget.children[0]).data("id")
        var doc = $(ev.currentTarget.children[0]).data("doc-id")
        var data = {}
        data["doc_id"] = doc
        data["tag"] = tag1
        $.ajax({
            type: "POST",
            url: 'remove_taggit_tag/',
            dataType: "json",
            data: data,
            success: function(payload){
                var tag2 = tag1
                var tag_list = []
                var tags = $(ev.target).parents('#taggit_tags')
                tags.find(".taggit_tag").each(function(index, data) {
                    tag_list.push(data.textContent)
                })
                var index = tag_list.indexOf(tag2) + 1
                var tag3 = tags.children().filter(":nth-child("+ index +")")
                tag3.remove()
            }
        })
    });
  
  $(".docviewer-textLink .nolink .sharer").live("click", function(ev) {
//    ev.preventDefault()
//    ev.stopPropagation()
    return false
  })
  
  $(".docviewer-textLink .nolink .taggit_tag").live("click", function(ev) {
//    ev.preventDefault()
//    ev.stopPropagation()
    return false
  })
    
    var all_pickers = $(".ui-autocomplete-input")
    if (all_pickers.length) {
        all_pickers.autocomplete({
            close: function(ev, ui) {
                $(this).val("")
            }
        })
    }
    
    
    
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
//        $(ev.target).offset({top: my_top, left: my_left})
//        var element = $(ev.target).detached()
//        my_parent.append($(ev.target))
    })
    
    $("ul.ui-autocomplete.ui-menu.ui-widget.ui-widget-content.ui-corner-all").live('hide', function (ev) {
//        $(ev.target).offset({top: 0, left: 0})
    })

})


//highlight action if targeted in url
$(document).ready(function(){
  $(".search-hit:target").find(".taken-actions").css("background", "lightyellow")
})

//default popover and tooltip activators
$(function () {
  $('[data-toggle="popover"]').popover()
});
$(function () {
  $('[data-toggle="tooltip"]').tooltip()
});

//custom popover activator
$('[popover-content]').each(function(){
  $(this).popover({
    placement: 'top',
    html : ($(this).attr("popover-html") == "true"),
    title : $(this).attr("popover-title"),
    content : $(this).attr("popover-content")
  })
});

//custom tooltip activator
$('[tooltip-title]').each(function(){
  $(this).tooltip({
    placement : 'bottom',
    title : $(this).attr("tooltip-title")
  })
});

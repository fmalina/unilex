$(document).ready(function(){
    $("#q").autocomplete("/vocabularies/autocomplete", {
        width: 380,
        scrollHeight: 'auto',
        selectFirst: false,
        autoFill: false,
        minChars: 1
    }).attr("autocomplete","off");
    $("#q").result(function(event, data, formatted){
        if(data){
            window.location = $(data[0]).find('.go').attr('href');
            $(this).val('');
        }
    });
});

function leaving_callback () {}

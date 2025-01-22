$(function(){
    // search
    $("#q").autocomplete("/tree/autocomplete", {
        width: 330,
        scrollHeight: 'auto',
        selectFirst: false,
        autoFill: false,
        minChars: 4
    }).attr("autocomplete","off");
    $("#q").result(function(event, data, formatted){
        if(data){
            window.location = $(data[0]).find('.go').attr('href');
            $(this).val('');
        }
    });

    // messages
    $('#messages').append('<a class="dismiss" href="javascript:void()">dismiss</a>');
    $('.dismiss').bind('click', function(){
        $('#messages').slideUp('slow');
    });
    $('#messages').animate({opacity: 1.0}, 7000).slideUp('slow');
});

// pay
function leaving_callback () {}

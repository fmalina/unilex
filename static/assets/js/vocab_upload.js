$(function(){
    $("input[name='file'],textarea").change(function (){
        button = $(this).parents('form:first').find('button');
        if($(this).val()!=''){
            button.removeAttr('disabled');
        } else {
            button.attr('disabled', 'disabled');
        }
    });
    
    // Excel table animation intro
    $('.p2' ).delay(4000).fadeIn({
        start: function(){
            $('thead .p1, caption .p1').hide();
        }
    });
    $('.p3').delay(8000).fadeIn();
    $('.p4').delay(12000).fadeIn();
});

$(function(){
    $(".sort").sortable({
        placeholder: 'placeholder',
        forcePlaceholderSize: true,
        update: function(){
            var data = $(this).sortable('serialize');
            $.ajax({
                type: 'POST',
                data: data,
                url: $('.sort').attr('data-submit'),
                success: function(){
                    $(this).addClass("done");
                    // TODO re-key the li IDs instead of reload
                    window.location.reload(); 
                }
            });
        }
    });
    $(".isotope").isotope({itemSelector: '.L1in'});
});
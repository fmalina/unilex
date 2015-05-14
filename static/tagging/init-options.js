$(function(){
    $('#options input').each(function(){
        this.value = window.localStorage.getItem(this.id);
    }).blur(function(){
        window.localStorage.setItem(this.id, this.value);
    });
    $('button').on('click', function(){
        window.close();
    });
});
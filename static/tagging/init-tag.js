$(function(){
    tag.init();
    setInterval( function(){ tag.saveCurrent(); }, 5000);
});
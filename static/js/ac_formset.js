function makeAutocomplete(sel, url){
    sel.autocomplete(url, {
        width: 300,
		scrollHeight: 'auto',
		selectFirst: true,
		autoFill: false,
		minChars: 2,
		cacheLength: 0,
        formatItem: function(row) {
            return row[0];
        }
    }).attr("autocomplete","off");

	$(".autocomplete").result(function(event, data, formatted){
	    if(data){
	        $(this).parent().find("div").html(data[0]);
	        $(this).parent().find("input[type=text]").val(data[1]).hide();
	    }
	});
}

function acFormset(ac_url, formset_prefix){
    makeAutocomplete($('.show .autocomplete'), ac_url);
    $('#'+ formset_prefix +' li').formset({
        prefix: formset_prefix,
        formCssClass: formset_prefix + '-row',
        deleteText: '<b>×</b>',
        addText: '<span><b>+</b> add another</span>',
        added: function(li) {
            li.find('p').remove();
            var txt = li.find('.autocomplete');
            txt.unbind();
            txt.show();
            makeAutocomplete(txt, ac_url);
        }
    });
    $('.set li input[type=text]').not('.show input').hide();
}
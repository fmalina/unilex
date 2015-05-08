function makeAutocomplete(sel, url){
    sel.autocomplete(url, {
        width: 400,
		scrollHeight: 'auto',
		selectFirst: true,
		autoFill: false,
		minChars: 2,
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

function conceptFormset(site_url, formset_prefix){   
    makeAutocomplete($('.show .autocomplete'), site_url + '/vocabularies/autocomplete');
    $('#'+ formset_prefix +' li').formset({
        prefix: formset_prefix,
        formCssClass: formset_prefix + '-row',
        deleteText: '✗',
        addText: '<span>+ add another</span>',
        added: function(li) {
            li.find('p').remove();
            var txt = li.find('.autocomplete');
            txt.unbind();
            txt.show();
            makeAutocomplete(txt, site_url + '/vocabularies/autocomplete');
        }
    });
    $('.set li input[type=text]').not('.show input').hide();
}
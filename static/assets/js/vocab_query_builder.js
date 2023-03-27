var CHOOSER = {
    autocompleteServer : '',
    addNewTerm : function() {
        var id = CHOOSER.newId();
        const newTerm = `<div class="andTerm">
                <a href="#" class="convertToNot">NOT</a>
                <div class="termWrapper">
                    <div class="singleTerm">
                        <input type="text" class="autocompleteTerm" value="" id="${id}" name="${id}">
                        &nbsp;<a href="#" class="deleteSingleTerm">X</a>
                    </div>
                </div>
                &nbsp;<a href="#" class="orTerm">or...</a>
            </div>`;
            

        $('#placeholder').before(newTerm);
        CHOOSER.setupAutocomplete(id);
    },
    deleteSingleTerm : function(singleTermDiv) {
        var termWrapper = singleTermDiv.parent('div.termWrapper');
        var childTermCount = termWrapper.children('div.singleTerm').length;
        if (childTermCount > 1) {
            singleTermDiv.remove();
        } else {
            termWrapper.parent('div.andTerm').remove();
        }
        CHOOSER.updateQuery();
    },
    convertToNot : function(andTermDiv) {
        if (andTermDiv.hasClass('notTerm')) {
            andTermDiv.removeClass('notTerm');
        } else {
            andTermDiv.addClass('notTerm');
        }
        CHOOSER.updateQuery();
    },
    orTerm : function(termWrapperDiv) {
        var id = CHOOSER.newId();
        var childTermCount = termWrapperDiv.children('div.singleTerm').length;
        const newSingleTerm = `<div class="singleTerm">
                <input type="text" class="autocompleteTerm" value="" id="${id}" name="${id}">
                &nbsp;<a href="#" class="deleteSingleTerm">X</a>
            </div>`;  
        termWrapperDiv.append(newSingleTerm);
        CHOOSER.setupAutocomplete(id);
    },
    newId : (function() {
        var count = 1;
        return function() {
            return "term" + count++;
        }
    })(),
    setupAutocomplete : function(id) {
        // The autocomplete code assigns the selected item's HTML as the value of the input
        // and then triggers a 'result' event on it, passing some useful data.
        $('#' + id).autocomplete(CHOOSER.autocompleteServer + "/vocabularies/autocomplete", {
            width: 430,
            scrollHeight: 'auto',
            selectFirst: false,
            autoFill: false,
            minChars: 1
        }).attr("autocomplete","off").bind('result', function(event, extraData){
            CHOOSER.handleSelection($(this), extraData[0], extraData[1]);
            return false;
        });
    },
    handleSelection : function(input, data, number) {
        data = $(data);
        input.hide();
        var p = data.children('p');
        var aLink = p.children('a.go').attr('href');
        var queryPart = p.children('a.add').attr('title');
        var title = p.children('span').html();
        var guid = p.children('small');
        input.parent('div.singleTerm').prepend(title).prepend('<span class="queryPart">' + queryPart + '</span>');
        CHOOSER.updateQuery();
    },
    updateQuery : function() {
        var container = $('#termChoices');
        var sb = "";
        var andSep = "";
        container.children('div.andTerm').each(function(i,andTermDiv){
            andTermDiv = $(andTermDiv);
            sb += andSep;
            andSep = " AND ";
            if (andTermDiv.hasClass('notTerm')) {
                sb += "NOT "
            }
            var orTerms = andTermDiv.children('div.termWrapper').children('div.singleTerm');
            if (orTerms.length == 1) {
                sb += orTerms.children('span.queryPart').html();
            } else {
                var orSep = "";
                sb += "( ";
                orTerms.each(function(j, singleTermDiv) {
                    singleTermDiv = $(singleTermDiv);
                    sb += orSep;
                    orSep = " OR ";
                    sb += singleTermDiv.children('span.queryPart').html();
                });
                sb += " )";
            }
        });
        $('#id_query').val(sb);
    }
}
$(function() {
    $('#addNew').on('click', function(event) {
        CHOOSER.addNewTerm();
        return false;
    });
    $(document).on('click', '.deleteSingleTerm', function(event) {
        CHOOSER.deleteSingleTerm($(this).parents('div.singleTerm'));
        return false;
    });
    $(document).on('click', '.convertToNot', function(event) {
        CHOOSER.convertToNot($(this).parents('div.andTerm'));
        return false;
    });
    $(document).on('click', '.orTerm', function(event) {
        CHOOSER.orTerm($(this).parent('div.andTerm').children('div.termWrapper'));
        return false;
    });
});

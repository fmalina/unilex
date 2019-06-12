var tag = {
    // configure this
    repository: 'https://unilexicon.co',//m', // vocabulary repository url, has to be https

    isAllowed: function(tabId, changeInfo, tab) {
        // Called when the url of a tab changes.
        // If the site string is found in the tab's URL, show page action
        if(tab.url){
            chrome.pageAction.show(tabId);
            window.localStorage.removeItem(tab.url);
        }
    },

    saveCurrent: function(){
        chrome.tabs.getSelected(null, function(tab){
            // custom save action for localStorage
        });
    },

    tagging: function(tab){
        var body = $('body');
        if(body.text().indexOf('Loading...') >= 0){
            body.load(tag.repository + '/tag/'+tab.url, function(){
                $('#id_title').val(tab.title);
                $('#id_desc' ).val();
                // refresh the formset
                $('.delete-row').remove();
                $('.add-row').parent().remove();
                acFormset(tag.repository+'/vocabularies/autocomplete', 'form');
            });
        }
    },

    init: function(){
        var port = chrome.extension.connect();
        chrome.tabs.getSelected(null, function(tab){
            tag.tagging(tab);
        });

        $("button.save").on('click', function(event){
            event.preventDefault();
            tag.saveCurrent();
            $("button.save").animate({
                opacity: .5}, 500).animate({
                opacity: 1}, 500).parents('form:first').submit();
        });

        $("button.discard").on('click', function(event){
            event.preventDefault();
            $(this).text("Crunching...");
            chrome.tabs.getSelected(null, function(tab){
                tag.tagging(tab);
            });
        });
    }
};

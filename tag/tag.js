var tag = {
    // configure this
    repository: 'https://unilexicon.com', // vocabulary repository url, has to be https
    // done configuring
    site: function(){
        return window.localStorage.getItem('site');
    }, // deployment domain
    id: function(url){
        // catch the id from paths such as
        // node/id or node/id/somethingelse
        var id = false;
        var parts = url.split('/');
        var br = false;
        for(x=0; x<parts.length; x++){
            if(br){id = parts[x];}
            if(parts[x]=='node'){br = true;}
        }
        return id;
    },
    
    isAllowed: function(tabId, changeInfo, tab) {
        // Called when the url of a tab changes.
        // If the site string is found in the tab's URL, show page action
        if(tab.url.indexOf(tag.site()) > -1 && tag.id(tab.url)){
            chrome.pageAction.show(tabId);
            window.localStorage.removeItem(tag.id(tab.url));
        }
    },
    
    authToken: function(){
        // Create SWORD authentication token in agreed format
        var password = window.localStorage.getItem('password');
        var username = window.localStorage.getItem('username');
        password = md5(password);
        token = 'username=' + username + ':password=' + password;
        return md5(token);
    },
    
    setAuth: function(){
        $('#id_name').val(window.localStorage.getItem('name'));
        $('#id_auth_token').val(tag.authToken());
    },
    
    save: function(id){
        window.localStorage.setItem(id, $('body').html());
        window.localStorage.setItem(id+'title',       $('#id_title').val());
        window.localStorage.setItem(id+'notes',       $('#id_notes').val());
        window.localStorage.setItem(id+'description', $('#id_description').val());
    },

    saveCurrent: function(){
        chrome.tabs.getSelected(null, function(tab){
            tag.save(tag.id(tab.url));
        });
    },
    
    tagging: function(id){
        var body = $('body');
        body.html('Loading...');
        var state = window.localStorage.getItem(id);
    
        if(state == undefined){
            body.load(tag.repository + '/tag/'+id, function(){
                // save state
                tag.save(id);
                tag.setAuth();
            });
        }
        else {
            // retrieve last state
            body.html(state);
            
            $('#id_title').val(window.localStorage.getItem(id+'title'));
            $('#id_notes').val(window.localStorage.getItem(id+'notes'));
            $('#id_description').val(window.localStorage.getItem(id+'description'));
            
            tag.setAuth();
            // refresh the formset
            $('.delete-row').remove();
            $('.add-row').parent().remove();
            conceptFormset(tag.repository, 'form');
        }
    },
    
    init: function(){
        $('head').append("<link rel='stylesheet' href='" + tag.repository + "/css/autocomplete.css' />" +
                         "<link rel='stylesheet' href='" + tag.repository + "/css/set.css' />");

        var port = chrome.extension.connect();
        chrome.tabs.getSelected(null, function(tab){
            tag.tagging(tag.id(tab.url));
        });
        
        $("button.send").on('click', function(){
            $("button.send").text("Sending...");
        });

        $("button.save").on('click', function(event){
            event.preventDefault();
            tag.saveCurrent();
            $("button.save").animate({opacity: .5}, 500).animate({opacity:1}, 500);
        });

        $("button.discard").on('click', function(event){
            event.preventDefault();
            chrome.tabs.getSelected(null, function(tab){
                window.localStorage.removeItem(tag.id(tab.url));
            });
            $("button.discard").text("Crunching...").animate({opacity:.5}, 500, function(){
                location.reload();
            });
        });
    }
};

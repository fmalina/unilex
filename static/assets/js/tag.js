function Id(cssid){
    return document.getElementById(cssid);
}

function initTagging() {
    var doc = document;
    if(parent.document) doc = parent.document;
    var metaTag = parent.document.querySelector('meta[name="description"]');
    var desc = metaTag ? metaTag.getAttribute("content") : '';

    Id("id_title").value = doc.title;
    Id("id_key").value = doc.URL;
    Id("id_desc").value = desc;

	acFormset('/vocabularies/autocomplete',
    document.querySelector('.set').id);
}

document.addEventListener('DOMContentLoaded', initTagging);

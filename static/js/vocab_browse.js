var VocabBrowser = {
    root: null,
    toproot: null,
    init: function () {
        $.get(location.pathname + 'json', VocabBrowser.initTree, 'json');
    },
    id: function(id) {
        return id.replace('v-', '');
    },
    initTree: function (json) {
        VocabBrowser.root = json.id;
        VocabBrowser.toproot = json.id;
        var infovis = document.getElementById('infovis');
        var w = infovis.offsetWidth - 50, h = infovis.offsetHeight - 50;
        w = h = Math.min(w, h);
        // init Hypertree
        var ht = new $jit.Hypertree({
            'injectInto': 'infovis',
            'width': w,
            'height': h,
            //Change node and edge styles such as color, width and dimensions.
            Node: {
                dim: 9,
                color: "#c00"
            },
            Edge: {
                overridable: true,
                lineWidth: 1,
                color: "#aa0"
            },
            // Attach event handlers and add text to the
            // labels. This method is only triggered on label creation
            onCreateLabel: function (domElement, node){ // Change node styles when labels are placed or moved.
                domElement.innerHTML = node.name;
                if(node.data.type == 'vocab'){
                    $(domElement).addClass('vocabnode');
                }
                if(json.queries){
                    if(node.data.query != ''){
                        $(domElement).addClass('has_query');
                    }
                }
                $(domElement).bind('click', function () { VocabBrowser.go(node.id); });
            },
            onPlaceLabel: function(domElement, node){
                var style = domElement.style;
                var current = node.id == VocabBrowser.root;
                for (var i = 0; i < 6; i++ ) {
                    $(domElement).toggleClass('node-depth-' + i, node._depth == i);
                }
                style.display = '';
                if (node.data.type == 'concept') {
                    if(node._depth > 2) {
                        style.display = 'none';
                    }
                }
                if (current) {
                    VocabBrowser.showIcons(domElement, node);
                } else {
                    VocabBrowser.hideIcons(domElement, node);
                }
                style.zIndex = 100 - node._depth;
                var left = parseInt(style.left);
                var w = domElement.offsetWidth;
                var h = domElement.offsetHeight;
                style.left = left - (w / 2) + 'px';
                style.top = parseInt(style.top) - (h * 1.25) + 'px';
            },
            onAfterCompute: function(){
                var node = VocabBrowser.rootNode();
                if (node && node.id.indexOf("v-") == -1){
                    $.get(VocabBrowser.conceptUri(node.id,'edit'), function (data) {
                        $('#inner-details').html(data);
                    });
                } else {
                    $.get('/vocabularies/' + VocabBrowser.id(VocabBrowser.root) + '/edit', function (data) {
                        $('#inner-details').html(data);
                    });
                }
            }
        });
        // load JSON data.
        ht.loadJSON(json);
        // compute positions and plot.
        ht.refresh();
        ht.controller.onAfterCompute();
        VocabBrowser.ht = ht;
        setInterval(VocabBrowser.check_fragment, 100);
    },
    rootNode: function () {
        if (VocabBrowser.ht) {
            return VocabBrowser.ht.graph.getNode(VocabBrowser.root);
        }
    },
    go: function (id) {
        if (VocabBrowser.root == id) return;
        VocabBrowser.ht.onClick(id);
        location.hash = 'c-' + id;
        VocabBrowser.last_fragment = location.hash;
        VocabBrowser.root = id;
    },
    last_fragment: null,
    check_fragment: function () {
        var fragment = location.hash;
        if (fragment != VocabBrowser.last_fragment) {
            var mo = /c-([a-z0-9]+)/.exec(fragment);
            if (mo)
                VocabBrowser.go(mo[1]);
            VocabBrowser.last_fragment = fragment;
            // redirect to teh rigt context when logging in
            // $('#loginlink').attr('href', this.href + location.hash);
        }
    },
    showIcons: function (domElement, node) {
        $('#editicons').remove();
        var del   = '<img src="/img/icon-delete.png" alt="Delete" title="Delete..." id="icon-delete" >';
        var cut   = '<img src="/img/icon-cut.png"    alt="Cut"    title="Cut..."    id="icon-cut"    >';
        var paste = '<img src="/img/icon-paste.png"  alt="Paste"  title="Paste..."  id="icon-paste"  >';
        var add   = '<img src="/img/icon-add.png"    alt="Add"    title="Add..."    id="icon-add"    >';
        var edit  = '<img src="/img/icon-edit.png"   alt="Edit"   title="Edit..."   id="icon-edit"   >';
        var save  = '<img src="/img/icon-save.png"   alt="Save"   title="Download"  id="icon-save"   >';
        if (node.data.type == 'vocab') {
            $(domElement).append('<p id="editicons">' + save + add + del + paste + '</p>');
            $('#icon-save').bind('click', function () {
                location.href = location.pathname + 'skos'; 
            });
            nid = VocabBrowser.id(node.id);
            $('#icon-add').bind('click', function () {
                $.get('/vocabularies/' + nid + '/concepts/new', function (data) {
                    $('#inner-details').prepend(data);
                    $("#inner-details input[type='text']:first").focus();
                });
            });
            $('#icon-delete').bind('click', function () {
                $.get('/vocabularies/' + nid + '/delete', function (data) {
                    $('#inner-details').prepend(data);
                });
            });
            $('#icon-paste').bind('click', function () {
                VocabBrowser.paste('orphanate');
                location.reload();
            });
        } else {
            $(domElement).append('<p id="editicons">' + add + del + cut + paste + '</p>');
            $('#icon-add').bind('click', function () {
                $.get(VocabBrowser.conceptUri(node.id,'new'), function (data) {
                    $('#inner-details').prepend(data);
                    $("#inner-details input[type='text']:first").focus();
                });
            });
            $('#icon-delete').bind('click', function () {
                $.get(VocabBrowser.conceptUri(node.id,'delete'), function (data) {
                    $('#inner-details').prepend(data);
                });
            });
            $('#icon-cut').bind('click', function () {
                $.cookie("cut", null);
                $.cookie("cut", node.id);
                $(this).css('opacity', '0.3');
            });
            $('#icon-paste').bind('click', function () {
                VocabBrowser.paste(node.id);
                location.reload();
            });
        }
        $('#editicons').show();
    },
    paste: function (node_id) {
        var child = $.cookie("cut");
        $.post(VocabBrowser.conceptUri(child,'adopt'), { mother: node_id, save: "Save" });
    },
    hideIcons: function (domElement, node) {
        $(domElement).html(node.name);
    },
    conceptUri: function(nodeId, action) {
        return '/vocabularies/' + VocabBrowser.id(VocabBrowser.toproot) + '/' + nodeId + '/' + action;
    },
}
    
$(function(){
    $.cookie("cut", null);
    VocabBrowser.init();
    $('.cancel').live('click', function(){
        $(this).parents('form:first').remove();
    });
});
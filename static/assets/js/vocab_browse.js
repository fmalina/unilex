function Id(cssid){
    return document.getElementById(cssid);
}

function fill(cssid, data){
    // data has to be server side escaped
    Id(cssid).innerHTML = data;
}

var VB = {
    root: null,
    toproot: null,
    init: function () {
        $.get(location.pathname + '.json', VB.initTree, 'json');
    },
    id: function(id) {
        return id.replace('v-', '');
    },
    initTree: function (json) {
        VB.root = json.id;
        VB.toproot = json.id;
        var infovis = Id('infovis');
        var w = infovis.offsetWidth, h = infovis.offsetHeight;
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
            onCreateLabel: function (el, node){ // Change node styles when labels are placed or moved.
                el.textContent = node.name;
                if(node.data.type == 'vocab'){
                    el.classList.add('vocabnode');
                }
                if(json.queries){
                    if(node.data.query != ''){
                        el.classList.add('has_query');
                    }
                }
                $(el).bind('click', function () { VB.go(node.id); });
            },
            onPlaceLabel: function(el, node){
                var style = el.style;
                var current = node.id == VB.root;
                for (var i = 0; i < 6; i++ ) {
                    $(el).toggleClass('node-depth-' + i, node._depth == i);
                }
                style.display = '';
                if (node.data.type == 'concept') {
                    if(node._depth > 2) {
                        style.display = 'none';
                    }
                }
                if (current) {
                    VB.showIcons(el, node);
                } else {
                    VB.hideIcons(el, node);
                }
                style.zIndex = 100 - node._depth;
                var left = parseInt(style.left);
                var w = el.offsetWidth;
                var h = el.offsetHeight;
                style.left = left - (w / 2) + 'px';
                style.top = parseInt(style.top) - (h * 1.25) + 'px';
            },
            onAfterCompute: function(){
                var node = VB.rootNode();
                if (node && node.id.indexOf("v-") == -1){
                    $.get(VB.conceptUri(node.id,'edit'), function (data) {
                        fill('editing', data);
                        document.title = document.title.split(':')[0] + ': ' + node.name;
                        flexi();
                        acFormset('/tree/autocomplete',
                            document.querySelector('.set').id);
                    });
                } else {
                    $.get('/tree/' + VB.id(VB.root) + '/edit', function (data) {
                        fill('editing', data);
                        flexi();
                    });
                }
            }
        });
        // load JSON data.
        ht.loadJSON(json);
        // compute positions and plot.
        ht.refresh();
        ht.controller.onAfterCompute();
        VB.ht = ht;
        setInterval(VB.check_fragment, 100);
    },
    rootNode: function () {
        if (VB.ht) {
            return VB.ht.graph.getNode(VB.root);
        }
    },
    go: function (id) {
        if (VB.root == id) return;
        VB.ht.onClick(id);
        location.hash = 'c-' + id;
        VB.last_fragment = location.hash;
        VB.root = id;
    },
    last_fragment: null,
    check_fragment: function () {
        var fragment = location.hash;
        if (fragment != VB.last_fragment) {
            var mo = /c-([a-z0-9-]+)/.exec(fragment);
            if (mo)
                VB.go(mo[1]);
            VB.last_fragment = fragment;
            // redirect to right context when logging in
            // $('#loginlink').attr('href', this.href + location.hash);
        }
    },
    addBox: function (data) {
        fill('action', data);
        document.querySelector("#action #id_name").focus();
    },
    showIcons: function (el, node) {
        $('#editicons').remove();
        var del   = '<i class="icon-delete"  title="Delete"   id="icon-delete" ><b>×</b></i>';
        var cut   = '<i class="icon-cut"     title="Cut out"  id="icon-cut"    ></i>';
        var paste = '<i class="icon-put"     title="Put in"   id="icon-paste"  ></i>';
        var add   = '<i class="icon-add"     title="Add"      id="icon-add"    ><b>+</b></i>';
        var edit  = '<i class="icon-edit"    title="Edit"     id="icon-edit"   ></i>';
        var save  = '<i class="icon-save"    title="Download" id="icon-save"   ></i>';
        if (node.data.type == 'vocab') {
            $(el).append('<p id="editicons">' + save + add + del + paste + '</p>');
            $('#icon-save').bind('click', function () {
                location.href = location.pathname + '.xml';
            });
            nid = VB.id(node.id);
            $('#icon-add').bind('click', function () {
                $.get('/tree/' + nid + '/new', VB.addBox);
            });
            $('#icon-delete').bind('click', function () {
                $.get('/tree/' + nid + '/delete', function (data) {
                    fill('action', data);
                });
            });
            $('#icon-paste').bind('click', function (e) {
                VB.paste('direct_to_parent_vocab');
                e.preventDefault();
            });
        } else {
            $(el).append('<p id="editicons">' + add + del + cut + paste + '</p>');
            $('#icon-add').bind('click', function () {
                $.get(VB.conceptUri(node.id, 'new'), VB.addBox);
            });
            $('#icon-delete').bind('click', function () {
                $.get(VB.conceptUri(node.id, 'delete'), function (data) {
                    fill('action', data);
                });
            });
            $('#icon-cut').bind('click', function () {
                localStorage.removeItem("cut");
                localStorage.setItem("cut", VB.id(VB.toproot) + ':' + node.id);
                $(this).css('opacity', '0.3');
            });
            $('#icon-paste').bind('click', function (e) {
                VB.paste(node.id);
                e.preventDefault();
            });
        }
        $('#editicons').show();
    },
    paste: function (nodeId) {
        $.post('/tree/adopt', {
            child: localStorage.getItem("cut"),
            parent: VB.id(VB.toproot) + ':' + nodeId,
            csrfmiddlewaretoken:
                document.getElementsByName('csrfmiddlewaretoken')[0].value
        }).done(function() {
            location.reload();
        });
    },
    hideIcons: function (el, node) {
        $(el).html(node.name);
    },
    conceptUri: function(nodeId, action) {
        return '/tree/' + VB.id(VB.toproot) + '/' + nodeId + '/' + action;
    },
}

function flexi(){
    // flexible height description
    var textarea = Id("id_description");
    if (textarea){
        textarea.style.height = (textarea.scrollHeight + 5) + "px";
        textarea.oninput = function() {
            textarea.style.height = ""; /* Reset the height*/
            textarea.style.height = (textarea.scrollHeight + 5) + "px";
        };
    }
}

function setView(view) {
    Id('list').className = view;
    Id('main').className = view + 'view';
    // init cards
    var masonry = new MiniMasonry({ container: '.L1-wrap' });
    if (view == 'card') {
        masonry.layout();
    } else {
        masonry.destroy();
    }
}

$(function(){
    VB.init();
    $(document).on('click', '.cancel', function(){
        $(this).parents('form:first').remove();
    });
    // Switch view dropdown
    var ul = $('.drop-nav ul');
    $('.drop-nav__head').on('click', function(e) {
        ul.toggle();
        e.stopPropagation();
    });
    $('.content').on('click', function() {
        if (ul.is(':visible')) {
            ul.hide();
        }
    });

    var initView = window.location.hash.replace('#view-', '');
    var views = ['tree', 'card', 'list', 'tabs'];
    if (views.includes(initView)) { setView(initView) };
    $(".view_on").click(function (e) {
        $(".view_on").removeClass('text-muted');
        $(this).addClass('text-muted');
        setView(e.target.dataset.view);
    });

    $('.sort').sortable({
        placeholder: 'placeholder',
        forcePlaceholderSize: true,
        update: function(){
            var data = $(this).sortable('serialize');
            var csrf = 'csrfmiddlewaretoken';
            data += `&${csrf}=${document.getElementsByName(csrf)[0].value}`;
            $.ajax({
                type: 'POST',
                data: data,
                url: Id('list').dataset.submit,
                success: function(){
                    $(this).addClass('done');
                    // TODO re-key the li IDs instead of reload
                    // window.location.reload(); 
                }
            });
        }
    });
});

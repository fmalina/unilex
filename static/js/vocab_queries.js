$.fn.extend({
    insertAtCaret: function(myValue){
      this.each(function(i) {
        if (document.selection) {
          this.focus();
          sel = document.selection.createRange();
          sel.text = myValue;
          this.focus();
        }
        else if (this.selectionStart || this.selectionStart == '0') {
          var startPos = this.selectionStart;
          var endPos = this.selectionEnd;
          var scrollTop = this.scrollTop;
          this.value = this.value.substring(0, startPos)+myValue+this.value.substring(endPos,this.value.length);
          this.focus();
          this.selectionStart = startPos + myValue.length;
          this.selectionEnd = startPos + myValue.length;
          this.scrollTop = scrollTop;
        } else {
          this.value += myValue;
          this.focus();
        }
      })
    }
});

$(function(){
    $('.test').click(function(){
		$(this).text(' loading ...');
        query = $('#id_query').val();
        $.post("/tag/query", { query: query },
            function(data){
                $('#results').slideDown();
                $('#results').html(data);
				$('.test').text('Ready, Test again');
            });
    });
    function add_operator(){
        $('#id_query').insertAtCaret(' ' + $('#operators').val() + ' ');
    }
    $('#operators').change(function(){
        add_operator();
    });
    $('#queries .add').bind('click', function(){
        $('#id_query').insertAtCaret(' ' + $(this).attr('title') + ' ');
    });
    $('#add_operator').click(function(){
        add_operator();
    });
});
function $e(Id){ return document.getElementById(Id);}


var AC = {
	ls: [],
	call_server: function(url, q){
		var xhr = new XMLHttpRequest();
		xhr.open('GET', url+'?'+q, true);
		xhr.onreadystatechange = function(){
			if(xhr.readyState==4){
				var ac = $e('ac');
				ac.style.display = "block";
				ac.innerHTML = xhr.responseText;
			}
		}
		xhr.send();
	},
	placeholderSupported: function(){
		var input = document.createElement('input');
		return ('placeholder' in input);
	},
	placeholder: function(el){
		var box = el,
		msg = box.getAttribute('placeholder');
		box.value = msg;
		box.onfocus = function(){
			if(box.value == msg){ box.value = ''; }
		};
		box.onblur = function(){
			if(box.value == ''){ box.value = msg; }
		};
	},
	predict: function(){
		var q = $e('q');
		var ix = AC.ls.length;
		AC.ls[ix] = {hasFocus: true, keyupcount: 0};
		q.onkeyup = function(){
			AC.ls[ix].keyupcount++;
			var check = function(){ AC.status(ix, 'focused') };
			setTimeout(check, 500);
		};
		q.onfocus = function(){
			AC.ls[ix].hasFocus = true;
			AC.status(ix, 'focused');
		};
		q.onblur = function(){
			AC.ls[ix].hasFocus = false;
			var check = function(){ AC.status(ix, 'blur') };
			setTimeout(check, 200);
		};
		if(!AC.placeholderSupported()){
			AC.placeholder(q);
		}
	},
	status: function(ix, e){
		if (e == 'focused') {
			if (AC.ls[ix].keyupcount < 1) {
				AC.ls[ix].keyupcount = 1;
			}
			if (AC.ls[ix].keyupcount == 1) {
				var q = escape(document.forms['ac_enabled'].q.value);
				if(q){
					AC.call_server('/autocomplete', 'q='+q );
				}
			}
			AC.ls[ix].keyupcount--;
		} else if (e == 'blur') {
			if (!AC.ls[ix].hasFocus) {
				$e('ac').style.display="none";
			}
		}
	}
};
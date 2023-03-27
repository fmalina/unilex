function Id(Id){ return document.getElementById(Id);}

var AC = {
	ls: [],
	call_server: function(url, q) {
		fetch(`${url}?${q}`)
		  .then(response => response.text())
		  .then(text => {
			var ac = Id('ac');
			ac.style.display = "block";
			ac.innerHTML = text;
		  });
	},
	predict: function(){
		var q = Id('q');
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
				Id('ac').style.display="none";
			}
		}
	}
};
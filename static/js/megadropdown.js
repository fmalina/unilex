$(document).ready(function(){
	function addMega(){
		$(this).addClass("hovering");
	}
	function removeMega(){
		$(this).removeClass("hovering");
	}
	var megaConfig = {
		interval: 100,
		sensitivity: 4,
		over: addMega,
		timeout: 500,
		out: removeMega
	};
	$("li.mega").hoverIntent(megaConfig);

	$("#mega .level2-wrap").each(function(){
	    var parent_pos = $(this).parent().position();
	    var pos = 0 - parseInt(parent_pos.left);
	    var pos_px =  pos.toString() + 'px';
	    $(this).css({'left': pos_px});
	});
	
    /* TODO
    Automate menu widths:
    We have 5 columns, each 20%.
    For each 3nd level that has children, add 20% up to 100%. */
});

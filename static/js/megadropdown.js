$(function(){
	function addMega(){$(this).addClass("hovering");}
	function  rmMega(){$(this).removeClass("hovering");}
	$("#mega > li").hoverIntent(addMega, rmMega);
	$("#mega .level2-wrap").each(function(){
		var pos = $(this).parent().position().left;
		//var p_w = $(this).parent().width();
		//var width = $(this).width();
		var pos_px =  pos.toString() + 'px';
		$(this).css({'left': pos_px});
	});
});
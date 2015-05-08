function feedback(){
	var a = $("#feedback_message").val();
	if(a){
		$("#feedback_status").show();
		$("#feedback_status").html("Sending...");
		$("#feedback_submit button").attr("disabled", "disabled").addClass("disabled").removeClass("default").blur();
		$.ajax({
			type: "POST", url: "/feedback", data: {
				feedback_message: a,
				feedback_email: $("#feedback_email").val()
			}
			, error: function(b, d, c) {
			   $("#feedback_status").html("Whoops! We're experiencing some technical hiccups. If you're not too frustrated by this, please e-mail us at vizualbod@vizualbod.com instead.")}
			, success: function(b, c) {
			   $("#feedback_status").html("Success! Thanks for taking the time to write.")}
		})
	}
}

$(function(){
	var b = $("#feedback_message");
	var a = b.val();
	b.click(function() {
		if($(this).val() == a){
			$(this).removeClass("placeholder").val('');
			$("#feedback_submit").show();
		}
	});

	$("form#feedback").submit(function(){
		feedback(); return false;
	});
});
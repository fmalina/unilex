function Id(Id){ return document.getElementById(Id);}

function feedback() {
	var a = Id('feedback_message').value;
    const status = Id('feedback_status');
	if (a) {
		status.style.display = 'block';
		status.textContent = 'Sending...';
		var data = new URLSearchParams();
		data.append('feedback_message', a);
		if(Id("feedback_email")){
			data.append('feedback_email', Id("feedback_email").value);
		}
		data.append('csrfmiddlewaretoken', document.getElementsByName('csrfmiddlewaretoken')[0].value);
		fetch('/feedback', {
			method: 'POST',
			headers: {"Content-Type": "application/x-www-form-urlencoded"},
			body: data
		})
		.then(function(response) {
			var msg = response.ok ? 'Success! Thanks for taking the time to write.' :
			"Whoops! There were some technical hiccups. If you're not too frustrated by this, please e-mail hi@unilexicon.com";
			status.textContent = msg;
		});
	}
}
  
function initFeedbackForm() {
	const b = Id('feedback_message');

	b.addEventListener('click', function() {
		Id('feedback_submit').style.display = 'block';
	});

	Id('feedback_submit').addEventListener('click', function(event){
		feedback();
		event.preventDefault();
	});
}

document.addEventListener('DOMContentLoaded', initFeedbackForm);

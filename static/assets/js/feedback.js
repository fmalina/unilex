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

var feedback_text = `<p>How can we make this website better?
<span id="feedback_status"></span></p>
<p><small>You can also discuss
<a href="https://github.com/fmalina/unilex/issues">known issues on Github</a>
or email <u>hi@unilexicon.com</u></small></p>
<textarea name="feedback_message" id="feedback_message" rows="3" cols="80"
placeholder="Send us your suggestions, love letters. Tell us about issues&hellip;">
</textarea>`;

function initFeedbackForm() {
	const b = Id('open_feedback');
	Id('feedback_text').innerHTML = feedback_text;
	b.addEventListener('click', function(event) {
		event.preventDefault();
		Id('feedback').classList.toggle('open');
		Id('feedback_message').focus();
	});

	Id('feedback_submit').addEventListener('click', function(event){
		feedback();
		event.preventDefault();
	});
}

document.addEventListener('DOMContentLoaded', initFeedbackForm);

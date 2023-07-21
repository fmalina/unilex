function initTranslitForm() {
	const swap = Id('swap');
	swap.addEventListener('click', function(event) {
		event.preventDefault();
        var form = document.forms['translit'];
        var a = form.inp.value;
        var b = form.out.value;
        form.inp.value = b;
        form.out.value = a;
	});
}

document.addEventListener('DOMContentLoaded', initTranslitForm);

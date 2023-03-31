function setCookie(cname, cvalue, exdays) {
	const d = new Date();
	d.setTime(d.getTime() + (exdays*24*60*60*1000));
	let expires = "expires="+ d.toUTCString();
	document.cookie = cname + "=" + cvalue + ";" + expires + ";path=/";
}

function deleteCookie(cname) {
	const d = new Date();
	d.setTime(d.getTime() + (24*60*60*1000));
	let expires = "expires="+ d.toUTCString();
	document.cookie = cname + "=;" + expires + ";path=/";
}

function getCookie(cname) {
	let name = cname + "=";
	let decodedCookie = decodeURIComponent(document.cookie);
	let ca = decodedCookie.split(';');
	for(let i = 0; i <ca.length; i++) {
		let c = ca[i];
		while (c.charAt(0) == ' ') {
			c = c.substring(1);
		}
		if (c.indexOf(name) == 0) {
			return c.substring(name.length, c.length);
		}
	}
	return "";
}

function acceptCookieConsent(){
	deleteCookie('cookie_consent');
	setCookie('cookie_consent', 1, 30);
	document.getElementById("cookie-consent").style.display = "none";
}
const cc = document.getElementById("cookie-consent");
//const acc = document.getElementById("accepted");

// Set visibility of the cookie consent popup
let cookie_consent = getCookie("cookie_consent");
if(cookie_consent != ""){
	cc.style.display = "none";
}else{
	cc.style.display = "block";
    cc.innerHTML += `
	<p>This website uses cookies to enhance your browsing experience and
	  provide personalized advertising.
	  By continuing to use our website, you agree to our
	  <a href="https://blocl.uk/privacy" target="_blank">Privacy Policy</a></p>
	<div><button onclick="acceptCookieConsent();">I agree</button></div>
	<link rel="stylesheet" href="/assets/css/cookies.css">
  `;
	//acc.style.display = "none";
}

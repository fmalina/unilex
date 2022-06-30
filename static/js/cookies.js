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
const ccc = `
  <p>This website uses cookies to enhance your browsing experience and
    provide personalized advertising.
    By continuing to use our website, you agree to our
    <a href="https://blocl.uk/privacy" target="_blank">Privacy Policy</a></p>
  <div><button onclick="acceptCookieConsent();">I agree</button></div>
  <style>
  #cookie-consent{right:30px;bottom:30px;max-width:395px;background:white;border:1px solid #f3f3f3;
      box-sizing:border-box;position:fixed;padding:20px;border-radius:10px;
      box-shadow:0 6px 6px rgb(0 0 0 / 25%);font-family:inherit;z-index:999}
  #cookie-consent *{margin:0;padding:0;text-decoration:none;list-style:none;box-sizing:border-box}
  #cookie-consent p{color:#393d4d;font-size:14px;margin-bottom:20px}
  #cookie-consent button{display:block;width:100%;padding:7px;margin:0;
      font-family:inherit;font-size:16px;
      cursor:pointer;outline:0;border:0;
      color:white;background:#115cfa;border-radius:10px;}
  #cookie-consent button:hover{box-shadow:0 2px 5px 0 rgb(0 0 0 / 30%)}
  </style>
`;

// Set visibility of the cookie consent popup
let cookie_consent = getCookie("cookie_consent");
if(cookie_consent != ""){
	cc.style.display = "none";
}else{
	cc.style.display = "block";
    cc.innerHTML += ccc;
	//acc.style.display = "none";
}

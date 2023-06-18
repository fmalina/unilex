var tc_str = 'gdpr_consent';

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

function Id(Id){ return document.getElementById(Id); }

function acceptCookieConsent(){
	deleteCookie('cookie_consent');
	deleteCookie(tc_str);
	setCookie(tc_str, 1, 30);
	Id("cookie-consent").style.display = "none";
}

function initCookieConsent() {
	const cc = Id("cookie-consent");

	// Set visibility of the cookie consent popup
	let cookie_consent = getCookie(tc_str);
	if(cookie_consent != ""){
		cc.style.display = "none";
	} else {
		cc.style.display = "block";
	    const p = document.createElement("p");
        p.textContent = `This website uses cookies to enhance your browsing
        experience and provide personalized advertising.
        By continuing to use our website, you agree to our `;

        const privacy = document.createElement("a");
        privacy.href = "https://blocl.uk/privacy";
        privacy.target = "_blank";
        privacy.textContent = "privacy policy";
        p.appendChild(privacy);

        const consentButton = document.createElement("button");
        consentButton.id = "consent_button";
        consentButton.textContent = "I agree";
        const div = document.createElement("div");
        div.appendChild(consentButton);
        cc.appendChild(p);
        cc.appendChild(div);

        const head = document.querySelector("head");
        const link = document.createElement("link");
        link.rel = "stylesheet";
        link.href = "/assets/css/cookies.css";
        head.appendChild(link);
	}

	const cc_btn = Id('consent_button');
	if(cc_btn){
        cc_btn.addEventListener('click', function() {
            acceptCookieConsent();
        });
	}
}

document.addEventListener('DOMContentLoaded', initCookieConsent);
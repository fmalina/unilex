// Google AdSense
var s = document.createElement('script');
s.src = 'https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js';
s.async = true;
document.head.appendChild(s);

(adsbygoogle = window.adsbygoogle || []).push({
    google_ad_client: "ca-pub-7258089185308476",
    enable_page_level_ads: true
});

// Ad blocking recovery
var s1 = document.createElement('script');
s1.async = true;
s1.src = "https://fundingchoicesmessages.google.com/i/pub-7258089185308476?ers=1";
(function() {
    function signalGooglefcPresent() {
        if (!window.frames['googlefcPresent']) {
            if (document.body) {
                const iframe = document.createElement('iframe');
                iframe.style = 'width:0;height:0;border:none;z-index:-1000;left:-1000px;top:-1000px;';
                iframe.style.display = 'none';
                iframe.name = 'googlefcPresent';
                document.body.appendChild(iframe);
            } else {
                setTimeout(signalGooglefcPresent, 0);
            }
        }
    }
    signalGooglefcPresent();
})();

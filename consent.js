(() => {
  const STORAGE_KEY = "fileflip_analytics_consent_v1";
  const GA_ID = "G-1FL2CWNTS6";

  function loadAnalytics() {
    if (window.__fileflipAnalyticsLoaded) return;
    window.__fileflipAnalyticsLoaded = true;
    window.dataLayer = window.dataLayer || [];
    function gtag(){ window.dataLayer.push(arguments); }
    window.gtag = gtag;
    gtag("js", new Date());
    gtag("config", GA_ID);
    const script = document.createElement("script");
    script.async = true;
    script.src = "https://www.googletagmanager.com/gtag/js?id=" + encodeURIComponent(GA_ID);
    document.head.appendChild(script);
  }

  function buildConsentUi() {
    if (document.getElementById("fileflip-consent-banner")) return;
    const style = document.createElement("style");
    style.textContent = `
      #fileflip-consent-banner{position:fixed;z-index:99999;left:16px;right:16px;bottom:16px;max-width:720px;margin:auto;background:#fff;color:#17233e;border:1px solid #dfe4ef;border-radius:16px;box-shadow:0 12px 40px #101b3630;padding:18px;font:14px/1.55 Arial,sans-serif}
      #fileflip-consent-banner p{margin:0 0 12px}
      #fileflip-consent-banner a{color:#5142c8}
      #fileflip-consent-banner .ff-actions{display:flex;gap:9px;flex-wrap:wrap}
      #fileflip-consent-banner button,#fileflip-cookie-settings{border:0;border-radius:9px;padding:10px 15px;font-weight:700;cursor:pointer}
      #fileflip-consent-banner button{background:#5142c8;color:#fff}
      #fileflip-consent-banner button[data-choice="reject"]{background:#eef0f6;color:#17233e}
      #fileflip-cookie-settings{position:fixed;z-index:99998;left:12px;bottom:12px;background:#eef0f6;color:#17233e;border:1px solid #dfe4ef;font:12px Arial,sans-serif;box-shadow:0 2px 8px #0002}
      @media(max-width:480px){#fileflip-consent-banner{left:8px;right:8px;bottom:8px;padding:15px}#fileflip-cookie-settings{bottom:8px}}
    `;
    document.head.appendChild(style);

    const settings = document.createElement("button");
    settings.id = "fileflip-cookie-settings";
    settings.type = "button";
    settings.textContent = "Cookie settings";
    settings.addEventListener("click", showBanner);
    document.body.appendChild(settings);

    function showBanner() {
      let banner = document.getElementById("fileflip-consent-banner");
      if (!banner) {
        banner = document.createElement("section");
        banner.id = "fileflip-consent-banner";
        banner.setAttribute("role", "dialog");
        banner.setAttribute("aria-label", "Cookie and analytics choices");
        banner.innerHTML = '<p><strong>Your privacy choices</strong><br>FileFlip uses Google Analytics only if you choose to accept analytics. If you reject, analytics will remain off. You can change your choice at any time. Read our <a href="/privacy-policy">Privacy Policy</a> and <a href="/cookie-policy">Cookie Policy</a>.</p><div class="ff-actions"><button type="button" data-choice="accept">Accept analytics</button><button type="button" data-choice="reject">Reject analytics</button></div>';
        banner.addEventListener("click", event => {
          const choice = event.target && event.target.getAttribute("data-choice");
          if (!choice) return;
          try { localStorage.setItem(STORAGE_KEY, choice); } catch (_) {}
          banner.remove();
          if (choice === "accept") loadAnalytics();
        });
        document.body.appendChild(banner);
      }
    }

    let saved = null;
    try { saved = localStorage.getItem(STORAGE_KEY); } catch (_) {}
    if (saved === "accept") loadAnalytics();
    if (saved !== "accept" && saved !== "reject") showBanner();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", buildConsentUi, { once: true });
  } else {
    buildConsentUi();
  }
})();
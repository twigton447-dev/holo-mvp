(function () {
  var config = {
    goatcounterUrl: "https://holoengine.goatcounter.com/count",
    gaMeasurementId: "G-WMMFBGFND8",
    clarityProjectId: "",
  };

  function addScript(src, attrs) {
    if (document.querySelector('script[src="' + src + '"]')) return;
    var script = document.createElement("script");
    script.async = true;
    script.src = src;
    Object.keys(attrs || {}).forEach(function (key) {
      script.setAttribute(key, attrs[key]);
    });
    document.head.appendChild(script);
  }

  function loadGoatCounter() {
    if (!config.goatcounterUrl || document.querySelector("script[data-goatcounter]")) return;
    addScript("https://gc.zgo.at/count.js", {
      "data-goatcounter": config.goatcounterUrl,
    });
  }

  function loadGoogleAnalytics() {
    if (!config.gaMeasurementId || window.__holoGaLoaded) return;
    window.__holoGaLoaded = true;
    window.dataLayer = window.dataLayer || [];
    window.gtag = window.gtag || function () {
      window.dataLayer.push(arguments);
    };
    window.gtag("js", new Date());
    window.gtag("config", config.gaMeasurementId);
    addScript("https://www.googletagmanager.com/gtag/js?id=" + config.gaMeasurementId);
  }

  function loadClarity() {
    var meta = document.querySelector('meta[name="holo:clarity-id"]');
    var clarityId = (meta && meta.content ? meta.content : config.clarityProjectId).trim();
    if (!clarityId || clarityId === "CLARITY_PROJECT_ID" || window.clarity) return;
    (function (c, l, a, r, i, t, y) {
      c[a] = c[a] || function () {
        (c[a].q = c[a].q || []).push(arguments);
      };
      t = l.createElement(r);
      t.async = 1;
      t.src = "https://www.clarity.ms/tag/" + i;
      y = l.getElementsByTagName(r)[0];
      y.parentNode.insertBefore(t, y);
    })(window, document, "clarity", "script", clarityId);
  }

  loadGoatCounter();
  loadGoogleAnalytics();
  loadClarity();
})();

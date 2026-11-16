// Branch switcher for the multi-branch documentation site.
//
// Site layout produced by docs/build_site.py:
//   <site root>/branches.json      [{branch, label, banner?}, ...]
//   <site root>/<branch>/...       Sphinx HTML build of that branch
//
// The script finds the current branch from the page URL, fills the sidebar
// <select>, keeps the current page when switching (falls back to the branch
// index if the page does not exist there) and shows an optional banner.
(function () {
  "use strict";

  function contentRoot() {
    // Sphinx >= 7.2 exposes the build root relative to the current page.
    var rel = document.documentElement.dataset.content_root ||
      (window.DOCUMENTATION_OPTIONS && DOCUMENTATION_OPTIONS.URL_ROOT) || "./";
    return new URL(rel, window.location.href);
  }

  function showBanner(text) {
    var banner = document.createElement("div");
    banner.className = "branch-banner";
    banner.setAttribute("role", "note");
    banner.textContent = text;
    var content = document.querySelector(".wy-nav-content") || document.body;
    content.insertBefore(banner, content.firstChild);
  }

  function init() {
    var box = document.getElementById("branch-switcher");
    var select = document.getElementById("branch-switcher-select");
    if (!box || !select) return;

    var branchRoot = contentRoot();                // .../<branch>/
    var siteRoot = new URL("../", branchRoot);     // .../
    var current = decodeURIComponent(
      branchRoot.pathname.replace(/\/$/, "").split("/").pop());
    var pagePath = window.location.pathname.slice(branchRoot.pathname.length);

    fetch(new URL("branches.json", siteRoot), { cache: "no-cache" })
      .then(function (r) { if (!r.ok) throw new Error(r.status); return r.json(); })
      .then(function (branches) {
        var found = false;
        branches.forEach(function (b) {
          var opt = document.createElement("option");
          opt.value = b.branch;
          opt.textContent = b.label || b.branch;
          if (b.branch === current) {
            opt.selected = true;
            found = true;
            if (b.banner) showBanner(b.banner);
          }
          select.appendChild(opt);
        });
        if (!found) return;   // page not served from a known branch folder
        box.hidden = false;

        select.addEventListener("change", function () {
          var target = new URL(encodeURIComponent(select.value) + "/", siteRoot);
          var samePage = new URL(pagePath + window.location.hash, target);
          fetch(samePage, { method: "HEAD" })
            .then(function (r) { window.location.href = r.ok ? samePage : target; })
            .catch(function () { window.location.href = target; });
        });
      })
      .catch(function () { /* local build: no branches.json, keep hidden */ });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();

(function () {
  var progress = document.getElementById("scroll-progress");
  var header = document.querySelector(".site-header");
  var toggle = document.querySelector(".nav-toggle");

  function updateProgress() {
    var root = document.documentElement;
    var distance = root.scrollHeight - root.clientHeight;
    if (progress) {
      progress.style.width = (distance > 0 ? (root.scrollTop / distance) * 100 : 0) + "%";
    }
  }

  window.addEventListener("scroll", updateProgress, { passive: true });
  updateProgress();

  if (!header || !toggle) {
    return;
  }

  toggle.addEventListener("click", function () {
    var open = header.classList.toggle("nav-open");
    toggle.setAttribute("aria-expanded", String(open));
    toggle.setAttribute("aria-label", open ? "Close navigation" : "Open navigation");
  });

  document.querySelectorAll("#main-nav a").forEach(function (link) {
    link.addEventListener("click", function () {
      header.classList.remove("nav-open");
      toggle.setAttribute("aria-expanded", "false");
      toggle.setAttribute("aria-label", "Open navigation");
    });
  });
})();

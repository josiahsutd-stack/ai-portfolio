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

  function fallbackCopy(text) {
    return new Promise(function (resolve, reject) {
      var field = document.createElement("textarea");
      field.value = text;
      field.setAttribute("readonly", "");
      field.style.position = "fixed";
      field.style.opacity = "0";
      document.body.appendChild(field);
      field.select();
      try {
        if (!document.execCommand("copy")) {
          throw new Error("Copy command was rejected");
        }
        resolve();
      } catch (error) {
        reject(error);
      } finally {
        field.remove();
      }
    });
  }

  function writeCommand(text) {
    if (navigator.clipboard && window.isSecureContext) {
      return navigator.clipboard.writeText(text);
    }
    return fallbackCopy(text);
  }

  document.querySelectorAll("code[data-copy-command]").forEach(function (code) {
    var wrapper = document.createElement("div");
    var button = document.createElement("button");
    var status = document.createElement("span");

    wrapper.className = "command-copy";
    code.parentNode.insertBefore(wrapper, code);
    wrapper.appendChild(code);

    button.className = "copy-command";
    button.type = "button";
    button.textContent = "Copy";
    button.setAttribute("data-copy-button", "");
    button.setAttribute("aria-label", "Copy command");
    wrapper.appendChild(button);

    status.className = "copy-status";
    status.setAttribute("aria-live", "polite");
    status.setAttribute("aria-atomic", "true");
    wrapper.appendChild(status);

    button.addEventListener("click", function () {
      var command = code.textContent.trim();
      button.disabled = true;
      writeCommand(command)
        .then(function () {
          button.textContent = "Copied";
          button.setAttribute("data-state", "success");
          status.textContent = "Command copied to clipboard.";
        })
        .catch(function () {
          button.textContent = "Copy failed";
          button.setAttribute("data-state", "error");
          status.textContent = "Copy failed. Select the command text manually.";
        })
        .finally(function () {
          window.setTimeout(function () {
            button.textContent = "Copy";
            button.removeAttribute("data-state");
            button.disabled = false;
            status.textContent = "";
          }, 1800);
        });
    });
  });

  if (!header || !toggle) {
    return;
  }

  function closeNavigation(restoreFocus) {
    header.classList.remove("nav-open");
    toggle.setAttribute("aria-expanded", "false");
    toggle.setAttribute("aria-label", "Open navigation");
    if (restoreFocus) {
      toggle.focus();
    }
  }

  toggle.addEventListener("click", function () {
    var open = header.classList.toggle("nav-open");
    toggle.setAttribute("aria-expanded", String(open));
    toggle.setAttribute("aria-label", open ? "Close navigation" : "Open navigation");
  });

  document.querySelectorAll("#main-nav a").forEach(function (link) {
    link.addEventListener("click", function () {
      closeNavigation(false);
    });
  });

  document.addEventListener("keydown", function (event) {
    if (event.key === "Escape" && header.classList.contains("nav-open")) {
      closeNavigation(true);
    }
  });

  window.addEventListener("resize", function () {
    if (window.innerWidth > 680 && header.classList.contains("nav-open")) {
      closeNavigation(false);
    }
  });
})();

// Header Navigation Behavior
// Scroll effect, mobile nav toggle, and submenu handling for templates/partials/_header.html

(function () {
  var header = document.getElementById('header');
  var navBtn = document.getElementById('nav-toggle');
  var nav    = document.getElementById('nav');

  /* --- Scroll effect --- */
  function onScroll() {
    if (window.scrollY > 10) {
      header.classList.add('is-scrolled');
    } else {
      header.classList.remove('is-scrolled');
    }
  }
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  /* --- Mobile menu toggle (hamburger → X) --- */
  if (navBtn && nav) {
    navBtn.addEventListener('click', function () {
      var open = nav.classList.toggle('is-open');
      navBtn.classList.toggle('is-open', open);
      navBtn.setAttribute('aria-expanded', open);
      navBtn.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
    });
  }

  /* --- Generic submenu handler --- */
  function initSubmenu(triggerId) {
    var trigger = document.getElementById(triggerId);
    if (!trigger) return;
    var li = trigger.closest('.nav-item-has-submenu');

    trigger.addEventListener('click', function (e) {
      e.preventDefault();
      // Close other submenus
      document.querySelectorAll('.nav-item-has-submenu.is-open').forEach(function (el) {
        if (el !== li) {
          el.classList.remove('is-open');
          var t = el.querySelector('[aria-expanded]');
          if (t) t.setAttribute('aria-expanded', 'false');
        }
      });
      var open = li.classList.toggle('is-open');
      trigger.setAttribute('aria-expanded', open);
    });

    document.addEventListener('click', function (e) {
      if (!li.contains(e.target)) {
        li.classList.remove('is-open');
        trigger.setAttribute('aria-expanded', 'false');
      }
    });
  }

  initSubmenu('about-menu-trigger');
  initSubmenu('services-menu-trigger');
  initSubmenu('media-menu-trigger');

  /* --- ESC closes all submenus and mobile menu --- */
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') {
      document.querySelectorAll('.nav-item-has-submenu.is-open').forEach(function (el) {
        el.classList.remove('is-open');
        var t = el.querySelector('[aria-expanded]');
        if (t) { t.setAttribute('aria-expanded', 'false'); t.focus(); }
      });
      if (nav && navBtn) {
        nav.classList.remove('is-open');
        navBtn.classList.remove('is-open');
        navBtn.setAttribute('aria-expanded', 'false');
        navBtn.setAttribute('aria-label', 'Open menu');
      }
    }
  });
})();

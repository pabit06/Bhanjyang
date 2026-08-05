/*
 * CSP-safe event wiring.
 *
 * script-src no longer allows 'unsafe-inline', and a nonce does not cover
 * inline handler attributes (onclick="...", onerror="..."), so the browser
 * blocks them outright. Templates declare intent with data-* attributes and
 * this file attaches the real listeners.
 *
 *   data-action="fn"             click  -> window.fn(...args); dotted paths ok ("obj.method")
 *   data-action-args='[1,"x"]'   JSON array of arguments passed to data-action
 *   data-change-action="fn"      same as data-action, but on the change event
 *   data-trigger-click="#sel"    click  -> click() the element matching #sel
 *   data-scroll-to="#sel"        click  -> smooth-scroll the element matching #sel
 *   data-confirm="msg"           submit -> confirm(msg), cancel the submit on decline
 *   data-fallback="url"          img error -> swap src to url
 *   data-hide-on-error           img error -> hide the element
 *
 * Handlers are delegated from document, so markup injected later (map popups,
 * lazily rendered cards) is wired automatically. Delegation also means only the
 * nearest matching ancestor runs: a data-action button inside a data-action card
 * fires the button's action alone, which is what the old
 * `onclick="event.stopPropagation(); ..."` calls were for.
 */
(function () {
  'use strict';

  function resolve(path) {
    if (!path) return undefined;
    return path.split('.').reduce(function (ctx, key) {
      return ctx == null ? ctx : ctx[key];
    }, window);
  }

  function callAction(name, el) {
    var fn = resolve(name);
    if (typeof fn !== 'function') {
      console.warn('[csp-compat] no such action:', name, el);
      return;
    }

    var args = [];
    var raw = el.getAttribute('data-action-args');
    if (raw) {
      try {
        var parsed = JSON.parse(raw);
        args = Array.isArray(parsed) ? parsed : [parsed];
      } catch (err) {
        console.warn('[csp-compat] invalid data-action-args:', raw, el);
      }
    }

    // Keep `this` on the owner object so dotted paths (obj.method) still work.
    var dot = name.lastIndexOf('.');
    fn.apply(dot === -1 ? window : resolve(name.slice(0, dot)), args);
  }

  function closest(target, selector) {
    return target && target.closest ? target.closest(selector) : null;
  }

  document.addEventListener('click', function (event) {
    var el = closest(event.target, '[data-action], [data-trigger-click], [data-scroll-to]');
    if (!el) return;

    var scrollSelector = el.getAttribute('data-scroll-to');
    if (scrollSelector) {
      var scrollTarget = document.querySelector(scrollSelector);
      if (scrollTarget) scrollTarget.scrollIntoView({ behavior: 'smooth' });
      return;
    }

    var clickSelector = el.getAttribute('data-trigger-click');
    if (clickSelector) {
      var proxy = document.querySelector(clickSelector);
      if (proxy) proxy.click();
      return;
    }

    callAction(el.getAttribute('data-action'), el);
  });

  document.addEventListener('change', function (event) {
    var el = closest(event.target, '[data-change-action]');
    if (el) callAction(el.getAttribute('data-change-action'), el);
  });

  document.addEventListener('submit', function (event) {
    var message = event.target.getAttribute && event.target.getAttribute('data-confirm');
    if (message && !window.confirm(message)) event.preventDefault();
  });

  function handleImageError(img) {
    if (img.hasAttribute('data-hide-on-error')) {
      img.style.display = 'none';
      return;
    }
    var fallback = img.getAttribute('data-fallback');
    if (fallback && img.getAttribute('src') !== fallback) img.src = fallback;
  }

  // error does not bubble, so listen on the capture phase.
  document.addEventListener('error', function (event) {
    if (event.target && event.target.tagName === 'IMG') handleImageError(event.target);
  }, true);

  // This file is deferred, so images that already failed while the document was
  // parsing fired their error event before the listener above existed.
  document.addEventListener('DOMContentLoaded', function () {
    var images = document.querySelectorAll('img[data-fallback], img[data-hide-on-error]');
    Array.prototype.forEach.call(images, function (img) {
      if (img.complete && img.naturalWidth === 0) handleImageError(img);
    });
  });
})();

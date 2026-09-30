/* Behaviour every page shares: the reveal on scroll, the progress line, the nav, the
   phone menu, and the filmstrip's arrows. Loaded with `defer` from each page's <head>.
   It used to be pasted inline into five pages; one copy cannot drift from the others.

   Nothing on the site depends on this file to be readable. The one line in <head> that
   adds the .js class is what switches the reveal on, and it only does so because this
   file is then there to switch each element back to visible. */
(function () {
  var nav = document.querySelector('.site-nav');

  /* ---- Reveal ---------------------------------------------------------------- */
  var reveals = document.querySelectorAll('.reveal');
  if ('IntersectionObserver' in window) {
    var obs = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        // top < 0 catches anything already scrolled past. An anchor such as
        // photographs.html#school-meal jumps straight down the page, and every element
        // above it would otherwise never intersect and stay invisible.
        if (e.isIntersecting || e.boundingClientRect.top < 0) {
          e.target.classList.add('visible');
          obs.unobserve(e.target);
        }
      });
    }, { threshold: 0, rootMargin: '0px 0px -40px 0px' });
    reveals.forEach(function (el) { obs.observe(el); });

    // The anchor jump can land before the observer's first entries do, so everything
    // above the landing point never changes state. Sweep once, after it has settled.
    addEventListener('load', function () {
      reveals.forEach(function (el) {
        if (el.getBoundingClientRect().top < innerHeight) {
          el.classList.add('visible');
          obs.unobserve(el);
        }
      });
    });
  } else {
    reveals.forEach(function (el) { el.classList.add('visible'); });
  }

  /* ---- Progress line and nav state -------------------------------------------- */
  var bar = document.querySelector('.progress');
  var ticking = false;
  function onScroll() {
    ticking = false;
    var max = document.documentElement.scrollHeight - innerHeight;
    if (bar) bar.style.transform = 'scaleX(' + (max > 0 ? Math.min(1, scrollY / max) : 0) + ')';
    if (nav) nav.classList.toggle('scrolled', scrollY > 60);
  }
  addEventListener('scroll', function () {
    if (!ticking) { ticking = true; requestAnimationFrame(onScroll); }
  }, { passive: true });
  onScroll();

  /* ---- Phone menu ---------------------------------------------------------------
     Six links do not fit across a phone. The button is invisible without .js, so this
     is the only thing that can open the panel — there is no CSS-only state to drift out
     of sync with aria-expanded. */
  var toggle = document.querySelector('.nav-toggle');
  var links = document.getElementById('nav-links');
  if (toggle && links) {
    var setMenu = function (open) {
      toggle.setAttribute('aria-expanded', String(open));
      toggle.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
      links.classList.toggle('open', open);
    };
    toggle.addEventListener('click', function () {
      setMenu(toggle.getAttribute('aria-expanded') !== 'true');
    });
    // A same-page anchor does not reload, so the panel would stay open over it.
    links.addEventListener('click', function (e) {
      if (e.target.closest('a')) setMenu(false);
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && toggle.getAttribute('aria-expanded') === 'true') {
        setMenu(false);
        toggle.focus();
      }
    });
    document.addEventListener('click', function (e) {
      if (nav && !nav.contains(e.target)) setMenu(false);
    });
    // Turning a phone to landscape can cross the breakpoint; do not leave a stray panel.
    addEventListener('resize', function () {
      if (innerWidth > 960) setMenu(false);
    }, { passive: true });
  }

  /* ---- Filmstrip arrows ----------------------------------------------------------
     Swiping and trackpads scroll the rail natively. A mouse with only a vertical wheel
     cannot, so a pointer that hovers gets two buttons. site.css hides them on touch. */
  document.querySelectorAll('[data-rail]').forEach(function (controls) {
    var rail = document.getElementById(controls.getAttribute('data-rail'));
    if (!rail) return;
    var prev = controls.querySelector('[data-dir="-1"]');
    var next = controls.querySelector('[data-dir="1"]');
    function update() {
      prev.disabled = rail.scrollLeft <= 2;
      next.disabled = rail.scrollLeft >= rail.scrollWidth - rail.clientWidth - 2;
    }
    var still = matchMedia('(prefers-reduced-motion: reduce)');
    [prev, next].forEach(function (b) {
      b.addEventListener('click', function () {
        rail.scrollBy({ left: +b.getAttribute('data-dir') * rail.clientWidth * 0.8,
                        behavior: still.matches ? 'auto' : 'smooth' });
      });
    });
    rail.addEventListener('scroll', update, { passive: true });
    addEventListener('resize', update, { passive: true });
    controls.hidden = false;
    update();
  });
})();

/* Velvet Steel Barbershop - Main JS */

const navbar = document.getElementById('navbar');
if (navbar) {
  window.addEventListener('scroll', () => {
    navbar.classList.toggle('scrolled', window.scrollY > 60);
  });
}
const navToggle = document.getElementById('navToggle');
const navLinks  = document.getElementById('navLinks');
const mobNavOverlay  = document.getElementById('mobNavOverlay');
const navSidebarClose = document.getElementById('navSidebarClose');
const navDropdownEl  = document.querySelector('.nav-dropdown');

function openNav() {
  if (!navLinks) return;
  navLinks.classList.add('open');
  if (navToggle) navToggle.classList.add('active');
  if (mobNavOverlay) {
    mobNavOverlay.style.display = 'block';
    void mobNavOverlay.offsetWidth;
    mobNavOverlay.classList.add('active');
  }
  document.body.style.overflow = 'hidden';
  if (navToggle) {
    const spans = navToggle.querySelectorAll('span');
    if (spans[0]) spans[0].style.transform = 'rotate(45deg) translate(5px, 5px)';
    if (spans[1]) spans[1].style.opacity = '0';
    if (spans[2]) spans[2].style.transform = 'rotate(-45deg) translate(5px, -5px)';
  }
}

function closeMobileDropdown() {
  if (navDropdownEl) navDropdownEl.classList.remove('open');
}

function closeNav() {
  if (!navLinks) return;
  navLinks.classList.remove('open');
  if (navToggle) navToggle.classList.remove('active');
  if (mobNavOverlay) {
    mobNavOverlay.classList.remove('active');
    setTimeout(() => { if (!mobNavOverlay.classList.contains('active')) mobNavOverlay.style.display = ''; }, 350);
  }
  document.body.style.overflow = '';
  closeMobileDropdown();
  if (navToggle) {
    navToggle.querySelectorAll('span').forEach(s => {
      s.style.transform = '';
      s.style.opacity   = '';
    });
  }
}

if (navToggle) {
  navToggle.addEventListener('click', (e) => {
    e.stopPropagation();
    navLinks && navLinks.classList.contains('open') ? closeNav() : openNav();
  });
}

if (navSidebarClose) {
  navSidebarClose.addEventListener('click', closeNav);
}

if (mobNavOverlay) {
  mobNavOverlay.addEventListener('click', closeNav);
}

if (navLinks) {
  navLinks.querySelectorAll('a').forEach(link => {
    link.addEventListener('click', () => {
      if (window.innerWidth <= 900) closeNav();
    });
  });
}

// close sa ESC
document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape') closeNav();
});

const navUserBtn = document.querySelector('.nav-user');
if (navUserBtn && navDropdownEl) {
  navUserBtn.addEventListener('click', function(e) {
    if (window.innerWidth <= 900) {
      e.preventDefault();
      e.stopPropagation();
      navDropdownEl.classList.toggle('open');
    }
  });
}

document.querySelectorAll('.alert').forEach(alert => {
  setTimeout(() => {
    alert.style.opacity = '0';
    alert.style.transform = 'translateX(20px)';
    setTimeout(() => alert.remove(), 300);
  }, 5000);
});

function animateOnScroll() {
  const elements = document.querySelectorAll('[data-aos]');
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const delay = entry.target.dataset.delay || 0;
        setTimeout(() => {
          entry.target.style.opacity = '1';
          entry.target.style.transform = 'translateY(0)';
        }, parseInt(delay));
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.1 });

  elements.forEach(el => {
    el.style.opacity = '0';
    el.style.transform = 'translateY(24px)';
    el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
    observer.observe(el);
  });
}
animateOnScroll();

document.querySelectorAll('a[href^="#"]').forEach(a => {
  const href = a.getAttribute('href');
  if (!href || href === '#') return;
  a.addEventListener('click', e => {
    try {
      const target = document.querySelector(href);
      if (target) {
        e.preventDefault();
        target.scrollIntoView({ behavior: 'smooth' });
      }
    } catch(err) {}
  });
});

document.querySelectorAll('.btn-gold, .btn-outline').forEach(btn => {
  btn.addEventListener('click', function(e) {
    const ripple = document.createElement('span');
    const rect = this.getBoundingClientRect();
    ripple.style.cssText = `
      position: absolute; border-radius: 50%;
      width: 10px; height: 10px;
      background: rgba(255,255,255,0.3);
      left: ${e.clientX - rect.left - 5}px;
      top: ${e.clientY - rect.top - 5}px;
      transform: scale(0);
      animation: ripple 0.5s linear;
      pointer-events: none;
    `;
    if (!this.style.position) this.style.position = 'relative';
    this.style.overflow = 'hidden';
    this.appendChild(ripple);
    setTimeout(() => ripple.remove(), 500);
  });
});

const rippleStyle = document.createElement('style');
rippleStyle.textContent = '@keyframes ripple { to { transform: scale(30); opacity: 0; } }';
document.head.appendChild(rippleStyle);

const barberSelectEl = document.getElementById('barberSelect');
const barberPreview = document.getElementById('barberPreview');
if (barberSelectEl && barberPreview) {
  barberSelectEl.addEventListener('change', function() {
    const opt = this.options[this.selectedIndex];
    if (this.value && opt) {
      barberPreview.innerHTML = `
        <div style="display:flex;align-items:center;gap:10px;margin-top:8px;padding:10px;background:rgba(200,160,60,0.08);border:1px solid rgba(200,160,60,0.2);border-radius:4px;">
          <i class="fas fa-user-tie" style="color:var(--gold);"></i>
          <span style="font-size:0.83rem;color:var(--text-secondary);">${opt.dataset.specialty || ''}</span>
          ${opt.dataset.rating ? `<span style="margin-left:auto;color:var(--gold);font-size:0.78rem;"><i class="fas fa-star"></i> ${opt.dataset.rating}</span>` : ''}
        </div>
      `;
    } else {
      barberPreview.innerHTML = '';
    }
  });
}

const serviceSelectEl = document.getElementById('serviceSelect');
const servicePreview = document.getElementById('servicePreview');
if (serviceSelectEl && servicePreview) {
  serviceSelectEl.addEventListener('change', function() {
    const opt = this.options[this.selectedIndex];
    if (this.value && opt) {
      servicePreview.innerHTML = `
        <div style="display:flex;align-items:center;justify-content:space-between;margin-top:8px;padding:10px;background:rgba(200,160,60,0.08);border:1px solid rgba(200,160,60,0.2);border-radius:4px;">
          <span style="font-size:0.83rem;color:var(--text-secondary);display:flex;align-items:center;gap:6px;">
            <i class="fas fa-clock" style="color:var(--gold);"></i> ${opt.dataset.duration || ''} min
          </span>
          <span style="color:var(--gold);font-family:'Playfair Display',serif;font-size:1.1rem;font-weight:700;">&#8369;${opt.dataset.price || ''}</span>
        </div>
      `;
    } else {
      servicePreview.innerHTML = '';
    }
  });
}

/* ============================================================
   VS CONFIRM MODAL
   ============================================================ */
(function() {
  var overlay = document.getElementById('vsConfirmModal');
  if (!overlay) return;
  var msgEl = document.getElementById('vsConfirmMsg');
  var cancelBtn = document.querySelector('.vs-confirm-cancel');
  var okBtn = document.querySelector('.vs-confirm-ok');
  var pendingForm = null;
  var pendingCb = null;

  function showModal(msg) {
    if (msgEl) msgEl.textContent = msg;
    overlay.style.display = 'flex';
  }

  function closeModal() {
    overlay.style.display = 'none';
    pendingForm = null;
    pendingCb = null;
  }

  document.addEventListener('submit', function(e) {
    var form = e.target;
    if (!form || !form.hasAttribute('data-confirm')) return;
    e.preventDefault();
    e.stopPropagation();
    pendingForm = form;
    pendingCb = null;
    showModal(form.getAttribute('data-confirm'));
  }, true);

  if (cancelBtn) cancelBtn.addEventListener('click', closeModal);

  if (okBtn) {
    okBtn.addEventListener('click', function() {
      var f = pendingForm;
      var cb = pendingCb;
      closeModal();
      if (f) f.submit();
      if (cb) cb();
    });
  }

  overlay.addEventListener('click', function(e) {
    if (e.target === overlay) closeModal();
  });

  document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape' && overlay.style.display === 'flex') closeModal();
  });

  window.vsConfirm = function(msg, onOk) {
    pendingForm = null;
    pendingCb = onOk || null;
    showModal(msg);
  };
})();

/* ============================================================
   CUSTOM SELECT DROPDOWN
   ============================================================ */
(function() {
  function buildCustomSelect(sel) {
    if (sel.dataset.csInit) return;
    sel.dataset.csInit = '1';

    var wrap = document.createElement('div');
    wrap.className = 'cs-wrap';
    sel.parentNode.insertBefore(wrap, sel);
    wrap.appendChild(sel);
    sel.style.display = 'none';

    var trigger = document.createElement('div');
    trigger.className = 'cs-trigger';
    trigger.setAttribute('tabindex', '0');
    trigger.setAttribute('role', 'combobox');
    trigger.setAttribute('aria-haspopup', 'listbox');
    trigger.setAttribute('aria-expanded', 'false');

    var trigText = document.createElement('span');
    trigText.className = 'cs-trigger-text';

    var arrow = document.createElement('span');
    arrow.className = 'cs-arrow';
    arrow.innerHTML = '<i class="fas fa-chevron-down"></i>';

    trigger.appendChild(trigText);
    trigger.appendChild(arrow);
    wrap.insertBefore(trigger, sel);

    var dropdown = document.createElement('div');
    dropdown.className = 'cs-dropdown';
    dropdown.setAttribute('role', 'listbox');
    wrap.appendChild(dropdown);

    var statusColors = {
      pending: 'rgba(200,160,60,0.5)',
      confirmed: 'rgba(76,175,125,0.5)',
      completed: 'rgba(74,144,200,0.5)',
      cancelled: 'rgba(224,85,85,0.5)',
      no_show: 'rgba(120,100,60,0.5)'
    };
    var statusTextColors = {
      pending: '#c8a03c',
      confirmed: '#4caf7d',
      completed: '#4a90c8',
      cancelled: '#e05555',
      no_show: '#8a6040'
    };

    var isStatus = sel.classList.contains('status-select');
    if (isStatus) {
      wrap.classList.add('cs-compact');
      function updateStatusBorder() {
        trigger.style.borderColor = statusColors[sel.value] || 'rgba(200,160,60,0.3)';
        trigger.style.color = statusTextColors[sel.value] || '';
      }
      sel.addEventListener('change', updateStatusBorder);
      updateStatusBorder();
    }

    function refreshTrigger() {
      var cur = sel.options[sel.selectedIndex];
      if (cur && cur.value !== '') {
        trigText.textContent = cur.textContent.trim();
        if (!isStatus) trigText.style.color = '';
      } else {
        trigText.textContent = cur ? cur.textContent.trim() : 'Select\u2026';
        if (!isStatus) trigText.style.color = 'var(--text-muted, #7a7060)';
      }
    }

    function buildOptions() {
      dropdown.innerHTML = '';
      Array.from(sel.options).forEach(function(opt) {
        var item = document.createElement('div');
        item.className = 'cs-option';
        if (opt.value === '') item.classList.add('cs-option-placeholder');
        if (opt.selected) item.classList.add('selected');
        item.textContent = opt.textContent.trim();
        item.dataset.value = opt.value;
        if (isStatus && statusTextColors[opt.value]) {
          item.style.color = statusTextColors[opt.value];
        }
        item.addEventListener('click', function(e) {
          e.stopPropagation();
          sel.value = opt.value;
          sel.dispatchEvent(new Event('change', { bubbles: true }));
          if (isStatus) {
            trigger.style.borderColor = statusColors[opt.value] || 'rgba(200,160,60,0.3)';
            trigger.style.color = statusTextColors[opt.value] || '';
          }
          refreshTrigger();
          closeDropdown();
        });
        dropdown.appendChild(item);
      });
    }

    function positionDropdown() {
      var rect = trigger.getBoundingClientRect();
      var spaceBelow = window.innerHeight - rect.bottom;
      dropdown.style.position = 'fixed';
      dropdown.style.width = rect.width + 'px';
      dropdown.style.left = rect.left + 'px';
      dropdown.style.zIndex = '99999';
      if (spaceBelow < 280 && rect.top > 280) {
        dropdown.classList.add('cs-open-up');
        dropdown.style.top = '';
        dropdown.style.bottom = (window.innerHeight - rect.top) + 'px';
      } else {
        dropdown.classList.remove('cs-open-up');
        dropdown.style.top = rect.bottom + 'px';
        dropdown.style.bottom = '';
      }
    }

    function openDropdown() {
      document.querySelectorAll('.cs-dropdown.cs-open').forEach(function(d) {
        d.classList.remove('cs-open', 'cs-open-up');
        if (d._csWrap) {
          var t = d._csWrap.querySelector('.cs-trigger');
          if (t) { t.classList.remove('open'); t.setAttribute('aria-expanded', 'false'); }
          d._csWrap.appendChild(d);
          delete d._csWrap;
        }
        d.style.cssText = '';
      });

      buildOptions();
      refreshTrigger();

      document.body.appendChild(dropdown);
      dropdown._csWrap = wrap;
      positionDropdown();

      dropdown.classList.add('cs-open');
      trigger.classList.add('open');
      trigger.setAttribute('aria-expanded', 'true');
    }

    function closeDropdown() {
      dropdown.classList.remove('cs-open', 'cs-open-up');
      trigger.classList.remove('open');
      trigger.setAttribute('aria-expanded', 'false');
      if (dropdown.parentNode === document.body) {
        dropdown.style.cssText = '';
        wrap.appendChild(dropdown);
        delete dropdown._csWrap;
      }
    }

    trigger.addEventListener('click', function(e) {
      e.stopPropagation();
      dropdown.classList.contains('cs-open') ? closeDropdown() : openDropdown();
    });

    trigger.addEventListener('keydown', function(e) {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        dropdown.classList.contains('cs-open') ? closeDropdown() : openDropdown();
      }
      if (e.key === 'Escape') closeDropdown();
    });

    document.addEventListener('click', function(e) {
      if (!wrap.contains(e.target) && !dropdown.contains(e.target)) closeDropdown();
    });

    window.addEventListener('scroll', function() {
      if (dropdown.classList.contains('cs-open')) positionDropdown();
    }, true);

    window.addEventListener('resize', function() {
      if (dropdown.classList.contains('cs-open')) positionDropdown();
    });

    refreshTrigger();
  }

  function initCustomSelects() {
    document.querySelectorAll(
      'select.form-control:not([data-no-custom]), ' +
      'select.form-control-sm:not([data-no-custom]), ' +
      'select.res-link-select:not([data-no-custom]), ' +
      'select.status-select:not([data-no-custom])'
    ).forEach(function(sel) {
      if (window.getComputedStyle(sel).display === 'none') return;
      buildCustomSelect(sel);
    });
  }

  initCustomSelects();
})();

/* ============================================================
   TESTIMONIALS SLIDER
   ============================================================ */
(function() {
  var wrap = document.getElementById('tsliderWrap');
  var track = document.getElementById('tsliderTrack');
  var dotsEl = document.getElementById('tsliderDots');
  var prevBtn = document.getElementById('tsliderPrev');
  var nextBtn = document.getElementById('tsliderNext');
  if (!track || !wrap) return;

  var cards = Array.from(track.querySelectorAll('.tcard'));
  var total = cards.length;
  var current = 0;
  var perPage = 1;
  var totalGroups = 1;
  var timer = null;

  function getPerPage() { return window.innerWidth >= 900 ? 3 : 1; }

  function layout() {
    perPage = getPerPage();
    totalGroups = Math.ceil(total / perPage);
    if (current >= totalGroups) current = totalGroups - 1;
    var cardW = wrap.offsetWidth / perPage;
    cards.forEach(function(c) { c.style.flexShrink = '0'; c.style.width = cardW + 'px'; });
    track.style.width = (cardW * total) + 'px';
    slide(false);
    buildDots();
  }

  function slide(animate) {
    var cardW = wrap.offsetWidth / perPage;
    var x = current * perPage * cardW;
    if (!animate) {
      track.style.transition = 'none';
      track.style.transform = 'translateX(-' + x + 'px)';
      void track.offsetWidth;
      track.style.transition = '';
    } else {
      track.style.transform = 'translateX(-' + x + 'px)';
    }
    if (!dotsEl) return;
    var dots = dotsEl.querySelectorAll('.tdot');
    dots.forEach(function(d, i) { d.classList.toggle('tdot-active', i === current); });
  }

  function buildDots() {
    if (!dotsEl) return;
    dotsEl.innerHTML = '';
    for (var i = 0; i < totalGroups; i++) {
      (function(idx) {
        var d = document.createElement('button');
        d.className = 'tdot' + (idx === current ? ' tdot-active' : '');
        d.setAttribute('aria-label', 'Slide ' + (idx + 1));
        d.addEventListener('click', function() { stopTimer(); current = idx; slide(true); buildDots(); startTimer(); });
        dotsEl.appendChild(d);
      })(i);
    }
  }

  function goTo(dir) {
    current = (current + dir + totalGroups) % totalGroups;
    slide(true);
    buildDots();
  }

  function startTimer() { timer = setInterval(function() { goTo(1); }, 5000); }
  function stopTimer() { clearInterval(timer); }

  layout();
  startTimer();

  if (prevBtn) prevBtn.addEventListener('click', function() { stopTimer(); goTo(-1); startTimer(); });
  if (nextBtn) nextBtn.addEventListener('click', function() { stopTimer(); goTo(1); startTimer(); });
  wrap.addEventListener('mouseenter', stopTimer);
  wrap.addEventListener('mouseleave', startTimer);
  window.addEventListener('resize', function() { stopTimer(); layout(); startTimer(); });
})();

// ── COOKIE CONSENT ──────────────────────────────────────────
(function() {
  var COOKIE_KEY = 'vs_cookie_consent';
  var banner = document.getElementById('cookieBanner');
  if (!banner) return;

  function getCookie(name) {
    var match = document.cookie.match(new RegExp('(?:^|; )' + name + '=([^;]*)'));
    return match ? decodeURIComponent(match[1]) : null;
  }
  function setCookie(name, value, days) {
    var expires = new Date(Date.now() + days * 864e5).toUTCString();
    document.cookie = name + '=' + encodeURIComponent(value) + '; expires=' + expires + '; path=/; SameSite=Lax';
  }
  function dismiss() {
    banner.classList.add('cookie-banner-hide');
    setTimeout(function() { banner.style.display = 'none'; }, 380);
  }
  if (!getCookie(COOKIE_KEY)) {
    banner.style.display = 'flex';
  }

  document.getElementById('cookieAccept').addEventListener('click', function() {
    setCookie(COOKIE_KEY, 'accepted', 365);
    dismiss();
  });

  document.getElementById('cookieDecline').addEventListener('click', function() {
    setCookie(COOKIE_KEY, 'necessary', 365);
    dismiss();
  });
})();

console.log('%c✂ Velvet Steel Barbershop', 'color:#c8a03c;font-size:18px;font-weight:bold;');
console.log('%cPremium grooming. Deliberate craft.', 'color:#8a8070;font-size:11px;');
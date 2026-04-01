/* Velvet Steel Barbershop - Main JS */

const navbar = document.getElementById('navbar');
if (navbar) {
  window.addEventListener('scroll', () => {
    navbar.classList.toggle('scrolled', window.scrollY > 60);
  });
}

const navToggle = document.getElementById('navToggle');
const navLinks = document.getElementById('navLinks');
const navDropdownEl = document.querySelector('.nav-dropdown');

function closeMobileDropdown() {
  if (navDropdownEl) navDropdownEl.classList.remove('open');
}

function closeNav() {
  if (!navLinks || !navToggle) return;
  navLinks.classList.remove('open');
  navToggle.classList.remove('active');
  closeMobileDropdown();
  navToggle.querySelectorAll('span').forEach(s => {
    s.style.transform = '';
    s.style.opacity = '';
  });
}

if (navToggle && navLinks) {
  navToggle.addEventListener('click', (e) => {
    e.stopPropagation();
    const isOpen = navLinks.classList.contains('open');
    if (isOpen) {
      closeNav();
    } else {
      navLinks.classList.add('open');
      navToggle.classList.add('active');
      const spans = navToggle.querySelectorAll('span');
      spans[0].style.transform = 'rotate(45deg) translate(5px, 5px)';
      spans[1].style.opacity = '0';
      spans[2].style.transform = 'rotate(-45deg) translate(5px, -5px)';
    }
  });

  document.addEventListener('click', (e) => {
    if (navbar && !navbar.contains(e.target)) {
      closeNav();
    }
  });

  navLinks.querySelectorAll('a').forEach(link => {
    link.addEventListener('click', () => closeNav());
  });
}

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
  a.addEventListener('click', e => {
    const target = document.querySelector(a.getAttribute('href'));
    if (target) {
      e.preventDefault();
      target.scrollIntoView({ behavior: 'smooth' });
    }
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

const barberSelect = document.getElementById('barberSelect');
const barberPreview = document.getElementById('barberPreview');
if (barberSelect && barberPreview) {
  barberSelect.addEventListener('change', function() {
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

const serviceSelect = document.getElementById('serviceSelect');
const servicePreview = document.getElementById('servicePreview');
if (serviceSelect && servicePreview) {
  serviceSelect.addEventListener('change', function() {
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

(function() {
  var overlay = document.getElementById('vsConfirmModal');
  if (!overlay) return;
  var msgEl = overlay.querySelector('.vs-confirm-msg');
  var cancelBtn = overlay.querySelector('.vs-confirm-cancel');
  var okBtn = overlay.querySelector('.vs-confirm-ok');
  var pendingForm = null;

  document.querySelectorAll('form[data-confirm]').forEach(function(form) {
    form.addEventListener('submit', function(e) {
      e.preventDefault();
      if (msgEl) msgEl.textContent = this.dataset.confirm;
      pendingForm = this;
      overlay.classList.add('active');
    });
  });

  if (cancelBtn) {
    cancelBtn.addEventListener('click', function() {
      overlay.classList.remove('active');
      pendingForm = null;
    });
  }

  if (okBtn) {
    okBtn.addEventListener('click', function() {
      overlay.classList.remove('active');
      if (pendingForm) {
        var f = pendingForm;
        pendingForm = null;
        f.submit();
      }
    });
  }

  overlay.addEventListener('click', function(e) {
    if (e.target === overlay) {
      overlay.classList.remove('active');
      pendingForm = null;
    }
  });

  document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
      overlay.classList.remove('active');
      pendingForm = null;
    }
  });
})();

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

console.log('%c✂ Velvet Steel Barbershop', 'color:#c8a03c;font-size:18px;font-weight:bold;');
console.log('%cPremium grooming. Deliberate craft.', 'color:#8a8070;font-size:11px;');

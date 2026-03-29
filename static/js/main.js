/* Velvet Steel Barbershop - Main JS */

// ===================== NAVBAR SCROLL
const navbar = document.getElementById('navbar');
if (navbar) {
  window.addEventListener('scroll', () => {
    navbar.classList.toggle('scrolled', window.scrollY > 60);
  });
}

// ===================== MOBILE NAV TOGGLE
const navToggle = document.getElementById('navToggle');
const navLinks = document.getElementById('navLinks');

function closeNav() {
  if (!navLinks || !navToggle) return;
  navLinks.classList.remove('open');
  navToggle.classList.remove('active');
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

  // Close when clicking outside the navbar
  document.addEventListener('click', (e) => {
    if (navbar && !navbar.contains(e.target)) {
      closeNav();
    }
  });

  // Close when a nav link is tapped on mobile
  navLinks.querySelectorAll('a').forEach(link => {
    link.addEventListener('click', () => closeNav());
  });
}

// ===================== AUTO-DISMISS ALERTS
document.querySelectorAll('.alert').forEach(alert => {
  setTimeout(() => {
    alert.style.opacity = '0';
    alert.style.transform = 'translateX(20px)';
    setTimeout(() => alert.remove(), 300);
  }, 5000);
});

// ===================== SCROLL ANIMATION (AOS-like, no lib)
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

// ===================== SMOOTH ANCHOR LINKS
document.querySelectorAll('a[href^="#"]').forEach(a => {
  a.addEventListener('click', e => {
    const target = document.querySelector(a.getAttribute('href'));
    if (target) {
      e.preventDefault();
      target.scrollIntoView({ behavior: 'smooth' });
    }
  });
});

// ===================== SERVICE CARD 
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

const style = document.createElement('style');
style.textContent = '@keyframes ripple { to { transform: scale(30); opacity: 0; } }';
document.head.appendChild(style);

// ===================== BARBER PREVIEW (booking page)
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

// ===================== SERVICE PREVIEW (booking page)
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
          <span style="color:var(--gold);font-family:'Playfair Display',serif;font-size:1.1rem;font-weight:700;">₱${opt.dataset.price || ''}</span>
        </div>
      `;
    } else {
      servicePreview.innerHTML = '';
    }
  });
}

console.log('%c✂ Velvet Steel Barbershop', 'color:#c8a03c;font-size:18px;font-weight:bold;');
console.log('%cPremium grooming. Deliberate craft.', 'color:#8a8070;font-size:11px;');

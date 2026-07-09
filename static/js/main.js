document.addEventListener('DOMContentLoaded', () => {

  // Footer year
  const yearEl = document.getElementById('year');
  if (yearEl) yearEl.textContent = new Date().getFullYear();

  // Scroll progress rail
  const progressFill = document.getElementById('scrollProgress');
  const updateProgress = () => {
    const h = document.documentElement;
    const scrolled = (h.scrollTop) / (h.scrollHeight - h.clientHeight) * 100;
    if (progressFill) progressFill.style.width = `${scrolled}%`;
  };
  document.addEventListener('scroll', updateProgress, { passive: true });
  updateProgress();

  // Mobile nav toggle
  const navToggle = document.getElementById('navToggle');
  const mainNav = document.getElementById('mainNav');
  if (navToggle && mainNav) {
    navToggle.addEventListener('click', () => {
      mainNav.classList.toggle('open');
      navToggle.classList.toggle('open');
    });
    mainNav.querySelectorAll('a').forEach(link => {
      link.addEventListener('click', () => mainNav.classList.remove('open'));
    });
  }

  // Scroll reveal via IntersectionObserver
  const revealEls = document.querySelectorAll('.reveal');
  if ('IntersectionObserver' in window && revealEls.length) {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-visible');
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.15 });
    revealEls.forEach((el, i) => {
      el.style.setProperty('--i', i % 6);
      observer.observe(el);
    });
  } else {
    revealEls.forEach(el => el.classList.add('is-visible'));
  }

  // ---------------- Gallery filters ----------------
  const filterBtns = document.querySelectorAll('.filter-btn');
  const galleryItems = document.querySelectorAll('.gallery-item');
  filterBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      filterBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      const cat = btn.dataset.category;
      galleryItems.forEach(item => {
        const show = cat === 'all' || item.dataset.category === cat;
        item.classList.toggle('hidden', !show);
      });
    });
  });

  // ---------------- Lightbox ----------------
  const lightbox = document.getElementById('lightbox');
  const lightboxImg = document.getElementById('lightboxImg');
  const lightboxCaption = document.getElementById('lightboxCaption');
  const lightboxClose = document.getElementById('lightboxClose');

  document.querySelectorAll('.gallery-item, .marquee-item').forEach(item => {
    item.addEventListener('click', () => {
      const img = item.querySelector('img');
      if (!lightbox || !img) return;
      lightboxImg.src = img.src;
      lightboxCaption.textContent = img.alt || '';
      lightbox.classList.add('open');
    });
  });
  if (lightboxClose) {
    lightboxClose.addEventListener('click', () => lightbox.classList.remove('open'));
  }
  if (lightbox) {
    lightbox.addEventListener('click', (e) => {
      if (e.target === lightbox) lightbox.classList.remove('open');
    });
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') lightbox.classList.remove('open');
    });
  }

  // ---------------- Simple client-side form validation feedback ----------------
  const enquiryForm = document.getElementById('enquiryForm');
  if (enquiryForm) {
    enquiryForm.addEventListener('submit', (e) => {
      const requiredFields = enquiryForm.querySelectorAll('[required]');
      let valid = true;
      requiredFields.forEach(field => {
        if (!field.value.trim()) {
          valid = false;
          field.style.borderColor = '#FF5A1F';
        } else {
          field.style.borderColor = '';
        }
      });
      if (!valid) e.preventDefault();
    });
  }

  // ---------------- Header shrink on scroll (subtle) ----------------
  const header = document.getElementById('siteHeader');
  let lastY = window.scrollY;
  document.addEventListener('scroll', () => {
    if (!header) return;
    const y = window.scrollY;
    header.style.boxShadow = y > 10 ? '0 8px 24px rgba(0,0,0,0.25)' : 'none';
    lastY = y;
  }, { passive: true });

});

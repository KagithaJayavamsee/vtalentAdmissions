const navToggle = document.getElementById('navToggle');
const mainNav = document.getElementById('mainNav');

if (navToggle && mainNav) {
  const setNavOpen = (isOpen) => {
    navToggle.setAttribute('aria-expanded', String(isOpen));
    mainNav.classList.toggle('nav-open', isOpen);
  };

  navToggle.addEventListener('click', () => {
    setNavOpen(navToggle.getAttribute('aria-expanded') !== 'true');
  });

  mainNav.addEventListener('click', (event) => {
    if (event.target instanceof Element && event.target.closest('a')) {
      setNavOpen(false);
    }
  });

  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape' && navToggle.getAttribute('aria-expanded') === 'true') {
      setNavOpen(false);
      navToggle.focus();
    }
  });
}

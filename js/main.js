// core functionality

// Navigation
function navigateToSection(sectionId) {
    const section = document.getElementById(sectionId);
    if (section) {
        section.scrollIntoView({ behavior: 'smooth' });
    }
}

// Menu Toggle
const menuToggleButton = document.querySelector('.menu-toggle');
const menu = document.querySelector('.menu');

menuToggleButton.addEventListener('click', () => {
    menu.classList.toggle('active');
});

// Smooth Scrolling
document.querySelectorAll('a.scroll-link').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
        e.preventDefault();
        navigateToSection(this.getAttribute('href').substring(1));
    });
});

// Utilities
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}
// script.js

// Smooth scrolling for anchor links
const smoothScroll = (target) => {
    document.querySelector(target).scrollIntoView({
        behavior: 'smooth'
    });
};

// Mobile menu toggle functionality
const mobileMenuToggle = () => {
    const menu = document.getElementById('mobile-menu');
    menu.classList.toggle('active');
};

// Button click animations
const buttonClickAnimation = (button) => {
    button.classList.add('clicked');
    setTimeout(() => button.classList.remove('clicked'), 300);
};

// Event listeners
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        smoothScroll(this.getAttribute('href'));
    });
});

document.getElementById('mobile-menu-toggle').addEventListener('click', mobileMenuToggle);

document.querySelectorAll('.button').forEach(button => {
    button.addEventListener('click', function () {
        buttonClickAnimation(this);
    });
});

// Additional interactivity features can be added here...
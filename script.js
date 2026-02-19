// script.js

// Smooth Scrolling
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();

        document.querySelector(this.getAttribute('href')).scrollIntoView({
            behavior: 'smooth'
        });
    });
});

// Form Handling
const form = document.querySelector('form');
form.addEventListener('submit', function (e) {
    e.preventDefault();
    const formData = new FormData(form);
    // Handle the form data here
    console.log('Form submitted:', formData);
});

// WhatsApp Integration
function sendWhatsAppMessage(message) {
    const number = '1234567890'; // Replace with actual number
    const url = `https://api.whatsapp.com/send?phone=${number}&text=${encodeURIComponent(message)}`;
    window.open(url, '_blank');
}

// Mobile Menu Toggle
const menuToggle = document.querySelector('.menu-toggle');
const menu = document.querySelector('.menu');
menuToggle.addEventListener('click', function() {
    menu.classList.toggle('active');
});

// Interactive Features
const interactiveElements = document.querySelectorAll('.interactive');
interactiveElements.forEach(element => {
    element.addEventListener('click', function() {
        this.classList.toggle('active');
    });
});

// Wait for the DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Welcome button click event on home page
    const welcomeBtn = document.getElementById('welcome-btn');
    if (welcomeBtn) {
        welcomeBtn.addEventListener('click', function() {
            alert('Welcome to my Flask website! Thanks for visiting.');
        });
    }
    
    // Time button click event on about page
    const timeBtn = document.getElementById('time-btn');
    const currentTimeElement = document.getElementById('current-time');
    if (timeBtn && currentTimeElement) {
        timeBtn.addEventListener('click', function() {
            const now = new Date();
            currentTimeElement.textContent = 'Current time: ' + now.toLocaleTimeString();
        });
    }
    
    // Add a simple animation to the navigation links
    const navLinks = document.querySelectorAll('.nav-links a');
    navLinks.forEach(link => {
        link.addEventListener('mouseover', function() {
            this.style.transform = 'translateY(-2px)';
        });
        
        link.addEventListener('mouseout', function() {
            this.style.transform = 'translateY(0)';
        });
    });
    
    console.log('JavaScript loaded successfully!');
});
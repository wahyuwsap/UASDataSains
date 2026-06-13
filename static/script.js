document.addEventListener('DOMContentLoaded', function() {
    // Initialize AOS Library
    AOS.init({
        once: true,
        offset: 50,
    });

    // Add interact effects for form inputs
    const inputs = document.querySelectorAll('.form-control');
    inputs.forEach(input => {
        input.addEventListener('focus', function() {
            this.parentElement.parentElement.classList.add('focused');
        });
        input.addEventListener('blur', function() {
            this.parentElement.parentElement.classList.remove('focused');
        });
    });
});

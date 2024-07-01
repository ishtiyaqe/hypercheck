document.addEventListener('DOMContentLoaded', () => {
    const footerElements = document.querySelectorAll('.main-footer');
    footerElements.forEach(element => {
        element.style.display = 'none';
    });
});
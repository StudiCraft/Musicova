// HTML/ui.js
// This file will contain UI related functionalities, including theme management.

/**
 * Initializes the dark mode functionality.
 * Checks localStorage for a saved preference and applies it on load.
 * Sets up the event listener for the dark mode toggle button.
 * @param {string} toggleButtonId - The ID of the dark mode toggle button.
 */
function initDarkMode(toggleButtonId) {
    const darkModeToggle = document.getElementById(toggleButtonId);
    if (!darkModeToggle) {
        console.error('Dark mode toggle button not found:', toggleButtonId);
        return;
    }

    const toggleIcon = darkModeToggle.querySelector('.toggle-icon');
    if (!toggleIcon) {
        console.error('Toggle icon not found within button:', toggleButtonId);
        return;
    }

    // Apply saved theme on load
    if (localStorage.getItem('darkMode') === 'enabled') {
        document.body.classList.add('dark-mode');
        toggleIcon.textContent = '☀️';
    } else {
        document.body.classList.remove('dark-mode'); // Ensure it's not there if disabled
        toggleIcon.textContent = '🌙';
    }

    // Event listener for the dark mode toggle button
    darkModeToggle.addEventListener('click', () => {
        document.body.classList.toggle('dark-mode');
        const isDarkMode = document.body.classList.contains('dark-mode');
        localStorage.setItem('darkMode', isDarkMode ? 'enabled' : 'disabled');
        toggleIcon.textContent = isDarkMode ? '☀️' : '🌙';
    });
}

// Export functions if using modules in the future, or make them globally available.
// For now, they will be global as script tags will be added to HTML.

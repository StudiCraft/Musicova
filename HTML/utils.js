// HTML/utils.js
// This file will contain utility functions used across the application.

/**
 * Converts seconds into a 'minutes:seconds' string format.
 * Example: 125 seconds becomes "2:05".
 * @param {number} seconds - The total number of seconds.
 * @returns {string} The formatted time string (e.g., "MM:SS").
 */
function formatTime(seconds) {
    const minutes = Math.floor(seconds / 60); // Calculate minutes
    const remainingSeconds = Math.floor(seconds % 60); // Calculate remaining seconds
    // Format seconds to always have two digits (e.g., "05" instead of "5")
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
}

// Add other utility functions here as needed.

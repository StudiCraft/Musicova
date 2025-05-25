/**
 * HTML/script.js
 * This script manages the music player functionality for the Musicova web interface.
 * It handles audio import (files and folders), dynamic creation of player cards for each audio track,
 * playback controls (play, pause, next, previous), and interactive progress bar functionality.
 * It also updates time displays and manages the visual state of play/pause buttons.
 */
document.addEventListener('DOMContentLoaded', () => {
    // DOM element selections
    const importButton = document.querySelector('.import-button'); // Button to trigger file/folder import
    const fileSelect = document.querySelector('.file-select'); // Dropdown to select import type (file/folder)
    
    // Create and append the main container for audio cards
    const playerContainer = document.createElement('div');
    playerContainer.className = 'audio-cards-container'; // Container for all dynamically generated audio player cards
    // Appends the player container to the element with class 'musicova-player-title'
    document.querySelector('.musicova-player-title').appendChild(playerContainer);

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

    /**
     * Dynamically creates the HTML structure for an audio player card.
     * Each card includes album art (placeholder), track name, time display,
     * a progress bar, playback controls (previous, play/pause, next), and an HTML audio element.
     * @param {File} file - The audio file object for which to create the card.
     * @returns {HTMLElement} The fully constructed audio card element.
     */
    function createAudioCard(file) {
        // Create the main card container
        const card = document.createElement('div');
        card.className = 'audio-card';

        // Create placeholder for album art
        const albumArt = document.createElement('div');
        albumArt.className = 'album-art'; // Styled by CSS

        // Create div for audio track name
        const audioName = document.createElement('div');
        audioName.className = 'audio-name';
        audioName.textContent = file.name.replace(/\.[^/.]+$/, ''); // Display filename without extension

        // Create div for time display (current time / total duration)
        const timeDisplay = document.createElement('div');
        timeDisplay.className = 'time-display';
        timeDisplay.innerHTML = '<span>0:00</span><span>0:00</span>'; // Initial state for current time and total duration

        // Create progress bar elements
        const progressBar = document.createElement('div');
        progressBar.className = 'progress-bar'; // Outer container for progress
        const progressFill = document.createElement('div');
        progressFill.className = 'progress-fill'; // The actual filled part of the progress bar
        progressBar.appendChild(progressFill);

        // Create container for control buttons
        const controls = document.createElement('div');
        controls.className = 'controls';

        // Create 'Previous' button
        const prevButton = document.createElement('button');
        prevButton.className = 'control-button prev-button';
        prevButton.innerHTML = `<img src="Icons/10b81wv7wlmm7brpwyt.svg" alt="Previous" style="width: 24px; height: 24px;">`;

        // Create 'Play/Pause' button
        const playButton = document.createElement('button');
        playButton.className = 'control-button play-button';
        playButton.innerHTML = `<img src="Icons/r5qa5pfzfndm7bro859.svg" alt="Play" style="width: 24px; height: 24px;">`; // Initial state: Play icon

        // Create 'Next' button
        const nextButton = document.createElement('button');
        nextButton.className = 'control-button next-button';
        // Uses the same icon as previous, flipped horizontally via CSS transform
        nextButton.innerHTML = `<img src="Icons/10b81wv7wlmm7brpwyt.svg" alt="Next" style="width: 24px; height: 24px; transform: scaleX(-1);">`;

        // Add buttons to controls container
        controls.appendChild(prevButton);
        controls.appendChild(playButton);
        controls.appendChild(nextButton);

        // Create the HTML audio element
        const audio = document.createElement('audio');
        audio.src = URL.createObjectURL(file); // Create a temporary URL for the local file

        // Event listener: Update total duration when audio metadata is loaded
        audio.addEventListener('loadedmetadata', () => {
            timeDisplay.children[1].textContent = formatTime(audio.duration); // Update total duration display
        });

        // Event listener: Update progress bar and current time during playback
        audio.addEventListener('timeupdate', () => {
            const currentTime = audio.currentTime;
            const duration = audio.duration;
            // Calculate progress percentage, ensure duration is not zero to avoid NaN
            const progress = duration ? (currentTime / duration) * 100 : 0;
            progressFill.style.width = `${progress}%`; // Update progress bar fill
            timeDisplay.children[0].textContent = formatTime(currentTime); // Update current time display
        });

        /**
         * Event listener for the play/pause button.
         * Toggles audio playback and updates the button icon.
         */
        playButton.addEventListener('click', () => {
            if (audio.paused) {
                audio.play(); // Play audio
                // Change button icon to 'Pause'
                playButton.innerHTML = `<img src="Icons/5dd3gw6mlhjm7brpg84.svg" alt="Pause" style="width: 24px; height: 24px;">`;
            } else {
                audio.pause(); // Pause audio
                // Change button icon to 'Play'
                playButton.innerHTML = `<img src="Icons/r5qa5pfzfndm7bro859.svg" alt="Play" style="width: 24px; height: 24px;">`;
            }
        });

        // Variables to manage progress bar dragging state
        let isDragging = false; // True if user is currently dragging the progress bar handle
        let wasPlaying = false; // True if audio was playing before dragging started

        /**
         * Event listener for 'mousedown' on the progress bar.
         * Initiates seeking: pauses audio if it was playing, and sets dragging flag.
         * @param {MouseEvent} e - The mousedown event object.
         */
        progressBar.addEventListener('mousedown', (e) => {
            isDragging = true;
            wasPlaying = !audio.paused; // Check if audio was playing before mousedown
            if (wasPlaying) {
                audio.pause(); // Pause audio during seek
                // Temporarily set icon to 'Play' if it was playing
                playButton.innerHTML = `<img src="Icons/r5qa5pfzfndm7bro859.svg" alt="Play" style="width: 24px; height: 24px;">`;
            }
            updateProgress(e); // Update progress based on click position
        });

        /**
         * Event listener for 'mousemove' on the document.
         * If dragging is active, updates the audio progress.
         * @param {MouseEvent} e - The mousemove event object.
         */
        document.addEventListener('mousemove', (e) => {
            if (isDragging) {
                updateProgress(e); // Continuously update progress while dragging
            }
        });

        /**
         * Event listener for 'mouseup' on the document.
         * Finalizes seeking: resumes playback if audio was playing before, and resets dragging flag.
         */
        document.addEventListener('mouseup', () => {
            if (isDragging && wasPlaying) {
                audio.play(); // Resume playback if it was playing
                // Restore 'Pause' icon
                playButton.innerHTML = `<img src="Icons/5dd3gw6mlhjm7brpg84.svg" alt="Pause" style="width: 24px; height: 24px;">`;
            }
            isDragging = false; // Reset dragging state
        });

        /**
         * Updates the audio current time based on the click/drag position on the progress bar.
         * @param {MouseEvent} e - The mouse event (mousedown or mousemove).
         */
        function updateProgress(e) {
            const rect = progressBar.getBoundingClientRect(); // Get progress bar dimensions and position
            // Calculate click position as a fraction (0 to 1) of the progress bar width
            let clickPosition = (e.clientX - rect.left) / rect.width;
            // Clamp the position between 0 and 1 to avoid out-of-bounds values
            clickPosition = Math.max(0, Math.min(1, clickPosition));
            audio.currentTime = clickPosition * audio.duration; // Set audio current time
        }

        /**
         * Event listener for the 'Previous' button.
         * Pauses the current track and plays the previous track in the playlist.
         * If the current track is the first, it does nothing.
         */
        prevButton.addEventListener('click', () => {
            const cards = Array.from(playerContainer.children); // Get all audio cards
            const currentIndex = cards.indexOf(card); // Find index of the current card
            if (currentIndex > 0) { // Check if there is a previous card
                const prevCard = cards[currentIndex - 1]; // Get the previous card element
                const prevAudio = prevCard.querySelector('audio'); // Get the audio element of the previous card
                const prevPlayButton = prevCard.querySelector('.play-button'); // Get play button of previous card

                // Pause current audio and reset its play button
                audio.pause();
                playButton.innerHTML = `<img src="Icons/r5qa5pfzfndm7bro859.svg" alt="Play" style="width: 24px; height: 24px;">`;
                
                // Play previous audio from the beginning and update its play button
                prevAudio.currentTime = 0;
                prevAudio.play();
                prevPlayButton.innerHTML = `<img src="Icons/5dd3gw6mlhjm7brpg84.svg" alt="Pause" style="width: 24px; height: 24px;">`;
            }
        });

        /**
         * Event listener for the 'Next' button.
         * Pauses the current track and plays the next track in the playlist.
         * If the current track is the last, it does nothing.
         */
        nextButton.addEventListener('click', () => {
            const cards = Array.from(playerContainer.children); // Get all audio cards
            const currentIndex = cards.indexOf(card); // Find index of the current card
            if (currentIndex < cards.length - 1) { // Check if there is a next card
                const nextCard = cards[currentIndex + 1]; // Get the next card element
                const nextAudio = nextCard.querySelector('audio'); // Get the audio element of the next card
                const nextPlayButton = nextCard.querySelector('.play-button'); // Get play button of next card

                // Pause current audio and reset its play button
                audio.pause();
                playButton.innerHTML = `<img src="Icons/r5qa5pfzfndm7bro859.svg" alt="Play" style="width: 24px; height: 24px;">`;

                // Play next audio from the beginning and update its play button
                nextAudio.currentTime = 0;
                nextAudio.play();
                nextPlayButton.innerHTML = `<img src="Icons/5dd3gw6mlhjm7brpg84.svg" alt="Pause" style="width: 24px; height: 24px;">`;
            }
        });

        // Append all created elements to the card
        card.appendChild(albumArt);
        card.appendChild(audioName);
        card.appendChild(timeDisplay);
        card.appendChild(progressBar);
        card.appendChild(controls);
        card.appendChild(audio); // Audio element is part of the card but not directly visible

        return card; // Return the fully assembled audio card
    }

    /**
     * Processes an array of audio files.
     * It clears any existing audio cards from the player container and then creates
     * and appends a new card for each valid audio file provided.
     * Valid audio types are checked by MIME type or file extension.
     * @param {File[]} files - An array of File objects to process.
     */
    function handleAudioFiles(files) {
        playerContainer.innerHTML = ''; // Clear any existing audio cards from the container
        
        // Iterate over each file provided
        files.forEach(file => {
            // Check if the file is an audio type by MIME or common audio extensions
            if (file.type.startsWith('audio/') || file.name.match(/\.(mp3|wav|ogg|m4a)$/i)) {
                const card = createAudioCard(file); // Create a new audio card for the file
                playerContainer.appendChild(card); // Append the new card to the container
            }
        });
    }

    /**
     * Event listener for the 'Import' button.
     * Handles the file/folder import process based on the selection in the `fileSelect` dropdown.
     * It dynamically creates an input element of type 'file', configures it for
     * file or folder selection, and triggers its click event to open the file dialog.
     * Selected files are then passed to `handleAudioFiles`.
     */
    importButton.addEventListener('click', () => {
        const selectedOption = fileSelect.value; // Get the selected import type (file/folder)

        // Alert user if no import type is selected
        if (!selectedOption) {
            alert('Please select an import type first');
            return;
        }

        // Dynamically create a file input element
        const input = document.createElement('input');
        input.type = 'file';
        
        if (selectedOption === 'folder') {
            // Enable directory selection for folder import
            input.webkitdirectory = true; // For Chrome/Safari
            input.directory = true;       // Standard property
        } else {
            // For file import, accept all audio types and allow multiple file selection
            input.accept = 'audio/*';
            input.multiple = true;
        }

        /**
         * Event listener for 'change' on the dynamically created file input.
         * This is triggered when the user selects files/folders.
         * @param {Event} e - The change event object.
         */
        input.addEventListener('change', (e) => {
            const files = Array.from(e.target.files); // Convert FileList to an array
            if (files.length > 0) {
                handleAudioFiles(files); // Process the selected files
            }
        });

        input.click(); // Programmatically click the hidden file input to open the dialog
    });
});
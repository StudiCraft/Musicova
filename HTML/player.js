// HTML/player.js
// This file will manage the music player functionality, including audio import,
// card creation, and playback controls.

// Ensure this script runs after the DOM is fully loaded.
// Specific player initialization logic will be triggered from player.html,
// for example, by calling an initPlayer() function defined here if needed,
// or this script can self-initialize if it's always for the player page.

let playerContainer; // To be initialized when the DOM is ready for player page

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
    albumArt.className = 'album-art';

    // Create div for audio track name
    const audioName = document.createElement('div');
    audioName.className = 'audio-name';
    audioName.textContent = file.name.replace(/\.[^/.]+$/, '');

    // Create div for time display (current time / total duration)
    const timeDisplay = document.createElement('div');
    timeDisplay.className = 'time-display';
    timeDisplay.innerHTML = '<span>0:00</span><span>0:00</span>';

    // Create progress bar elements
    const progressBar = document.createElement('div');
    progressBar.className = 'progress-bar';
    const progressFill = document.createElement('div');
    progressFill.className = 'progress-fill';
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
    playButton.innerHTML = `<img src="Icons/r5qa5pfzfndm7bro859.svg" alt="Play" style="width: 24px; height: 24px;">`;

    // Create 'Next' button
    const nextButton = document.createElement('button');
    nextButton.className = 'control-button next-button';
    nextButton.innerHTML = `<img src="Icons/10b81wv7wlmm7brpwyt.svg" alt="Next" style="width: 24px; height: 24px; transform: scaleX(-1);">`;

    controls.appendChild(prevButton);
    controls.appendChild(playButton);
    controls.appendChild(nextButton);

    // Create "Remove" button
    const removeButton = document.createElement('button');
    removeButton.className = 'control-button remove-button';
    removeButton.innerHTML = '&#x1F5D1;'; // Trash can icon
    removeButton.title = 'Remove track';
    controls.appendChild(removeButton); // Add it to the controls div

    // Create volume control
    const volumeControlContainer = document.createElement('div');
    volumeControlContainer.className = 'volume-control-container';
    const volumeSlider = document.createElement('input');
    volumeSlider.type = 'range';
    volumeSlider.min = '0';
    volumeSlider.max = '1';
    volumeSlider.step = '0.01';
    volumeSlider.value = '1'; // Default volume: 100%
    volumeSlider.className = 'volume-slider';
    volumeControlContainer.appendChild(volumeSlider);

    // Create the HTML audio element
    const audio = document.createElement('audio');
    audio.src = URL.createObjectURL(file);

    audio.addEventListener('loadedmetadata', () => {
        timeDisplay.children[1].textContent = formatTime(audio.duration); // Uses formatTime from utils.js
    });

    audio.addEventListener('timeupdate', () => {
        const currentTime = audio.currentTime;
        const duration = audio.duration;
        const progress = duration ? (currentTime / duration) * 100 : 0;
        progressFill.style.width = `${progress}%`;
        timeDisplay.children[0].textContent = formatTime(currentTime); // Uses formatTime from utils.js
    });

    playButton.addEventListener('click', () => {
        if (audio.paused) {
            // Before playing this audio, pause all other audio elements
            document.querySelectorAll('audio').forEach(otherAudio => {
                if (otherAudio !== audio && !otherAudio.paused) {
                    otherAudio.pause();
                    // Reset other play buttons to 'Play' icon
                    const otherPlayButton = otherAudio.closest('.audio-card').querySelector('.play-button');
                    if (otherPlayButton) {
                        otherPlayButton.innerHTML = `<img src="Icons/r5qa5pfzfndm7bro859.svg" alt="Play" style="width: 24px; height: 24px;">`;
                    }
                    // Remove active class from other cards
                     otherAudio.closest('.audio-card').classList.remove('active-card');
                }
            });
            audio.play();
            playButton.innerHTML = `<img src="Icons/5dd3gw6mlhjm7brpg84.svg" alt="Pause" style="width: 24px; height: 24px;">`;
            card.classList.add('active-card');
        } else {
            audio.pause();
            playButton.innerHTML = `<img src="Icons/r5qa5pfzfndm7bro859.svg" alt="Play" style="width: 24px; height: 24px;">`;
            card.classList.remove('active-card');
        }
    });

    let isDragging = false;
    let wasPlaying = false;

    progressBar.addEventListener('mousedown', (e) => {
        isDragging = true;
        wasPlaying = !audio.paused;
        if (wasPlaying) {
            audio.pause();
            playButton.innerHTML = `<img src="Icons/r5qa5pfzfndm7bro859.svg" alt="Play" style="width: 24px; height: 24px;">`;
        }
        updateProgress(e, progressBar, audio);
    });

    document.addEventListener('mousemove', (e) => {
        if (isDragging) {
            updateProgress(e, progressBar, audio);
        }
    });

    document.addEventListener('mouseup', () => {
        if (isDragging) {
            if (wasPlaying) {
                 // Before playing this audio, pause all other audio elements
                document.querySelectorAll('audio').forEach(otherAudio => {
                    if (otherAudio !== audio && !otherAudio.paused) {
                        otherAudio.pause();
                        const otherPlayButton = otherAudio.closest('.audio-card').querySelector('.play-button');
                        if (otherPlayButton) {
                            otherPlayButton.innerHTML = `<img src="Icons/r5qa5pfzfndm7bro859.svg" alt="Play" style="width: 24px; height: 24px;">`;
                        }
                        otherAudio.closest('.audio-card').classList.remove('active-card');
                    }
                });
                audio.play();
                playButton.innerHTML = `<img src="Icons/5dd3gw6mlhjm7brpg84.svg" alt="Pause" style="width: 24px; height: 24px;">`;
                card.classList.add('active-card');
            }
            isDragging = false;
        }
    });

    function updateProgress(e, progressBarElement, audioElement) {
        const rect = progressBarElement.getBoundingClientRect();
        let clickPosition = (e.clientX - rect.left) / rect.width;
        clickPosition = Math.max(0, Math.min(1, clickPosition));
        audioElement.currentTime = clickPosition * audioElement.duration;
    }

    prevButton.addEventListener('click', () => {
        const cards = Array.from(playerContainer.children);
        const currentIndex = cards.indexOf(card);
        if (currentIndex > 0) {
            const prevCard = cards[currentIndex - 1];
            const prevAudio = prevCard.querySelector('audio');
            const prevPlayButton = prevCard.querySelector('.play-button');

            audio.pause();
            audio.currentTime = 0; // Reset current track
            playButton.innerHTML = `<img src="Icons/r5qa5pfzfndm7bro859.svg" alt="Play" style="width: 24px; height: 24px;">`;
            card.classList.remove('active-card');

            // Pause all other audios before playing the new one
            document.querySelectorAll('audio').forEach(otherAudio => {
                if (otherAudio !== prevAudio && !otherAudio.paused) {
                    otherAudio.pause();
                    const otherPlayButton = otherAudio.closest('.audio-card').querySelector('.play-button');
                    if (otherPlayButton) {
                        otherPlayButton.innerHTML = `<img src="Icons/r5qa5pfzfndm7bro859.svg" alt="Play" style="width: 24px; height: 24px;">`;
                    }
                    otherAudio.closest('.audio-card').classList.remove('active-card');
                }
            });

            prevAudio.currentTime = 0;
            prevAudio.play();
            prevPlayButton.innerHTML = `<img src="Icons/5dd3gw6mlhjm7brpg84.svg" alt="Pause" style="width: 24px; height: 24px;">`;
            prevCard.classList.add('active-card');
        }
    });

    nextButton.addEventListener('click', () => {
        const cards = Array.from(playerContainer.children);
        const currentIndex = cards.indexOf(card);
        if (currentIndex < cards.length - 1) {
            const nextCard = cards[currentIndex + 1];
            const nextAudio = nextCard.querySelector('audio');
            const nextPlayButton = nextCard.querySelector('.play-button');

            audio.pause();
            audio.currentTime = 0; // Reset current track
            playButton.innerHTML = `<img src="Icons/r5qa5pfzfndm7bro859.svg" alt="Play" style="width: 24px; height: 24px;">`;
            card.classList.remove('active-card');

            // Pause all other audios before playing the new one
             document.querySelectorAll('audio').forEach(otherAudio => {
                if (otherAudio !== nextAudio && !otherAudio.paused) {
                    otherAudio.pause();
                    const otherPlayButton = otherAudio.closest('.audio-card').querySelector('.play-button');
                    if (otherPlayButton) {
                        otherPlayButton.innerHTML = `<img src="Icons/r5qa5pfzfndm7bro859.svg" alt="Play" style="width: 24px; height: 24px;">`;
                    }
                     otherAudio.closest('.audio-card').classList.remove('active-card');
                }
            });

            nextAudio.currentTime = 0;
            nextAudio.play();
            nextPlayButton.innerHTML = `<img src="Icons/5dd3gw6mlhjm7brpg84.svg" alt="Pause" style="width: 24px; height: 24px;">`;
            nextCard.classList.add('active-card');
        }
    });

    card.appendChild(albumArt);
    card.appendChild(audioName);
    card.appendChild(timeDisplay);
    card.appendChild(progressBar);
    card.appendChild(controls);
    card.appendChild(volumeControlContainer); // Add volume control to the card
    card.appendChild(audio);

    // Volume slider event listener
    volumeSlider.addEventListener('input', (e) => {
        audio.volume = e.target.value;
    });

    // Remove button event listener
    removeButton.addEventListener('click', () => {
        // Stop audio if it's playing
        if (!audio.paused) {
            audio.pause();
        }
        // Revoke the object URL to free up resources
        URL.revokeObjectURL(audio.src);
        // Remove the card from the DOM
        card.remove();
        // If this was the only card, or if other logic is needed (e.g. update playlist array), handle here
    });

    return card;
}

/**
 * Processes an array of audio files.
 * Clears existing cards and creates new ones for valid audio files.
 * @param {File[]} files - An array of File objects.
 */
function handleAudioFiles(files) {
    if (!playerContainer) {
        console.error("Player container not initialized.");
        return;
    }
    playerContainer.innerHTML = ''; // Clear existing cards

    files.forEach(file => {
        if (file.type.startsWith('audio/') || file.name.match(/\.(mp3|wav|ogg|m4a)$/i)) {
            const card = createAudioCard(file);
            playerContainer.appendChild(card);
        }
    });
}

/**
 * Initializes the player functionality, setting up import buttons and containers.
 * This should be called when the player page DOM is ready.
 */
function initPlayerPage() {
    const importButton = document.querySelector('.import-button');
    const fileSelect = document.querySelector('.file-select');
    const clearPlaylistButton = document.querySelector('.clear-playlist-button');

    // Initialize playerContainer
    const existingPlayerContainer = document.querySelector('.audio-cards-container');
    if (existingPlayerContainer) {
        playerContainer = existingPlayerContainer;
    } else {
        // Create and append the main container for audio cards if it doesn't exist
        playerContainer = document.createElement('div');
        playerContainer.className = 'audio-cards-container';
        // Append it to a suitable parent, e.g., after the import controls
        const playerTitleDiv = document.querySelector('.musicova-player-title');
        if (playerTitleDiv) {
            playerTitleDiv.appendChild(playerContainer);
        } else {
            document.body.appendChild(playerContainer); // Fallback
        }
    }


    if (importButton && fileSelect) {
        importButton.addEventListener('click', () => {
            const selectedOption = fileSelect.value;
            if (!selectedOption) {
                alert('Please select an import type first');
                return;
            }

            const input = document.createElement('input');
            input.type = 'file';

            if (selectedOption === 'folder') {
                input.webkitdirectory = true;
                input.directory = true;
            } else {
                input.accept = 'audio/*';
                input.multiple = true;
            }

            input.addEventListener('change', (e) => {
                const files = Array.from(e.target.files);
                if (files.length > 0) {
                    handleAudioFiles(files);
                }
            });
            input.click();
        });
    } else {
        console.error('Import button or file select not found.');
    }

    if (clearPlaylistButton && playerContainer) {
        clearPlaylistButton.addEventListener('click', () => {
            // Stop all playing audio and revoke URLs
            playerContainer.querySelectorAll('audio').forEach(audioEl => {
                if (!audioEl.paused) {
                    audioEl.pause();
                }
                URL.revokeObjectURL(audioEl.src);
            });
            // Clear the container
            playerContainer.innerHTML = '';
        });
    } else {
        if (!clearPlaylistButton) console.error('Clear playlist button not found.');
        if (!playerContainer) console.error('Player container not found for clear playlist functionality.');
    }

    // Initialize dark mode for player page
    initDarkMode('darkModeToggle'); // Assumes initDarkMode is available globally from ui.js
}

// If player.html is guaranteed to load this script, and the necessary DOM elements
// (like '.import-button') are present, we can auto-initialize.
// Otherwise, player.html should call initPlayerPage() in a DOMContentLoaded listener.
// For simplicity, let's assume player.html will set up its own DOMContentLoaded listener
// to call initPlayerPage and initDarkMode.
// However, since initDarkMode is now part of ui.js, player.html will call that separately.
// initPlayerPage will be called by player.html.
// The initDarkMode call within initPlayerPage is redundant if player.html calls it directly.
// Let's remove it from here to avoid double initialization and rely on player.html to call it.
// initDarkMode('darkModeToggle'); // Removed from here.tool_code
replace_with_git_merge_diff
HTML/player.js
<<<<<<< SEARCH
            card.classList.add('active-card');
        } else {
            audio.pause();
            playButton.innerHTML = `<img src="Icons/r5qa5pfzfndm7bro859.svg" alt="Play" style="width: 24px; height: 24px;">`;
            card.classList.remove('active-card');
        }
    });

    let isDragging = false;
    let wasPlaying = false;

    progressBar.addEventListener('mousedown', (e) => {
        isDragging = true;
        wasPlaying = !audio.paused;
        if (wasPlaying) {
            audio.pause();
            playButton.innerHTML = `<img src="Icons/r5qa5pfzfndm7bro859.svg" alt="Play" style="width: 24px; height: 24px;">`;
        }
        updateProgress(e, progressBar, audio);
    });

    document.addEventListener('mousemove', (e) => {
        if (isDragging) {
            updateProgress(e, progressBar, audio);
        }
    });

    document.addEventListener('mouseup', () => {
        if (isDragging) {
            if (wasPlaying) {
                 // Before playing this audio, pause all other audio elements
                document.querySelectorAll('audio').forEach(otherAudio => {
                    if (otherAudio !== audio && !otherAudio.paused) {
                        otherAudio.pause();
                        const otherPlayButton = otherAudio.closest('.audio-card').querySelector('.play-button');
                        if (otherPlayButton) {
                            otherPlayButton.innerHTML = `<img src="Icons/r5qa5pfzfndm7bro859.svg" alt="Play" style="width: 24px; height: 24px;">`;
                        }
                        otherAudio.closest('.audio-card').classList.remove('active-card');
                    }
                });
                audio.play();
                playButton.innerHTML = `<img src="Icons/5dd3gw6mlhjm7brpg84.svg" alt="Pause" style="width: 24px; height: 24px;">`;
                card.classList.add('active-card');
            }
            isDragging = false;
        }
    });

    function updateProgress(e, progressBarElement, audioElement) {
        const rect = progressBarElement.getBoundingClientRect();
        let clickPosition = (e.clientX - rect.left) / rect.width;
        clickPosition = Math.max(0, Math.min(1, clickPosition));
        audioElement.currentTime = clickPosition * audioElement.duration;
    }

    prevButton.addEventListener('click', () => {
        const cards = Array.from(playerContainer.children);
=======
            card.classList.add('active-card');
        } else {
            audio.pause();
            playButton.innerHTML = `<img src="Icons/r5qa5pfzfndm7bro859.svg" alt="Play" style="width: 24px; height: 24px;">`;
            card.classList.remove('active-card');
        }
    });

    // --- Progress Bar Interaction ---
    let isDraggingProgressBar = false;
    let wasPlayingBeforeDrag = false;

    progressBar.addEventListener('mousedown', (e) => {
        isDraggingProgressBar = true;
        wasPlayingBeforeDrag = !audio.paused;
        if (wasPlayingBeforeDrag) {
            audio.pause();
            // Visually update play button to "Play" as audio is paused
            playButton.innerHTML = `<img src="Icons/r5qa5pfzfndm7bro859.svg" alt="Play" style="width: 24px; height: 24px;">`;
        }
        // Immediately update progress to the click position
        handleProgressUpdate(e, progressBar, audio, progressFill, timeDisplay.children[0]);
    });

    document.addEventListener('mousemove', (e) => {
        if (isDraggingProgressBar) {
            // Update progress as the mouse moves
            handleProgressUpdate(e, progressBar, audio, progressFill, timeDisplay.children[0]);
        }
    });

    document.addEventListener('mouseup', (e) => { // Changed 'e' to be available if needed, though not used in this specific logic
        if (isDraggingProgressBar) {
            // Final progress update on mouse up
            handleProgressUpdate(e, progressBar, audio, progressFill, timeDisplay.children[0], true); // Pass true for final update

            if (wasPlayingBeforeDrag) {
                // Pause other audios before resuming this one
                document.querySelectorAll('audio').forEach(otherAudio => {
                    if (otherAudio !== audio && !otherAudio.paused) {
                        otherAudio.pause();
                        const otherPlayButton = otherAudio.closest('.audio-card').querySelector('.play-button');
                        if (otherPlayButton) {
                            otherPlayButton.innerHTML = `<img src="Icons/r5qa5pfzfndm7bro859.svg" alt="Play" style="width: 24px; height: 24px;">`;
                        }
                        otherAudio.closest('.audio-card').classList.remove('active-card');
                    }
                });
                audio.play();
                playButton.innerHTML = `<img src="Icons/5dd3gw6mlhjm7brpg84.svg" alt="Pause" style="width: 24px; height: 24px;">`;
                card.classList.add('active-card');
            }
            isDraggingProgressBar = false;
            wasPlayingBeforeDrag = false;
        }
    });

    /**
     * Handles the update of audio progress based on mouse interaction with the progress bar.
     * @param {MouseEvent} e - The mouse event.
     * @param {HTMLElement} progressBarElement - The progress bar element.
     * @param {HTMLAudioElement} audioElement - The audio element.
     * @param {HTMLElement} progressFillElement - The progress fill element.
     * @param {HTMLElement} currentTimeDisplay - The element displaying current time.
     * @param {boolean} isFinalUpdate - Indicates if this is the final update (e.g., on mouseup).
     */
    function handleProgressUpdate(e, progressBarElement, audioElement, progressFillElement, currentTimeDisplay, isFinalUpdate = false) {
        const rect = progressBarElement.getBoundingClientRect();
        let clickPositionRatio = (e.clientX - rect.left) / rect.width;
        clickPositionRatio = Math.max(0, Math.min(1, clickPositionRatio)); // Clamp between 0 and 1

        const newTime = clickPositionRatio * audioElement.duration;

        // Update audio time only if it's the final update or if dragging (provides smoother visual feedback)
        if (isFinalUpdate || isDraggingProgressBar) {
             audioElement.currentTime = newTime;
        }

        // Update visual representation (fill and time text) immediately
        progressFillElement.style.width = `${clickPositionRatio * 100}%`;
        currentTimeDisplay.textContent = formatTime(newTime);
    }


    prevButton.addEventListener('click', () => {
        if (!playerContainer) return; // Ensure playerContainer is defined
        const cards = Array.from(playerContainer.children);
>>>>>>> REPLACE

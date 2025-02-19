document.addEventListener('DOMContentLoaded', () => {
    const importButton = document.querySelector('.import-button');
    const fileSelect = document.querySelector('.file-select');
    const playerContainer = document.createElement('div');
    playerContainer.className = 'audio-cards-container';
    document.querySelector('.musicova-player-title').appendChild(playerContainer);

    function formatTime(seconds) {
        const minutes = Math.floor(seconds / 60);
        const remainingSeconds = Math.floor(seconds % 60);
        return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
    }

    function createAudioCard(file) {
        const card = document.createElement('div');
        card.className = 'audio-card';

        const albumArt = document.createElement('div');
        albumArt.className = 'album-art';

        const audioName = document.createElement('div');
        audioName.className = 'audio-name';
        audioName.textContent = file.name.replace(/\.[^/.]+$/, '');

        const timeDisplay = document.createElement('div');
        timeDisplay.className = 'time-display';
        timeDisplay.innerHTML = '<span>0:00</span><span>0:00</span>';

        const progressBar = document.createElement('div');
        progressBar.className = 'progress-bar';
        const progressFill = document.createElement('div');
        progressFill.className = 'progress-fill';
        progressBar.appendChild(progressFill);

        const controls = document.createElement('div');
        controls.className = 'controls';

        const prevButton = document.createElement('button');
        prevButton.className = 'control-button prev-button';
        prevButton.innerHTML = `<img src="Icons/10b81wv7wlmm7brpwyt.svg" alt="Previous" style="width: 24px; height: 24px;">`

        const playButton = document.createElement('button');
        playButton.className = 'control-button play-button';
        playButton.innerHTML = `<img src="Icons/r5qa5pfzfndm7bro859.svg" alt="Play" style="width: 24px; height: 24px;">`

        const nextButton = document.createElement('button');
        nextButton.className = 'control-button next-button';
        nextButton.innerHTML = `<img src="Icons/10b81wv7wlmm7brpwyt.svg" alt="Next" style="width: 24px; height: 24px; transform: scaleX(-1);">`

        controls.appendChild(prevButton);
        controls.appendChild(playButton);
        controls.appendChild(nextButton);

        const audio = document.createElement('audio');
        audio.src = URL.createObjectURL(file);

        // Update time display when metadata is loaded
        audio.addEventListener('loadedmetadata', () => {
            timeDisplay.children[1].textContent = formatTime(audio.duration);
        });

        // Update progress bar and current time during playback
        audio.addEventListener('timeupdate', () => {
            const currentTime = audio.currentTime;
            const duration = audio.duration;
            const progress = (currentTime / duration) * 100;
            progressFill.style.width = `${progress}%`;
            timeDisplay.children[0].textContent = formatTime(currentTime);
        });

        // Handle play/pause
        playButton.addEventListener('click', () => {
            if (audio.paused) {
                audio.play();
                playButton.innerHTML = `<img src="Icons/5dd3gw6mlhjm7brpg84.svg" alt="Pause" style="width: 24px; height: 24px;">`
            } else {
                audio.pause();
                playButton.innerHTML = `<img src="Icons/r5qa5pfzfndm7bro859.svg" alt="Play" style="width: 24px; height: 24px;">`
            }
        });

        // Handle progress bar interactions
        let isDragging = false;
        let wasPlaying = false;

        progressBar.addEventListener('mousedown', (e) => {
            isDragging = true;
            wasPlaying = !audio.paused;
            if (wasPlaying) {
                audio.pause();
                playButton.innerHTML = `<img src="Icons/r5qa5pfzfndm7bro859.svg" alt="Play" style="width: 24px; height: 24px;">`;
            }
            updateProgress(e);
        });

        document.addEventListener('mousemove', (e) => {
            if (isDragging) {
                updateProgress(e);
            }
        });

        document.addEventListener('mouseup', () => {
            if (isDragging && wasPlaying) {
                audio.play();
                playButton.innerHTML = `<img src="Icons/5dd3gw6mlhjm7brpg84.svg" alt="Pause" style="width: 24px; height: 24px;">`;
            }
            isDragging = false;
        });

        function updateProgress(e) {
            const rect = progressBar.getBoundingClientRect();
            let clickPosition = (e.clientX - rect.left) / rect.width;
            clickPosition = Math.max(0, Math.min(1, clickPosition));
            audio.currentTime = clickPosition * audio.duration;
        }

        // Handle previous and next buttons
        prevButton.addEventListener('click', () => {
            const cards = Array.from(playerContainer.children);
            const currentIndex = cards.indexOf(card);
            if (currentIndex > 0) {
                const prevCard = cards[currentIndex - 1];
                const prevAudio = prevCard.querySelector('audio');
                const prevPlayButton = prevCard.querySelector('.play-button');
                audio.pause();
                playButton.innerHTML = `<img src="Icons/r5qa5pfzfndm7bro859.svg" alt="Play" style="width: 24px; height: 24px;">`
                prevAudio.currentTime = 0;
                prevAudio.play();
                prevPlayButton.innerHTML = `<img src="Icons/5dd3gw6mlhjm7brpg84.svg" alt="Pause" style="width: 24px; height: 24px;">`;
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
                playButton.innerHTML = `<img src="Icons/r5qa5pfzfndm7bro859.svg" alt="Play" style="width: 24px; height: 24px;">`
                nextAudio.currentTime = 0;
                nextAudio.play();
                nextPlayButton.innerHTML = `<img src="Icons/5dd3gw6mlhjm7brpg84.svg" alt="Pause" style="width: 24px; height: 24px;">`;
            }
        });

        card.appendChild(albumArt);
        card.appendChild(audioName);
        card.appendChild(timeDisplay);
        card.appendChild(progressBar);
        card.appendChild(controls);
        card.appendChild(audio);

        return card;
    }

    function handleAudioFiles(files) {
        playerContainer.innerHTML = ''; // Clear existing cards
        
        files.forEach(file => {
            if (file.type.startsWith('audio/') || file.name.match(/\.(mp3|wav|ogg|m4a)$/i)) {
                const card = createAudioCard(file);
                playerContainer.appendChild(card);
            }
        });
    }

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
});
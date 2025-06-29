"""
Musicova: A PyQt5-based desktop music player application.

This module implements a music player with a graphical user interface using PyQt5.
It allows users to import music files and folders, manage playlists, control playback,
and switch between light and dark themes.
"""
import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QLabel,
                             QVBoxLayout, QWidget, QFileDialog, QComboBox,
                             QScrollArea, QHBoxLayout, QSlider, QGridLayout)
from PyQt5.QtCore import Qt, QUrl, QSettings
from PyQt5.QtGui import QIcon, QPixmap, QTransform, QFontDatabase # Added QFontDatabase
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent

# Icon Paths (assuming icons are in 'Python/Icons/' relative to this script)
# IMPORTANT: These icons need to be copied from HTML/Icons to Python/Icons for this to work.
ICONS_DIR = os.path.join(os.path.dirname(__file__), 'Icons')
PLAY_ICON_PATH = os.path.join(ICONS_DIR, 'r5qa5pfzfndm7bro859.svg')
PAUSE_ICON_PATH = os.path.join(ICONS_DIR, '5dd3gw6mlhjm7brpg84.svg')
PREV_ICON_PATH = os.path.join(ICONS_DIR, '10b81wv7wlmm7brpwyt.svg')
# NEXT_ICON_PATH uses PREV_ICON_PATH and is transformed in code.
# Other icons (trash, moon, sun) will remain text-based for now.

class MusicovaApp(QMainWindow):
    """
    The main application window for Musicova.

    Handles initial setup, theme toggling, and launching the player window.
    It saves theme preferences using QSettings.
    """
    def __init__(self):
        """
        Initializes the MusicovaApp.

        Sets up the main window, loads theme settings, and calls init_ui to
        create the user interface.
        """
        super().__init__()
        self.settings = QSettings('Musicova', 'Theme')  # Application and organization name for settings
        self.dark_mode = self.settings.value('dark_mode', False, type=bool) # Load saved theme or default to False
        self.init_ui()

    def init_ui(self):
        """
        Initializes the user interface elements for the main window.

        Sets the window title, minimum size, and creates the layout.
        It includes a logo, title, subtitle, an access button to the player,
        and a theme toggle button.
        """
        self.setWindowTitle('Musicova')
        self.setMinimumSize(800, 600)

        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Media player instance for the main window (potentially for previews or other features)
        # self.media_player = QMediaPlayer() # This player is not directly used for playback in the main screen. Removed as unused.
        layout.setAlignment(Qt.AlignCenter)

        # Load and display logo
        logo_path = os.path.join(os.path.dirname(__file__), 'Musicova logo v2.png')
        logo_label = QLabel()
        pixmap = QPixmap(logo_path)
        scaled_pixmap = pixmap.scaled(300, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation) # Scale logo smoothly
        logo_label.setPixmap(scaled_pixmap)
        logo_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(logo_label)

        # Add title and subtitle labels
        title_label = QLabel('Musicova')
        title_label.setStyleSheet('color: black; font-family: "DynaPuff", sans-serif; font-size: 48px; font-weight: bold;')
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        subtitle_label = QLabel('The Open-Source Offline Music Player')
        subtitle_label.setStyleSheet('font-family: "DynaPuff", sans-serif; font-size: 24px;')
        subtitle_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(subtitle_label)

        # Add access button to open the player window
        access_button = QPushButton('Access')
        access_button.setObjectName("access_button") # Set object name for styling
        access_button.clicked.connect(self.show_player) # Connect button click to show_player method
        layout.addWidget(access_button, alignment=Qt.AlignCenter)

        # Add theme toggle button
        self.theme_button = QPushButton('🌙') # Initial icon for light mode
        self.theme_button.setFixedSize(40, 40) # Fixed size for a circular look with border-radius
        self.theme_button.clicked.connect(self.toggle_theme) # Connect button click to toggle_theme method

        # Layout for the theme button, pushing it to the right
        top_bar_layout = QHBoxLayout()
        top_bar_layout.addStretch(1) # Add stretch to push button to the right
        top_bar_layout.addWidget(self.theme_button)
        layout.insertLayout(0, top_bar_layout) # Insert this layout at the top of the main layout

        # Set initial theme based on saved settings or default
        self.apply_theme()

    def show_player(self):
        """
        Shows the PlayerWindow and hides the main application window.

        Creates an instance of PlayerWindow, displays it, and then hides
        the current (MusicovaApp) window.
        """
        # Hide the main window and show the player window
        self.player_window = PlayerWindow(self) # Pass self as parent for theme access
        self.player_window.show()
        self.hide()

    def toggle_theme(self):
        """
        Toggles the application theme between dark and light mode.

        Updates the internal dark_mode state, saves the preference,
        changes the theme button icon, and applies the theme to both
        the main window and the player window (if it exists).
        """
        self.dark_mode = not self.dark_mode
        self.settings.setValue('dark_mode', self.dark_mode) # Save the new theme preference
        self.theme_button.setText('☀️' if self.dark_mode else '🌙') # Update button icon
        self.apply_theme()
        # Update player window theme if it exists and is visible
        if hasattr(self, 'player_window') and self.player_window is not None and self.player_window.isVisible():
            self.player_window.apply_theme()

    def apply_theme(self):
        """
        Applies the current theme (dark or light) to the main window.

        Sets the stylesheet for the main window and its child widgets
        based on the self.dark_mode flag. This includes background colors,
        text colors, and button styles.
        """
        if self.dark_mode:
            # Apply dark theme stylesheet
            self.setStyleSheet("""
                QMainWindow, QWidget {
                    background-color: #1a1a1a;
                    color: white;
                }
            """)
            self.theme_button.setStyleSheet("""
                QPushButton {
                    background-color: #3d3d3d; /* --button-bg in dark mode */
                    color: #ffffff; /* --button-text in dark mode */
                    border: none;
                    border-radius: 20px; /* 50% radius for 40x40px button */
                    font-size: 20px;
                }
                QPushButton:hover {
                    background-color: #4a4a4a; /* Slightly lighter for hover */
                }
            """)
            if self.centralWidget().findChild(QPushButton, 'access_button'):
                self.centralWidget().findChild(QPushButton, 'access_button').setStyleSheet("""
                    QPushButton {
                        background-color: #3d3d3d; /* --button-bg dark */
                        color: #ffffff; /* --button-text dark */
                        border: none;
                        border-radius: 25px;
                        padding: 15px 30px;
                        font-family: 'DynaPuff';
                        font-size: 18px; /* Close to 1.2rem */
                        font-weight: bold; /* Close to 600 */
                    }
                    QPushButton:hover {
                        background-color: #4a4a4a; /* Slightly lighter hover for dark mode */
                        transform: translateY(-2px); /* Mimic web hover */
                    }
                """)
        else:
            self.setStyleSheet("""
                QMainWindow, QWidget {
                    background-color: blueviolet; /* Default background for light mode */
                    color: black; /* Default text color for light mode */
                }
            """)
            self.theme_button.setStyleSheet("""
                QPushButton {
                    background-color: white; /* --button-bg in light mode (example from CSS) */
                    color: blueviolet; /* --button-text in light mode (example from CSS) */
                    border: none;
                    border-radius: 20px; /* 50% radius for 40x40px button */
                    font-size: 20px;
                }
                QPushButton:hover {
                    background-color: #f0f0f0; /* --hover-bg in light mode */
                }
            """)
            if self.centralWidget().findChild(QPushButton, 'access_button'):
                self.centralWidget().findChild(QPushButton, 'access_button').setStyleSheet("""
                    QPushButton {
                        background-color: white; /* --button-bg light */
                        color: blueviolet; /* --button-text light */
                        border: none;
                        border-radius: 25px;
                        padding: 15px 30px;
                        font-family: 'DynaPuff';
                        font-size: 18px;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background-color: #f0f0f0; /* --hover-bg light (example from CSS) */
                        transform: translateY(-2px); /* Mimic web hover */
                    }
                """)

class PlayerWindow(QMainWindow):
    """
    The music player interface window.

    Handles playlist management, audio playback, UI for player controls,
    and theme synchronization with the main MusicovaApp. It displays imported
    music tracks as interactive cards, each with individual playback controls,
    progress bar, and volume slider.
    """
    def __init__(self, parent=None):
        """
        Initializes the PlayerWindow.

        Args:
            parent (MusicovaApp, optional): Reference to the main application
                                            window, used for theme synchronization.
                                            Defaults to None.

        Sets up the player window, initializes an empty playlist, and calls
        init_ui to create the user interface.
        """
        super().__init__(parent)
        self.parent = parent # Store reference to parent (MusicovaApp) for theme access
        self.playlist = [] # List to store file paths of tracks
        self.current_player = None # To keep track of the currently active QMediaPlayer (not used in current card-based design)
        self.init_ui()

    def init_ui(self):
        """
        Initializes the user interface elements for the player window.

        Sets the window title, minimum size, and creates layouts for
        import controls, track display (cards), and navigation buttons.
        It includes a title, import options, a scrollable area for track cards,
        a back button, and a theme toggle button.
        """
        self.setWindowTitle('Musicova - Player')
        self.setMinimumSize(800, 600)

        # Initialize grid layout attributes
        self.current_row = 0
        self.current_col = 0
        self.max_columns = 1  # Number of cards per row

        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Unused QMediaPlayer instance removed. Playback is per-card.
        # self.media_player = QMediaPlayer()

        # Add title label for the player window
        self.title_label = QLabel('Musicova Player')
        self.title_label.setStyleSheet('font-family: "DynaPuff", sans-serif; font-size: 100px; font-weight: bold;')
        self.title_label.setAlignment(Qt.AlignCenter)

        # Add import controls container (ComboBox for type, Import button)
        self.import_container = QWidget() # Container for import controls
        import_layout = QHBoxLayout(self.import_container)
        import_layout.setAlignment(Qt.AlignCenter)
        import_layout.setSpacing(10)

        self.file_select = QComboBox() # ComboBox to choose import type (folder/file)
        self.file_select.setObjectName("file_select_player") # For styling
        self.file_select.addItem('Select import type')
        self.file_select.addItem('Choose Folder')
        self.file_select.addItem('Choose File')
        self.file_select.setFixedWidth(200)
        import_layout.addWidget(self.file_select)

        self.import_button = QPushButton('Import') # Button to trigger file dialog
        self.import_button.setObjectName("import_button_player") # For styling
        self.import_button.setFixedWidth(100)
        self.import_button.clicked.connect(self.import_files) # Connect to import_files method
        import_layout.addWidget(self.import_button)

        # Add Clear Playlist button
        self.clear_playlist_button = QPushButton('Clear Playlist')
        self.clear_playlist_button.setObjectName("clear_playlist_button_player") # For styling
        self.clear_playlist_button.setFixedWidth(150) # Adjust width as needed
        self.clear_playlist_button.clicked.connect(self.clear_playlist) # Connect to clear_playlist method
        import_layout.addWidget(self.clear_playlist_button)

        layout.addWidget(self.import_container) # Add import controls to the main layout

        # Create cards container with grid layout for displaying track cards
        self.cards_container = QWidget() # Container for all track cards
        self.cards_layout = QGridLayout(self.cards_container) # Grid layout for cards
        self.cards_layout.setSpacing(20)
        self.cards_layout.setAlignment(Qt.AlignCenter) # Center cards if space allows
        
        # Add cards container to a scroll area to handle many tracks
        cards_scroll = QScrollArea()
        cards_scroll.setWidgetResizable(True) # Allow widget within scroll area to resize
        cards_scroll.setWidget(self.cards_container) # Put the cards container inside the scroll area
        cards_scroll.setMinimumHeight(400) # Minimum height for the scrollable area
        cards_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded) # Show scrollbars only when needed
        cards_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        layout.addWidget(cards_scroll) # Add scrollable cards area to the main layout
        
        # Dictionary to store media players and their associated controls for each track
        self.track_players = {} # Key: file_path, Value: dict of player, progress_slider, etc.

        # Create Back button and Theme toggle button
        self.back_button = QPushButton('Back to Home')
        self.back_button.setObjectName("back_button_player") # For styling
        self.back_button.clicked.connect(self.go_back) # Connect to go_back method

        self.theme_button = QPushButton('🌙') # Initial icon, will be updated by apply_theme
        self.theme_button.setFixedSize(40, 40)
        self.theme_button.clicked.connect(self.parent.toggle_theme) # Connect to parent's (MusicovaApp) toggle_theme

        # Layout for top controls (Back button and Theme button)
        top_controls_layout = QHBoxLayout()
        top_controls_layout.addWidget(self.back_button) # Back button on the left
        top_controls_layout.addStretch(1) # Push theme button to the right
        top_controls_layout.addWidget(self.theme_button) # Theme button on the right

        # Add widgets to main layout in the desired order
        layout.addLayout(top_controls_layout) # Top bar with back and theme buttons
        layout.addWidget(self.title_label) # "Musicova Player" title
        layout.addWidget(self.import_container) # Import controls
        layout.addWidget(cards_scroll) # Scrollable area for track cards

        # Apply the current theme to the player window
        self.apply_theme()

    def import_files(self):
        """
        Handles the selection of audio files or folders to import.

        Clears the current playlist, then opens a file dialog based on the
        user's selection in the `file_select` QComboBox (either 'Choose Folder'
        or 'Choose File'). Adds valid audio files (.mp3, .wav, .ogg) to the playlist.
        Finally, updates the visibility of UI elements.
        """
        # Clear existing playlist before importing new files
        self.clear_playlist()

        selected_option = self.file_select.currentText()
        if selected_option == 'Choose Folder':
            folder = QFileDialog.getExistingDirectory(self, 'Select Folder')
            if folder: # Check if a folder was actually selected
                for root, _, files in os.walk(folder): # Walk through the directory tree
                    for file in files:
                        if file.lower().endswith(('.mp3', '.wav', '.ogg')): # Check for supported audio file extensions
                            self.add_to_playlist(os.path.join(root, file))
        elif selected_option == 'Choose File':
            file, _ = QFileDialog.getOpenFileName(self, 'Select File', '', 'Audio Files (*.mp3 *.wav *.ogg)')
            if file: # Check if a file was actually selected
                self.add_to_playlist(file)

        # Update import controls and cards container visibility
        self.update_import_controls_visibility()

    def clear_playlist(self):
        """
        Clears the current playlist and resets the player UI.

        Stops all currently playing tracks, disposes of their media players,
        clears the internal playlist data structure, and removes all track
        cards from the UI. Resets the grid layout for new cards.
        """
        # Clear the playlist array
        self.playlist.clear()

        # Stop and clean up all media players associated with tracks
        for controls in self.track_players.values():
            controls['player'].stop()
            controls['player'].deleteLater() # Ensure QMediaPlayer objects are properly cleaned up

        # Clear the dictionary holding track players and controls
        self.track_players.clear()

        # Reset grid layout position trackers for new cards
        self.current_row = 0
        self.current_col = 0

        # Remove all widgets (track cards) from the cards layout
        while self.cards_layout.count():
            item = self.cards_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater() # Ensure card widgets are properly cleaned up

        # Update the visibility of import controls and cards container
        self.update_import_controls_visibility()

    def add_to_playlist(self, file_path):
        """
        Adds an individual audio file to the playlist and creates its UI card.

        The card includes:
        - Album art placeholder.
        - Track name.
        - Time display (current/total).
        - Progress slider.
        - Play/Pause, Previous, Next, and Remove buttons.
        - Volume slider.

        A new QMediaPlayer instance is created for this track and all UI elements
        are connected to appropriate signals/slots. The card is added to a grid layout.

        Args:
            file_path (str): The absolute path to the audio file.
        """
        # Normalize file path to use forward slashes consistently for internal use
        file_path = file_path.replace('\\', '/')
        self.playlist.append(file_path)
        
        # Create player card widget
        player_card = QWidget()
        player_card.setObjectName('player_card') # For styling based on theme
        player_card.setFixedWidth(300) # Fixed width for card
        player_card.setMinimumHeight(400) # Minimum height for card content
        # Default card style (can be overridden by theme in apply_theme)
        player_card.setStyleSheet("""
            QWidget#player_card {
                background-color: #2a2a2a; /* Default darkish background */
                border-radius: 20px;
                padding: 20px;
                color: white; /* Default text color */
            }
        """)
        
        card_layout = QVBoxLayout(player_card) # Vertical layout for card content
        
        # Add album art placeholder (simple colored box)
        album_art = QLabel()
        album_art.setFixedSize(200, 200)
        album_art.setStyleSheet('background-color: blueviolet; border-radius: 10px;') # Placeholder style
        album_art.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(album_art, alignment=Qt.AlignCenter)
        
        # Add track name label
        track_name = os.path.basename(file_path) # Display only the file name
        track_label = QLabel(track_name)
        track_label.setObjectName("track_label_card") # Set object name for QSS
        # track_label.setStyleSheet('color: white; font-weight: bold; font-size: 14px;') # Style now handled by QSS
        track_label.setAlignment(Qt.AlignCenter)
        track_label.setWordWrap(True) # Wrap text if name is too long
        card_layout.addWidget(track_label)
        
        # Add progress bar (QSlider) and time labels (0:00 / X:XX)
        progress_container = QWidget() # Container for progress elements
        progress_layout = QHBoxLayout(progress_container) # Horizontal layout for time_current | slider | time_total
        
        time_current = QLabel('0:00') # Label for current playback time
        time_current.setObjectName("time_label_card") # Set object name for QSS
        # time_current.setStyleSheet('color: white;') # Style now handled by QSS
        progress_slider = QSlider(Qt.Horizontal) # Slider for track progress
        # Styling for progress_slider is now handled globally in apply_theme by QSlider::groove:horizontal etc.
        
        time_total = QLabel('0:00') # Label for total track duration
        time_total.setObjectName("time_label_card") # Set object name for QSS
        # time_total.setStyleSheet('color: white;') # Style now handled by QSS
        
        progress_layout.addWidget(time_current)
        progress_layout.addWidget(progress_slider)
        progress_layout.addWidget(time_total)
        
        card_layout.addWidget(progress_container) # Add progress container to card
        
        # Add playback controls (Play/Pause button)
        controls_container = QWidget() # Container for control buttons
        controls_layout = QHBoxLayout(controls_container) # Horizontal layout for buttons
        controls_layout.setSpacing(10) # Reduced spacing for more buttons
        
        # Define icon paths (ideally at module level or class level)
        # For this change, defining them locally for clarity of what's being used.
        # Assume ICONS_DIR is defined appropriately earlier, e.g., os.path.join(os.path.dirname(__file__), 'Icons')
        # For the purpose of this diff, I'll hardcode the string for now.
        # Later, I'll add the ICONS_DIR definition.
        play_icon_path = os.path.join(os.path.dirname(__file__), 'Icons', 'r5qa5pfzfndm7bro859.svg')
        # pause_icon_path = os.path.join(os.path.dirname(__file__), 'Icons', '5dd3gw6mlhjm7brpg84.svg') # Used in play_pause
        prev_icon_path = os.path.join(os.path.dirname(__file__), 'Icons', '10b81wv7wlmm7brpwyt.svg')
        # For Next icon, we need to flip prev_icon. QPixmap can do this.
        
        prev_button_card = QPushButton()
        prev_button_card.setObjectName("prev_button_card")
        prev_button_card.setIcon(QIcon(PREV_ICON_PATH)) # Use global path
        prev_button_card.setIconSize(prev_button_card.sizeHint() / 1.5)
        prev_button_card.setFixedSize(40, 40)
        # prev_button_card.setStyleSheet("...") # Styling moved to apply_theme

        play_button = QPushButton()
        play_button.setObjectName("play_button_card")
        play_button.setIcon(QIcon(PLAY_ICON_PATH)) # Use global path
        play_button.setIconSize(play_button.sizeHint())
        play_button.setFixedSize(50, 50)
        # play_button.setStyleSheet("...") # Styling moved to apply_theme

        next_button_card = QPushButton()
        next_button_card.setObjectName("next_button_card")
        next_pixmap = QPixmap(PREV_ICON_PATH) # Use global path
        mirrored_next_pixmap = next_pixmap.transformed(QTransform().scale(-1, 1))
        next_button_card.setIcon(QIcon(mirrored_next_pixmap))
        next_button_card.setIconSize(next_button_card.sizeHint() / 1.5)
        next_button_card.setFixedSize(40, 40)
        # next_button_card.setStyleSheet("...") # Styling moved to apply_theme

        # Create a dedicated QMediaPlayer for this track
        media_player = QMediaPlayer()
        content = QMediaContent(QUrl.fromLocalFile(file_path)) # Create QMediaContent from file path
        media_player.setMedia(content) # Set the media for this player instance
        
        # Store the player and its associated UI controls in the track_players dictionary
        # Ensure prev_button_card and next_button_card are included from above
        self.track_players[file_path].update({
            'player': media_player,
            'progress': progress_slider,
            'time_current': time_current,
            'time_total': time_total,
            'play_button': play_button,
            'card_widget': player_card
        })
        
        # Connect signals from the media player and UI controls to appropriate methods
        # Use lambdas to pass file_path to handlers, identifying which track's controls/player to update
        media_player.durationChanged.connect(lambda duration, fp=file_path: self.update_duration(duration, fp))
        media_player.positionChanged.connect(lambda position, fp=file_path: self.update_position(position, fp))
        progress_slider.sliderPressed.connect(lambda fp=file_path: self.on_slider_pressed(fp))
        progress_slider.sliderReleased.connect(lambda fp=file_path: self.on_slider_released(fp))
        progress_slider.valueChanged.connect(lambda value, fp=file_path: self.on_slider_value_changed(value, fp))
        play_button.clicked.connect(lambda fp=file_path: self.play_pause(fp))
        prev_button_card.clicked.connect(lambda _, fp=file_path: self.play_adjacent_track(fp, direction=-1))
        next_button_card.clicked.connect(lambda _, fp=file_path: self.play_adjacent_track(fp, direction=1))
        
        # Add buttons to controls layout
        controls_layout.addStretch(1)
        controls_layout.addWidget(prev_button_card)
        controls_layout.addWidget(play_button)
        controls_layout.addWidget(next_button_card)
        controls_layout.addStretch(1)
        
        card_layout.addWidget(controls_container) # Add controls container to card

        # Add Volume Slider
        volume_slider = QSlider(Qt.Horizontal)
        volume_slider.setObjectName("volume_slider_card") # Set object name for QSS
        volume_slider.setRange(0, 100) # QMediaPlayer volume is 0-100
        volume_slider.setValue(100)    # Default volume 100%
        # volume_slider.setStyleSheet(""" # Styling moved to apply_theme
            QSlider::groove:horizontal {
              background: #555555; /* Darker groove for visibility */
              height: 8px;
              border-radius: 4px;
            }
            QSlider::sub-page:horizontal {
                background: #8a2be2; /* Theme color for played part */
                height: 8px;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #cccccc; /* Light handle for visibility */
                width: 16px;
                height: 16px;
                margin: -4px 0; /* Center handle on groove */
                border-radius: 8px;
            }
        """)
        card_layout.addWidget(volume_slider)

        # Store volume slider in track_players for access
        self.track_players[file_path]['volume_slider'] = volume_slider
        
        # Connect volume slider to media player's volume
        volume_slider.valueChanged.connect(lambda value, p=media_player: p.setVolume(value))

        # Add Remove Button to card
        remove_button = QPushButton('🗑️') # Using an emoji for simplicity
        remove_button.setObjectName("remove_button_card")
        remove_button.setFixedSize(30, 30) # Small button
        # remove_button.setStyleSheet("...") # Styling moved to apply_theme
        # remove_button.clicked.connect(lambda checked, fp=file_path, card_widget=player_card: self.remove_track(fp, card_widget))
        # The above lambda captures player_card at the time of connection.
        # It's better to find the card dynamically or ensure the card itself is passed correctly.
        # For now, let's connect it and refine `remove_track` to handle finding the card if needed, or ensure `player_card` is the correct reference.
        remove_button.clicked.connect(lambda _, fp=file_path: self.remove_track(fp))
        card_layout.addWidget(remove_button, alignment=Qt.AlignRight) # Add to card layout

        # Add the fully constructed player card to the grid layout
        self.cards_layout.addWidget(player_card, self.current_row, self.current_col)
        self.current_col += 1
        # If max columns reached, move to the next row
        if self.current_col >= self.max_columns:
            self.current_col = 0
            self.current_row += 1

    def update_import_controls_visibility(self):
        """
        Updates the visibility of UI elements based on the playlist state.

        The import controls (file/folder selection, import button) are always visible.
        The container for track cards (`cards_container`) is shown only if the
        playlist is not empty, otherwise it's hidden.
        """
        # Import controls (selection dropdown and button) should always be visible
        self.import_container.setVisible(True)
        # Show or hide the cards container based on whether the playlist has tracks
        self.cards_container.setVisible(len(self.playlist) > 0)

    def apply_theme(self):
        """
        Applies the current theme (dark or light) to the player window.

        Sets the stylesheet for the player window and its child widgets
        (buttons, combo boxes, scrollbars, sliders, player cards) based on
        the `self.parent.dark_mode` flag (inherited from MusicovaApp).
        Updates the theme button icon accordingly.
        """
        if self.parent.dark_mode:
            # Apply dark theme stylesheet
            self.setStyleSheet("""
                QMainWindow, QWidget {
                    background-color: #1a1a1a;
                    color: white;
                }
                QPushButton {
                    background-color: #3d3d3d;
                    color: white;
                    border: none;
                    border-radius: 25px;
                    padding: 15px 30px;
                    font-family: 'DynaPuff';
                    font-size: 18px; /* Matches .musicova-title button, .file-select */
                    font-weight: 600; /* Matches .musicova-title button, .file-select */
                }
                QPushButton:hover {
                    background-color: #4a4a4a; /* Darker hover consistent with MusicovaApp */
                    /* transform: translateY(-2px); QSS doesn't support transform directly */
                }
                QComboBox {
                    background-color: #3d3d3d;
                    color: white;
                    border: none;
                    border-radius: 25px;
                    padding: 15px 30px; /* Matches .file-select */
                    font-family: 'DynaPuff';
                    font-size: 18px; /* Matches .file-select */
                    font-weight: 600; /* Matches .file-select */
                }
                QComboBox QAbstractItemView {
                    background-color: #2d2d2d;
                    color: white;
                    selection-background-color: #3d3d3d;
                }
                QScrollArea, QScrollBar {
                    background-color: #1a1a1a;
                    border: none;
                }
                QScrollBar:vertical {
                    width: 10px;
                    background: #1a1a1a;
                }
                QScrollBar::handle:vertical {
                    background: #3d3d3d;
                    border-radius: 5px;
                }
                QScrollBar:horizontal {
                    height: 10px;
                    background: #1a1a1a;
                }
                QScrollBar::handle:horizontal {
                    background: #3d3d3d;
                    border-radius: 5px;
                }
                QSlider::groove:horizontal {
                    background: #404040;
                    height: 4px;
                    border-radius: 2px;
                }
                QSlider::handle:horizontal {
                    background: #8a2be2;
                    width: 12px;
                    margin: -4px 0;
                    border-radius: 6px;
                }
                QSlider::sub-page:horizontal {
                    background: #8a2be2; /* --progress-fill dark */
                    border-radius: 2px;
                }
                /* Style for Volume QSlider */
                QSlider[objectName="volume_slider_card"]::groove:horizontal {
                    background: #404040; /* --progress-bg dark */
                    height: 8px;
                    border-radius: 4px;
                }
                QSlider[objectName="volume_slider_card"]::handle:horizontal {
                    background: #8a2be2; /* --progress-fill dark */
                    width: 16px;
                    height: 16px;
                    margin: -4px 0;
                    border-radius: 8px;
                }
                QSlider[objectName="volume_slider_card"]::sub-page:horizontal {
                    background: #8a2be2; /* --progress-fill dark */
                    border-radius: 4px;
                }

                QWidget#player_card {
                    background-color: #2d2d2d; /* --card-bg dark */
                    border-radius: 15px;
                    padding: 20px;
                    /* box-shadow not directly supported well in QSS for all platforms */
                }
                /* General QLabel color for the window */
                QLabel {
                    color: white; /* --text-color dark */
                }
                /* Specific labels within player cards */
                QWidget#player_card QLabel[objectName="track_label_card"] {
                    color: white; /* --text-color dark */
                    font-family: 'DynaPuff';
                    font-size: 18px; /* Approx 1.4rem, adjust as needed */
                    font-weight: 600;
                }
                QWidget#player_card QLabel[objectName="time_label_card"] {
                    color: #cccccc; /* Lighter grey for time, similar to web's #666 on dark */
                    font-size: 12px; /* Approx 0.9rem */
                }
                QWidget#player_card[active="true"] {
                    border: 2px solid #8a2be2; /* --progress-fill dark */
                }
                /* Card Control Buttons - Dark Mode */
                QWidget#player_card QPushButton[objectName="play_button_card"] {
                    background-color: #8a2be2; /* Theme accent */
                    border-radius: 25px; /* For 50x50 button */
                }
                QWidget#player_card QPushButton[objectName="play_button_card"]:hover {
                    background-color: #9932cc; /* Darker accent */
                }
                QWidget#player_card QPushButton[objectName="prev_button_card"],
                QWidget#player_card QPushButton[objectName="next_button_card"] {
                    background-color: #4a4a4a; /* Darker grey */
                    border-radius: 20px; /* For 40x40 button */
                }
                QWidget#player_card QPushButton[objectName="prev_button_card"]:hover,
                QWidget#player_card QPushButton[objectName="next_button_card"]:hover {
                    background-color: #5a5a5a;
                }
                QWidget#player_card QPushButton[objectName="remove_button_card"] {
                    background-color: #5a2d2d; /* Dark redish */
                    color: white;
                    font-size: 15px;
                    border-radius: 15px; /* For 30x30 button */
                }
                QWidget#player_card QPushButton[objectName="remove_button_card"]:hover {
                    background-color: #7a3d3d;
                }
            """)
            self.theme_button.setText('☀️')
            self.theme_button.setStyleSheet("""
                QPushButton {
                    background-color: #3d3d3d; /* --button-bg dark */
                    color: #ffffff; /* --button-text dark */
                    border: none;
                    border-radius: 20px;
                    font-size: 20px;
                }
                QPushButton:hover {
                    background-color: #4a4a4a;
                }
            """)
            self.back_button.setStyleSheet("""
                QPushButton {
                    background-color: #3d3d3d; /* --button-bg dark */
                    color: #ffffff; /* --button-text dark */
                    border: none;
                    border-radius: 25px; /* from .back-button */
                    padding: 12px 24px; /* from .back-button */
                    font-family: "DynaPuff", sans-serif; /* from .back-button */
                    font-size: 16px; /* 1rem from .back-button (assuming 1rem=16px) */
                    font-weight: 600; /* from .back-button */
                }
                QPushButton:hover {
                    background-color: #4a4a4a; /* Consistent darker hover */
                }
            """)
            # Common style for file_select
            file_select_style = """
                QComboBox {{
                    border: none;
                    border-radius: 25px;
                    padding: 15px 30px;
                    font-family: "DynaPuff", sans-serif;
                    font-size: 18px; /* Approx 1.2rem */
                    font-weight: 600;
                }}
                QComboBox QAbstractItemView {{ /* Style for the dropdown list itself */
                    border: 1px solid #3d3d3d; /* Or themed border */
                    /* Other dropdown styles can be added if needed */
                }}
            """
            self.file_select.setStyleSheet(file_select_style + """
                QComboBox {
                    background-color: #3d3d3d; /* --button-bg dark */
                    color: #ffffff; /* --button-text dark */
                }
                QComboBox:hover {
                    background-color: #4a4a4a; /* Consistent hover */
                }
                QComboBox QAbstractItemView {
                    background-color: #2d2d2d;
                    color: white;
                    selection-background-color: #3d3d3d;
                }
            """)
            # Common style for import_button
            import_button_style = """
                QPushButton {{
                    border: none;
                    border-radius: 25px;
                    padding: 15px 30px;
                    font-family: "DynaPuff", sans-serif;
                    font-size: 18px; /* Approx 1.2rem */
                    font-weight: 600;
                }}
            """
            self.import_button.setStyleSheet(import_button_style + """
                QPushButton {
                    background-color: #3d3d3d; /* --button-bg dark */
                    color: #ffffff; /* --button-text dark */
                }
                QPushButton:hover {
                    background-color: #4a4a4a; /* Consistent hover */
                }
            """)
            # Style for clear_playlist_button (dark mode)
            self.clear_playlist_button.setStyleSheet(import_button_style + """
                QPushButton {
                    background-color: #3d3d3d;
                    color: #ffffff;
                    margin-left: 10px; /* Add some space from the import button */
                }
                QPushButton:hover {
                    background-color: #4a4a4a;
                }
            """)
        else:
            self.setStyleSheet("""
                QMainWindow, QWidget {
                    background-color: blueviolet; /* Light theme main background */
                    color: black; /* Light theme main text color */
                }
                QPushButton {
                    background-color: white; /* Light theme button background */
                    color: blueviolet; /* Light theme button text color */
                    border: none;
                    border-radius: 25px;
                    padding: 15px 30px;
                    font-family: 'DynaPuff';
                    font-size: 18px; /* Matches .musicova-title button, .file-select */
                    font-weight: 600; /* Matches .musicova-title button, .file-select */
                }
                QPushButton:hover {
                    background-color: #f0f0f0; /* --hover-bg light */
                    /* transform: translateY(-2px); QSS doesn't support transform */
                }
                QComboBox {
                    background-color: white;
                    color: blueviolet;
                    border: none;
                    border-radius: 25px;
                    padding: 15px 30px; /* Matches .file-select */
                    font-family: 'DynaPuff';
                    font-size: 18px; /* Matches .file-select */
                    font-weight: 600; /* Matches .file-select */
                }
                QComboBox QAbstractItemView {
                    background-color: white;
                    color: blueviolet;
                    selection-background-color: #f0f0f0;
                }
                QScrollArea, QScrollBar {
                    background-color: blueviolet;
                    border: none;
                }
                QScrollBar:vertical {
                    width: 10px;
                    background: blueviolet;
                }
                QScrollBar::handle:vertical {
                    background: white;
                    border-radius: 5px;
                }
                QScrollBar:horizontal {
                    height: 10px;
                    background: blueviolet;
                }
                QScrollBar::handle:horizontal {
                    background: white;
                    border-radius: 5px;
                }
                QSlider::groove:horizontal {
                    background: #e0e0e0;
                    height: 4px;
                    border-radius: 2px;
                }
                QSlider::handle:horizontal {
                    background: blueviolet;
                    width: 12px;
                    margin: -4px 0;
                    border-radius: 6px;
                }
                QSlider::sub-page:horizontal {
                    background: blueviolet; /* --progress-fill light */
                    border-radius: 2px;
                }
                /* Style for Volume QSlider */
                QSlider[objectName="volume_slider_card"]::groove:horizontal {
                    background: #e0e0e0; /* --progress-bg light */
                    height: 8px;
                    border-radius: 4px;
                }
                QSlider[objectName="volume_slider_card"]::handle:horizontal {
                    background: blueviolet; /* --progress-fill light */
                    width: 16px;
                    height: 16px;
                    margin: -4px 0;
                    border-radius: 8px;
                }
                QSlider[objectName="volume_slider_card"]::sub-page:horizontal {
                    background: blueviolet; /* --progress-fill light */
                    border-radius: 4px;
                }

                QWidget#player_card {
                    background-color: white; /* --card-bg light */
                    border-radius: 15px;
                    padding: 20px;
                }
                QLabel {
                    color: black; /* --text-color light */
                }
                QWidget#player_card QLabel[objectName="track_label_card"] {
                    color: black; /* --text-color light */
                    font-family: 'DynaPuff';
                    font-size: 18px;
                    font-weight: 600;
                }
                QWidget#player_card QLabel[objectName="time_label_card"] {
                    color: #333333; /* Darker grey for time, similar to web's #666 on light */
                    font-size: 12px;
                }
                QWidget#player_card[active="true"] {
                    border: 2px solid blueviolet; /* --progress-fill light */
                }
                /* Card Control Buttons - Light Mode */
                QWidget#player_card QPushButton[objectName="play_button_card"] {
                    background-color: blueviolet;
                    border-radius: 25px;
                }
                QWidget#player_card QPushButton[objectName="play_button_card"]:hover {
                    background-color: #9370DB; /* Lighter purple */
                }
                QWidget#player_card QPushButton[objectName="prev_button_card"],
                QWidget#player_card QPushButton[objectName="next_button_card"] {
                    background-color: #e0e0e0; /* Light grey */
                    border-radius: 20px;
                }
                QWidget#player_card QPushButton[objectName="prev_button_card"]:hover,
                QWidget#player_card QPushButton[objectName="next_button_card"]:hover {
                    background-color: #d0d0d0;
                }
                QWidget#player_card QPushButton[objectName="remove_button_card"] {
                    background-color: #ff7f7f; /* Light red */
                    color: white;
                    font-size: 15px;
                    border-radius: 15px;
                }
                QWidget#player_card QPushButton[objectName="remove_button_card"]:hover {
                    background-color: #ff6347; /* Tomato */
                }
            """)
            self.theme_button.setText('🌙')
            self.theme_button.setStyleSheet("""
                QPushButton {
                    background-color: white; /* --button-bg light */
                    color: blueviolet; /* --button-text light */
                    border: none;
                    border-radius: 20px;
                    font-size: 20px;
                }
                QPushButton:hover {
                    background-color: #f0f0f0; /* --hover-bg light */
                }
            """)
            # Common style for file_select
            file_select_style = """
                QComboBox {{
                    border: none;
                    border-radius: 25px;
                    padding: 15px 30px;
                    font-family: "DynaPuff", sans-serif;
                    font-size: 18px; /* Approx 1.2rem */
                    font-weight: 600;
                }}
                QComboBox QAbstractItemView {{ /* Style for the dropdown list itself */
                    border: 1px solid #3d3d3d; /* Or themed border */
                    /* Other dropdown styles can be added if needed */
                }}
            """
            self.file_select.setStyleSheet(file_select_style + """
                QComboBox {
                    background-color: white; /* --button-bg light */
                    color: blueviolet; /* --button-text light */
                }
                QComboBox:hover {
                    background-color: #f0f0f0; /* --hover-bg light */
                }
                QComboBox QAbstractItemView {
                    background-color: white;
                    color: blueviolet;
                    selection-background-color: #f0f0f0;
                }
            """)
            # Common style for import_button
            import_button_style = """
                QPushButton {{
                    border: none;
                    border-radius: 25px;
                    padding: 15px 30px;
                    font-family: "DynaPuff", sans-serif;
                    font-size: 18px; /* Approx 1.2rem */
                    font-weight: 600;
                }}
            """
            self.import_button.setStyleSheet(import_button_style + """
                QPushButton {
                    background-color: white; /* --button-bg light */
                    color: blueviolet; /* --button-text light */
                }
                QPushButton:hover {
                    background-color: #f0f0f0; /* --hover-bg light */
                }
            """)
            self.back_button.setStyleSheet("""
                QPushButton {
                    background-color: white; /* --button-bg light */
                    color: blueviolet; /* --button-text light */
                    border: none;
                    border-radius: 25px;
                    padding: 12px 24px;
                    font-family: "DynaPuff", sans-serif;
                    font-size: 16px;
                    font-weight: 600;
                }
                QPushButton:hover {
                    background-color: #f0f0f0; /* --hover-bg light (example from CSS) */
                }
            """)
            # Style for clear_playlist_button (light mode)
            self.clear_playlist_button.setStyleSheet(import_button_style + """
                QPushButton {
                    background-color: white;
                    color: blueviolet;
                    margin-left: 10px; /* Add some space from the import button */
                }
                QPushButton:hover {
                    background-color: #f0f0f0;
                }
            """)

    # Note: play_track, play_previous, and play_next methods using self.media_player
    # are not compatible with the current card-based multi-player design.
    # Each card has its own QMediaPlayer. These methods would need significant
    # refactoring to work with the current architecture (e.g., by managing
    # a global "current track" reference and interacting with its specific card's player).
    # For now, they are documented as per their original intent but highlighted as problematic.

    def play_track(self, file_path):
        """
        Loads and plays a specific track using the window's main media player.

        NOTE: This method is NOT fully compatible with the current multi-player,
        card-based UI. It would attempt to use `self.media_player`, which is
        not the one associated with individual track cards.

        Args:
            file_path (str): The path to the audio file to play.
        """
        content = QMediaContent(QUrl.fromLocalFile(file_path))
        self.media_player.setMedia(content) # Uses the general PlayerWindow media player
        self.media_player.play()
        
        # This would require a dedicated label in PlayerWindow, not on a card
        # self.track_name_label.setText(os.path.basename(file_path)) 
        
        # These connections would also be to the general PlayerWindow media player
        # self.media_player.durationChanged.connect(self.update_duration)
        # self.media_player.positionChanged.connect(self.update_position)
        print(f"Attempting to play {file_path} with main player (may not be intended behavior with cards)")


    def update_duration(self, duration, file_path):
        """
        Updates the total duration display for a specific track's card.

        Args:
            duration (int): The total duration of the track in milliseconds.
            file_path (str): The path to the audio file, used as a key to find
                             the track's UI controls.
        """
        if file_path not in self.track_players: return # Guard against missing track
        controls = self.track_players[file_path]
        controls['progress'].setMaximum(duration) # Set slider's max value
        total_time = duration // 1000  # Convert milliseconds to seconds
        minutes = total_time // 60
        seconds = total_time % 60
        controls['time_total'].setText(f'{minutes}:{seconds:02d}') # Format as M:SS

    def update_position(self, position, file_path):
        """
        Updates the current playback position display (slider and time label)
        for a specific track's card.

        Args:
            position (int): The current playback position in milliseconds.
            file_path (str): The path to the audio file, used as a key to find
                             the track's UI controls.
        """
        if file_path not in self.track_players: return # Guard against missing track
        controls = self.track_players[file_path]
        # Only update slider value if the user is not currently dragging it
        if not controls['progress'].isSliderDown():
            controls['progress'].setValue(position)
        
        current_time = position // 1000  # Convert milliseconds to seconds
        minutes = current_time // 60
        seconds = current_time % 60
        controls['time_current'].setText(f'{minutes}:{seconds:02d}') # Format as M:SS

    def on_slider_pressed(self, file_path):
        """
        Handles the event when a track's progress slider is pressed by the user.

        If the track was playing, it's paused temporarily to allow smooth seeking.
        The state (playing/paused) is stored to resume correctly after release.

        Args:
            file_path (str): The path of the track whose slider was pressed.
        """
        if file_path not in self.track_players: return
        controls = self.track_players[file_path]
        # Store if player was playing before slider interaction
        self.was_playing = controls['player'].state() == QMediaPlayer.PlayingState
        if self.was_playing:
            controls['player'].pause() # Pause during seek

    def on_slider_released(self, file_path):
        """
        Handles the event when a track's progress slider is released by the user.

        Sets the media player's position to the slider's new value.
        If the track was playing before the slider was pressed, playback is resumed.

        Args:
            file_path (str): The path of the track whose slider was released.
        """
        if file_path not in self.track_players: return
        controls = self.track_players[file_path]
        controls['player'].setPosition(controls['progress'].value()) # Set player position to slider value
        if self.was_playing: # Resume playback if it was paused by on_slider_pressed
            controls['player'].play()
            self.was_playing = False # Reset flag

    def on_slider_value_changed(self, value, file_path):
        """
        Handles the event when a track's progress slider value changes
        *while the user is dragging it*.

        Updates the 'current time' label to reflect the slider's position in real-time.

        Args:
            value (int): The new value of the slider (playback position in ms).
            file_path (str): The path of the track whose slider value changed.
        """
        if file_path not in self.track_players: return
        controls = self.track_players[file_path]
        # Only update the time label if the slider is being actively dragged
        if controls['progress'].isSliderDown():
            current_time = value // 1000  # Convert milliseconds to seconds
            minutes = current_time // 60
            seconds = current_time % 60
            controls['time_current'].setText(f'{minutes}:{seconds:02d}')

    def play_pause(self, file_path):
        """
        Toggles playback (play or pause) for a specific track.

        Updates the play/pause button icon accordingly ('▶' for play, '⏸' for pause).

        Args:
            file_path (str): The path of the track to play or pause.
        """
        if file_path not in self.track_players: return # Guard against missing track
        controls = self.track_players[file_path]
        player = controls['player']
        play_button = controls['play_button']
        player_card_widget = play_button.parentWidget().parentWidget() # Access the player_card QWidget

        if player.state() == QMediaPlayer.PlayingState:
            player.pause()
            play_button.setText('▶') # Change icon to 'Play'
            player_card_widget.setProperty('active', False)
            self.style().unpolish(player_card_widget); self.style().polish(player_card_widget) # Refresh style
        else:
            # Pause other players and deactivate their cards
            for fp, other_controls in self.track_players.items():
                if fp != file_path and other_controls['player'].state() == QMediaPlayer.PlayingState:
                    other_controls['player'].pause()
                    other_controls['play_button'].setText('▶')
                    other_card_widget = other_controls['play_button'].parentWidget().parentWidget()
                    other_card_widget.setProperty('active', False)
                    self.style().unpolish(other_card_widget); self.style().polish(other_card_widget)

            player.play()
            play_button.setText('⏸') # Change icon to 'Pause'
            player_card_widget.setProperty('active', True)
            self.style().unpolish(player_card_widget); self.style().polish(player_card_widget) # Refresh style

    def remove_track(self, file_path):
        """
        Removes a track from the playlist and its UI card.

        Args:
            file_path (str): The path of the track to remove.
        """
        if file_path not in self.track_players:
            print(f"Track {file_path} not found in track_players.")
            return

        controls = self.track_players[file_path]
        player = controls['player']

        # Stop the player and release resources
        player.stop()
        player.setMedia(QMediaContent()) # Clear media content

        # Find the card widget to remove it from the layout
        # This requires iterating through the layout items or having a direct reference.
        # A more robust way is to store the card widget in self.track_players too.
        # For now, assuming self.track_players[file_path]['play_button'] exists and we can get parent widgets

        card_widget_to_remove = None
        # Iterate over cards_layout to find the widget associated with file_path
        for i in range(self.cards_layout.count()):
            item = self.cards_layout.itemAt(i)
            if item and item.widget():
                # This is a bit indirect. We need a reliable way to map file_path to its card widget.
                # Let's assume the 'play_button' is a good enough proxy to find its card.
                # This assumes the play_button is a direct child of a container, which is a child of the card.
                # Or, more simply, if we store the card_widget reference when creating it.
                # Let's modify add_to_playlist to store the card_widget.
                if 'card_widget' in controls and controls['card_widget'] == item.widget():
                     card_widget_to_remove = item.widget()
                     break

        if card_widget_to_remove:
            self.cards_layout.removeWidget(card_widget_to_remove)
            card_widget_to_remove.deleteLater() # Schedule the card widget for deletion
        else:
            print(f"Could not find card widget for {file_path} to remove from layout.")


        # Remove from internal data structures
        del self.track_players[file_path] # Remove entry from dict first
        player.deleteLater() # Now schedule the player object for deletion

        if file_path in self.playlist:
            self.playlist.remove(file_path)

        # Note: This doesn't currently re-flow the grid layout.
        # If that's desired, the items would need to be re-added or the layout managed differently.
        # For simplicity, removing leaves a gap. A QFlowLayout might handle this better if desired later.

        self.update_import_controls_visibility() # Update visibility if playlist becomes empty

    def play_adjacent_track(self, current_file_path, direction):
        """
        Plays the next or previous track in the playlist relative to the current track.

        Args:
            current_file_path (str): The file path of the currently reference track.
            direction (int): 1 for next track, -1 for previous track.
        """
        if not self.playlist:
            return

        try:
            current_index = self.playlist.index(current_file_path)
        except ValueError:
            print(f"Error: Current track {current_file_path} not found in playlist.")
            return

        # Stop and reset current track (if it's playing and its card exists)
        if current_file_path in self.track_players:
            current_controls = self.track_players[current_file_path]
            current_player = current_controls['player']
            if current_player.state() == QMediaPlayer.PlayingState:
                current_player.pause() # Pause instead of stop to potentially resume if user clicks back quickly
            current_player.setPosition(0) # Reset position
            current_controls['play_button'].setText('▶')
            current_card_widget = current_controls.get('card_widget')
            if current_card_widget:
                current_card_widget.setProperty('active', False)
                self.style().unpolish(current_card_widget); self.style().polish(current_card_widget)


        target_index = current_index + direction

        if 0 <= target_index < len(self.playlist):
            next_file_path = self.playlist[target_index]
            if next_file_path in self.track_players:
                # Call play_pause for the target track to handle playing and UI updates
                self.play_pause(next_file_path)
            else:
                print(f"Error: Target track {next_file_path} not found in track_players dictionary.")
        else:
            # Re-activate the current track's play button if we are at the boundary and not moving
            # This handles the case where user clicks next on last track or prev on first.
            if current_file_path in self.track_players:
                 current_controls = self.track_players[current_file_path]
                 # if current_controls['player'].state() != QMediaPlayer.PlayingState: # Only if it's not already playing
                 #    current_controls['play_button'].setText('▶') # Keep it as play, since nothing happened.
                 # No, if it was playing, it should resume being active if no move occurs
                 if current_controls['player'].state() == QMediaPlayer.PausedState : # If it was paused by us
                    current_card_widget = current_controls.get('card_widget')
                    if current_card_widget :
                        # self.play_pause(current_file_path) # This would replay it, not desired.
                        # We just want to make it look active if it was the one playing
                        # Actually, the play_pause logic will handle this. If it's paused, clicking play will make it active.
                        # The current state is fine. No need to auto-replay or force active state here if no move.
                        pass


    def go_back(self):
        """
        Returns to the main application window (MusicovaApp) from the player window.

        Stops all media players in the PlayerWindow, then shows the parent
        (MusicovaApp) window and closes the current (PlayerWindow).
        """
        # Stop all track players before going back
        for controls in self.track_players.values():
            if controls['player'].state() == QMediaPlayer.PlayingState:
                controls['player'].stop()
        
        # Show the main window (parent) and close this player window
        if self.parent:
            self.parent.show()
        self.close()

    def play_previous(self):
        """
        Plays the previous track in the playlist.

        NOTE: This method is NOT compatible with the current card-based UI
        as it relies on a single `self.media_player` and a linear playlist
        concept that doesn't directly map to individually controlled cards.
        It would require significant redesign to select and control the
        "previous" card's player.
        """
        if not self.playlist:
            return
        
        # This logic assumes a single media player and a global current track.
        # It won't work correctly with the card-based system.
        print("play_previous: Not implemented for card-based player.")
        # Example of what it might try to do (conceptually):
        # current_file = self.media_player.media().canonicalUrl().toLocalFile()
        # try:
        #     current_index = self.playlist.index(current_file)
        #     prev_index = (current_index - 1 + len(self.playlist)) % len(self.playlist) # Wrap around
        #     self.play_track(self.playlist[prev_index]) # This 'play_track' is also problematic
        # except ValueError:
        #     if self.playlist:
        #         self.play_track(self.playlist[-1]) # Play last track if current not found

    def play_next(self):
        """
        Plays the next track in the playlist.

        NOTE: This method is NOT compatible with the current card-based UI.
        Similar to `play_previous`, it assumes a single `self.media_player`
        and would need a redesign for the card system.
        """
        if not self.playlist:
            return
        
        # This logic assumes a single media player and a global current track.
        # It won't work correctly with the card-based system.
        print("play_next: Not implemented for card-based player.")
        # Example of what it might try to do (conceptually):
        # current_file = self.media_player.media().canonicalUrl().toLocalFile()
        # try:
        #     current_index = self.playlist.index(current_file)
        #     next_index = (current_index + 1) % len(self.playlist) # Wrap around
        #     self.play_track(self.playlist[next_index]) # This 'play_track' is also problematic
        # except ValueError:
        #     if self.playlist:
        #         self.play_track(self.playlist[0]) # Play first track if current not found

# The old play_previous and play_next methods are now removed by omitting them.

def main():
    """
    The main function to launch the Musicova application.

    Initializes the QApplication, creates an instance of MusicovaApp,
    shows the main window, and starts the application's event loop.
    """
    app = QApplication(sys.argv) # Create the PyQt application

    # Load custom font
    font_path = os.path.join(os.path.dirname(__file__), 'fonts', 'DynaPuff-Regular.ttf')
    font_id = QFontDatabase.addApplicationFont(font_path)
    if font_id == -1:
        print(f"Warning: Could not load font at {font_path}")
    else:
        font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
        print(f"Font '{font_family}' loaded successfully.")

    window = MusicovaApp() # Create the main application window
    window.show() # Display the window
    sys.exit(app.exec_()) # Start the event loop and exit when done

if __name__ == '__main__':
    # This ensures main() is called only when the script is executed directly
    main()

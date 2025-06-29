import sys
import os
import pygame # Keep pygame for audio playback
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QLabel, QSlider, QComboBox, QFileDialog,
                             QScrollArea, QStackedWidget, QFrame, QSpacerItem, QSizePolicy)
from PyQt5.QtGui import QFont, QPixmap, QImage, QIcon, QPalette, QColor, QPainter, QBrush
from PyQt5.QtCore import Qt, QSize, QTimer, QUrl, QRect
from PIL import Image # Keep PIL for image manipulation if needed before converting to QPixmap
from mutagen import File as MutagenFile # Keep mutagen for metadata

# FontAwesome Unicode characters (replace tkfontawesome)
FA_ICONS = {
    "play": "\uf04b",
    "pause": "\uf04c",
    "stop": "\uf04d", # Example, not used yet
    "backward-step": "\uf048", # Example
    "forward-step": "\uf051", # Example
    "trash-can": "\uf2ed",
    "moon": "\uf186",
    "sun": "\uf185",
    "arrow-left": "\uf060",
    "folder-open": "\uf07c", # Example for import
    "file-audio": "\uf1c7", # Example for import
}

# --- THEME_COLORS Definition (remains, will be used to generate QSS) ---
THEME_COLORS = {
    "light": {
        "bg": "blueviolet", "text": "black", "button_bg": "white", "button_text": "blueviolet",
        "title_text": "black", "card_bg": "white", "hover_bg": "#f0f0f0", "disabled_bg": "#cccccc",
        "progress_bg": "#e0e0e0", "progress_fill": "blueviolet", "font_family": "DynaPuff", # Ensure this font is available or use a common one
        "font_size_title": 48, "font_size_subtitle": 24, "font_size_button": 14,
        "font_size_player_title": 36, "font_size_track_name": 16, "font_size_time": 11,
        "font_size_icon_button": 14, # Adjusted for direct text rendering
    },
    "dark": {
        "bg": "#1a1a1a", "text": "white", "button_bg": "#3d3d3d", "button_text": "white",
        "title_text": "white", "card_bg": "#2d2d2d", "hover_bg": "#555555", "disabled_bg": "#454545",
        "progress_bg": "#404040", "progress_fill": "#8a2be2", "font_family": "DynaPuff", # Ensure this font is available
        "font_size_title": 48, "font_size_subtitle": 24, "font_size_button": 14,
        "font_size_player_title": 36, "font_size_track_name": 16, "font_size_time": 11,
        "font_size_icon_button": 14, # Adjusted
    }
}

# Placeholder for where the logo is expected
LOGO_PATH = "Python/Musicova logo v2.png"
FONT_PATH = "Python/fonts/DynaPuff-Regular.ttf" # Assuming this is the path

# --- AudioTrackWidget Class (QWidget) ---
class AudioTrackWidget(QWidget):
    def __init__(self, app_instance, file_path, track_index, on_play_callback, on_remove_callback, parent=None):
        super().__init__(parent)
        self.parent_app = app_instance
        self.file_path = file_path
        self.track_index = track_index
        self.on_play_callback = on_play_callback
        self.on_remove_callback = on_remove_callback

        self.sound = None
        self.duration_sec = 0
        self.is_playing = False
        self.is_paused = False
        self.display_name = os.path.basename(self.file_path) # Default

        self._load_audio_meta()
        self._init_ui()
        self.update_theme() # Apply initial theme via QSS or direct styling

        try:
            self.sound = pygame.mixer.Sound(file_path)
            self.duration_sec = self.sound.get_length()
            self.total_time_label.setText(self._format_time(self.duration_sec))
        except pygame.error as e:
            print(f"Error loading sound {file_path}: {e}")
            self.track_name_label.setText(f"{self.display_name} (Error)")
            self.play_pause_button.setEnabled(False)
        except Exception as e: # Catch other potential errors during init
            print(f"General error initializing track {file_path}: {e}")
            if hasattr(self, 'track_name_label'):
                self.track_name_label.setText(f"{self.display_name} (Load Error)")
            if hasattr(self, 'play_pause_button'):
                self.play_pause_button.setEnabled(False)


    def _load_audio_meta(self):
        try:
            audio_file = MutagenFile(self.file_path, easy=True)
            if audio_file:
                title = audio_file.get('title', [None])[0]
                artist = audio_file.get('artist', [None])[0]
                if title and artist:
                    self.display_name = f"{artist} - {title}"
                elif title:
                    self.display_name = title
                elif artist: # Less common to have artist but not title, but possible
                    self.display_name = f"{artist} - {os.path.splitext(os.path.basename(self.file_path))[0]}"
            # Album art extraction would go here if implemented
        except Exception as e:
            print(f"Error reading metadata for {self.file_path}: {e}")

        # Fallback if display_name is still just the extension or empty
        if '.' in self.display_name and self.display_name.rindex('.') == 0 or not self.display_name.strip():
            self.display_name = os.path.splitext(os.path.basename(self.file_path))[0]


    def _init_ui(self):
        self.setObjectName("AudioTrackWidgetCard") # For QSS styling
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(5)

        # Top part: Album art, Track name, Time
        top_layout = QHBoxLayout()

        self.album_art_label = QLabel("Art") # Placeholder
        self.album_art_label.setFixedSize(60, 60)
        self.album_art_label.setStyleSheet("background-color: grey; border: 1px solid black;") # Basic placeholder
        self.album_art_label.setAlignment(Qt.AlignCenter)
        top_layout.addWidget(self.album_art_label)

        info_layout = QVBoxLayout()
        self.track_name_label = QLabel(self.display_name)
        self.track_name_label.setObjectName("TrackNameLabel")
        self.track_name_label.setWordWrap(True)
        info_layout.addWidget(self.track_name_label)

        time_layout = QHBoxLayout()
        self.current_time_label = QLabel("0:00")
        self.current_time_label.setObjectName("TimeLabel")
        separator_label = QLabel("/")
        separator_label.setObjectName("TimeLabel")
        self.total_time_label = QLabel(self._format_time(self.duration_sec))
        self.total_time_label.setObjectName("TimeLabel")
        time_layout.addWidget(self.current_time_label)
        time_layout.addWidget(separator_label)
        time_layout.addWidget(self.total_time_label)
        time_layout.addStretch()
        info_layout.addLayout(time_layout)

        top_layout.addLayout(info_layout)
        main_layout.addLayout(top_layout)

        # Progress Bar
        self.progress_slider = QSlider(Qt.Horizontal)
        self.progress_slider.setObjectName("ProgressSlider")
        self.progress_slider.setRange(0, 1000) # Represents permillage for smoother seeking
        self.progress_slider.setValue(0)
        self.progress_slider.sliderMoved.connect(self.seek_audio_from_slider) # User drag
        self.progress_slider.valueChanged.connect(self.seek_audio_from_slider_click) # Click on bar
        main_layout.addWidget(self.progress_slider)

        # Controls Frame
        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(5)

        self.play_pause_button = QPushButton(FA_ICONS["play"])
        self.play_pause_button.setObjectName("IconPlainButton")
        self.play_pause_button.clicked.connect(self.toggle_play_pause)

        # Volume slider (simplified for now)
        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setObjectName("VolumeSlider")
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(100) # Default 100%
        self.volume_slider.valueChanged.connect(self.set_volume_from_slider)
        self.volume_slider.setFixedWidth(80)

        remove_button = QPushButton(FA_ICONS["trash-can"])
        remove_button.setObjectName("IconPlainButton")
        remove_button.clicked.connect(self._remove_self)

        controls_layout.addStretch()
        controls_layout.addWidget(self.play_pause_button)
        controls_layout.addStretch()
        controls_layout.addWidget(QLabel("Vol:")) # Simple label
        controls_layout.addWidget(self.volume_slider)
        controls_layout.addStretch()
        controls_layout.addWidget(remove_button)
        controls_layout.addStretch()
        main_layout.addLayout(controls_layout)

        self.setFixedHeight(self.sizeHint().height()) # Try to keep card height consistent

    def _format_time(self, seconds):
        if seconds is None or seconds < 0: return "0:00" # Handle potential negative from get_pos
        minutes = int(seconds // 60)
        seconds = int(seconds % 60)
        return f"{minutes}:{seconds:02d}"

    def set_progress_display(self, current_time_sec, percentage_permille): # percentage is 0-1000
        self.current_time_label.setText(self._format_time(current_time_sec))
        if not self.progress_slider.isSliderDown(): # Don't update if user is dragging
            self.progress_slider.setValue(int(percentage_permille))

    def toggle_play_pause(self):
        self.on_play_callback(self)

    def play(self, channel): # Expects a pygame channel
        if self.sound:
            channel.play(self.sound)
            self.is_playing = True
            self.is_paused = False
            self.play_pause_button.setText(FA_ICONS["pause"])
            self.parent_app.set_active_card_style(self, True)

    def pause(self, channel):
        if self.sound and self.is_playing:
            channel.pause()
            self.is_paused = True # is_playing remains true, but it's paused
            self.play_pause_button.setText(FA_ICONS["play"])
            # Active style might remain or change based on preference
            # self.parent_app.set_active_card_style(self, False) # Optional: remove active style on pause

    def resume(self, channel):
        if self.sound and self.is_paused:
            channel.unpause()
            self.is_paused = False
            self.play_pause_button.setText(FA_ICONS["pause"])
            self.parent_app.set_active_card_style(self, True)

    def stop(self, channel):
        if self.sound:
            channel.stop()
            self.is_playing = False
            self.is_paused = False
            self.play_pause_button.setText(FA_ICONS["play"])
            self.progress_slider.setValue(0)
            self.current_time_label.setText("0:00")
            self.parent_app.set_active_card_style(self, False)

    def set_volume_from_slider(self, value):
        if self.sound:
            self.sound.set_volume(float(value) / 100.0)

    def set_volume_direct(self, volume_float): # 0.0 to 1.0
        if self.sound:
            self.sound.set_volume(volume_float)
            self.volume_slider.setValue(int(volume_float * 100))

    def seek_audio_from_slider(self, value_permille): # value is 0-1000
        if self.sound and self.duration_sec > 0:
            seek_time_sec = (float(value_permille) / 1000.0) * self.duration_sec
            self.current_time_label.setText(self._format_time(seek_time_sec)) # Update display immediately
            # Actual seeking is handled by parent app on slider release or value changed if not dragging
            if self.parent_app.currently_playing_widget == self and not self.progress_slider.isSliderDown():
                 self.parent_app.seek_playback(seek_time_sec)


    def seek_audio_from_slider_click(self, value_permille):
        if not self.progress_slider.isSliderDown(): # only if not dragging (i.e. click)
            self.seek_audio_from_slider(value_permille)


    def _remove_self(self):
        # Stop playback if this track is playing (parent app will handle channel)
        if self.parent_app.currently_playing_widget == self:
            self.parent_app.stop_current_playback() # Ask parent to stop it properly
        self.on_remove_callback(self)
        self.deleteLater() # Safe way to delete QWidget

    def update_theme(self): # Called by parent app when theme changes
        # This will be handled by parent app's QSS update primarily
        # Specific font sizes might need to be reapplied here if not covered by general QSS
        theme_settings = THEME_COLORS[self.parent_app.current_theme]
        font_family = self.parent_app.font_families["default"]

        track_font = QFont(font_family, theme_settings["font_size_track_name"])
        self.track_name_label.setFont(track_font)

        time_font = QFont(font_family, theme_settings["font_size_time"])
        self.current_time_label.setFont(time_font)
        self.total_time_label.setFont(time_font)
        # Find the separator label and set its font too.
        # This requires separator_label to be an instance variable or iterated through layout.
        # For now, assuming parent QSS handles its color.

        icon_font = self.parent_app.font_families["icon"]
        button_font = QFont(icon_font, theme_settings["font_size_icon_button"])
        self.play_pause_button.setFont(button_font)
        # self.remove_button.setFont(button_font) # remove_button is local, find it or make it instance var

        # Find remove_button in layout to set font (example, better to make it self.remove_button)
        for i in range(self.layout().itemAt(2).layout().count()): # Assuming it's in the 3rd layout (controls_layout)
            widget = self.layout().itemAt(2).layout().itemAt(i).widget()
            if isinstance(widget, QPushButton) and widget.text() == FA_ICONS["trash-can"]:
                widget.setFont(button_font)
                break
        self.parent_app.apply_stylesheet() # Trigger global stylesheet refresh if needed


# --- MusicovaApp Class (QMainWindow) ---
class MusicovaApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_theme = "light" # Default theme
        self._init_pygame()
        self._init_fonts() # Initialize QFont objects
        self._init_ui()
        self.apply_stylesheet() # Apply initial theme

        self.playlist = [] # Stores AudioTrackWidget instances
        self.currently_playing_widget = None
        self.playback_start_time_abs = 0 # time.monotonic() when playback started/resumed
        self.paused_at_sec = 0 # Position where playback was paused

        # Pygame setup for audio playback
        self.audio_channel = pygame.mixer.Channel(0) # Use a specific channel

        self.progress_update_timer = QTimer(self)
        self.progress_update_timer.timeout.connect(self._update_current_track_progress)
        self.progress_update_timer.setInterval(250) # ms

        self.show_frame("home")

    def _init_pygame(self):
        try:
            pygame.mixer.init(frequency=44100, size=-16, channels=1, buffer=2048) # Using 1 channel for simplicity
            pygame.init() # Init other modules if needed
        except pygame.error as e:
            print(f"Error initializing pygame.mixer: {e}")
            # Show error dialog to user?

    def _init_fonts(self):
        # Load custom font if specified and available
        # For FontAwesome, it's better to use a font that includes these glyphs
        # or ensure a system font with them is available.
        # For DynaPuff, load it if path is correct.
        # Fallback to generic families if custom font fails.

        # It's good practice to load custom fonts using QFontDatabase
        font_db = self.fontDatabase() if hasattr(self, 'fontDatabase') else QApplication.fontDatabase()

        dyna_puff_id = font_db.addApplicationFont(FONT_PATH)
        dyna_puff_family_name = "DynaPuff"
        if dyna_puff_id != -1:
            dyna_puff_family_name = QFontDatabase.applicationFontFamilies(dyna_puff_id)[0]
        else:
            print(f"Warning: Could not load font {FONT_PATH}. Using system default.")
            dyna_puff_family_name = "Arial" # Fallback

        # For icons, rely on a system font that supports them or bundle a specific one.
        # Common choices: "Font Awesome 6 Free", "FontAwesome" (older versions might be named this)
        # Or use a more generic approach:
        icon_font_family = "Arial" # Fallback, many systems have some icon support in Arial/Segoe UI Symbol
        # A more robust solution for icons is SVG or QIcon.fromTheme if using standard icons.
        # For now, assume text characters are sufficient and a supporting font is present.

        self.font_families = {
            "default": dyna_puff_family_name,
            "icon": icon_font_family # Or a specific FontAwesome font name if installed/bundled
        }

        theme_settings = THEME_COLORS[self.current_theme] # Use current theme for initial font sizes
        self.fonts = {
            "title": QFont(self.font_families["default"], theme_settings["font_size_title"], QFont.Bold),
            "subtitle": QFont(self.font_families["default"], theme_settings["font_size_subtitle"]),
            "button": QFont(self.font_families["default"], theme_settings["font_size_button"], QFont.Bold),
            "player_title": QFont(self.font_families["default"], theme_settings["font_size_player_title"], QFont.Bold),
            "track_name": QFont(self.font_families["default"], theme_settings["font_size_track_name"]),
            "time": QFont(self.font_families["default"], theme_settings["font_size_time"]),
            "icon": QFont(self.font_families["icon"], theme_settings["font_size_icon_button"]) # For icon buttons
        }


    def _generate_qss(self):
        theme = THEME_COLORS[self.current_theme]
        # Note: Font family in QSS might not always work reliably for custom fonts loaded via QFontDatabase.
        # It's often better to set fonts directly on widgets.
        # However, we can try. If issues, remove font-family from QSS and rely on direct QFont application.
        font_family_default = self.font_families["default"]

        qss = f"""
            QMainWindow, QWidget#centralWidget {{
                background-color: {theme['bg']};
            }}
            QWidget#home_frame, QWidget#player_frame {{
                background-color: {theme['bg']};
            }}
            QLabel {{
                color: {theme['text']};
                background-color: transparent; /* Ensure labels don't obscure parent bg */
            }}
            QLabel#TitleLabel {{
                color: {theme['title_text']};
                font-size: {theme['font_size_title']}px; /* Sizes in px for QSS */
                font-weight: bold;
            }}
             QLabel#PlayerTitleLabel {{
                color: {theme['title_text']};
                font-size: {theme['font_size_player_title']}px;
                font-weight: bold;
            }}
            QLabel#SubtitleLabel {{
                color: {theme['text']};
                font-size: {theme['font_size_subtitle']}px;
            }}
            QPushButton, QPushButton#TButton {{ /* General buttons */
                background-color: {theme['button_bg']};
                color: {theme['button_text']};
                border: 1px solid {theme['button_text']};
                padding: 8px 12px;
                font-size: {theme['font_size_button']}px;
                font-weight: bold;
                border-radius: 4px; /* Add some rounded corners */
            }}
            QPushButton:hover, QPushButton#TButton:hover {{
                background-color: {theme['hover_bg']};
            }}
            QPushButton:pressed, QPushButton#TButton:pressed {{
                background-color: {theme['progress_fill']}; /* Use progress_fill for pressed */
                color: {theme['button_bg']};
            }}
            QPushButton:disabled, QPushButton#TButton:disabled {{
                background-color: {theme['disabled_bg']};
                color: #909090;
            }}

            /* Icon buttons on cards - plain style, color from progress_fill */
            QPushButton#IconPlainButton {{
                background-color: transparent;
                color: {theme['progress_fill']};
                border: none;
                padding: 3px;
                font-size: {theme['font_size_icon_button']}px; /* Ensure font is set for icons */
            }}
            QPushButton#IconPlainButton:hover {{
                color: {theme['text']}; /* Or a lighter/darker shade of progress_fill */
            }}
            QPushButton#IconPlainButton:pressed {{
                color: {theme['hover_bg']};
            }}
            QPushButton#IconPlainButton:disabled {{
                color: {theme['disabled_bg']};
            }}

            /* Dark mode toggle button - specific styling if needed, or use general QPushButton */
            QPushButton#DarkModeButton {{
                 /* font-family: '{self.font_families["icon"]}'; */ /* Set font directly for reliability */
                 font-size: {theme['font_size_icon_button']}px; /* Larger for visibility */
                 padding: 5px;
                 border-radius: 15px; /* Circular */
                 min-width: 30px; /* Ensure it's circular */
                 max-width: 30px;
                 min-height: 30px;
                 max-height: 30px;
            }}


            QComboBox {{
                background-color: {theme['button_bg']};
                color: {theme['button_text']};
                border: 1px solid {theme['button_text']};
                padding: 5px;
                font-size: {theme['font_size_button']}px;
                border-radius: 3px;
            }}
            QComboBox::drop-down {{
                border: none;
            }}
            QComboBox QAbstractItemView {{ /* Dropdown list style */
                background-color: {theme['button_bg']};
                color: {theme['button_text']};
                selection-background-color: {theme['progress_fill']};
                selection-color: {theme['button_bg']};
            }}

            QScrollArea {{
                background-color: {theme['bg']};
                border: none;
            }}
            QScrollBar:vertical {{
                border: none;
                background: {theme['progress_bg']};
                width: 10px;
                margin: 0px 0px 0px 0px;
            }}
            QScrollBar::handle:vertical {{
                background: {theme['button_bg']};
                min-height: 20px;
                border-radius: 5px;
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
             QScrollBar:horizontal {{
                border: none;
                background: {theme['progress_bg']};
                height: 10px;
                margin: 0px 0px 0px 0px;
            }}
            QScrollBar::handle:horizontal {{
                background: {theme['button_bg']};
                min-width: 20px;
                border-radius: 5px;
            }}
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
                width: 0px;
            }}


            /* AudioTrackWidget Card Styling */
            QWidget#AudioTrackWidgetCard {{
                background-color: {theme['card_bg']};
                border: 1px solid {theme['progress_bg']};
                border-radius: 5px; /* Rounded corners for cards */
            }}
            QWidget#AudioTrackWidgetCard[active="true"] {{ /* Custom property for active card */
                border: 2px solid {theme['progress_fill']};
            }}
            QLabel#TrackNameLabel {{
                color: {theme['text']};
                background-color: transparent; /* Important for card_bg to show */
                font-size: {theme['font_size_track_name']}px;
            }}
            QLabel#TimeLabel {{
                color: {theme['text']};
                background-color: transparent;
                font-size: {theme['font_size_time']}px;
            }}

            QSlider#ProgressSlider::groove:horizontal {{
                border: 1px solid {theme['progress_bg']};
                height: 8px;
                background: {theme['progress_bg']};
                margin: 2px 0;
                border-radius: 4px;
            }}
            QSlider#ProgressSlider::handle:horizontal {{
                background: {theme['progress_fill']};
                border: 1px solid {theme['progress_fill']};
                width: 12px;
                height: 12px;
                margin: -2px 0;
                border-radius: 6px;
            }}
            QSlider#VolumeSlider::groove:horizontal {{
                height: 4px; background: {theme['progress_bg']}; border-radius: 2px;
            }}
            QSlider#VolumeSlider::handle:horizontal {{
                background: {theme['progress_fill']}; width: 10px; height: 10px; border-radius: 5px; margin: -3px 0;
            }}

        """
        # Apply font-family using direct QFont objects for reliability over QSS font-family
        return qss

    def apply_stylesheet(self):
        qss = self._generate_qss()
        self.setStyleSheet(qss)
        # Re-apply fonts directly as QSS font-family can be unreliable for app-loaded fonts
        self._update_all_widget_fonts()
        # Update themes for child widgets if they have specific logic
        for track_widget in self.playlist:
            track_widget.update_theme()


    def _update_all_widget_fonts(self):
        # This method should iterate through key widgets and apply QFont objects from self.fonts
        # For example, for widgets created directly in MusicovaApp:
        if hasattr(self, 'home_screen_content'): # Check if home screen elements exist
            self.home_screen_content["title_label"].setFont(self.fonts["title"])
            self.home_screen_content["subtitle_label"].setFont(self.fonts["subtitle"])
            self.home_screen_content["access_button"].setFont(self.fonts["button"])

        if hasattr(self, 'player_screen_content'): # Check for player screen elements
            self.player_screen_content["title_label"].setFont(self.fonts["player_title"])
            self.player_screen_content["back_button"].setFont(self.fonts["button"]) # Assuming icon + text
            self.player_screen_content["import_type_combo"].setFont(self.fonts["button"])
            self.player_screen_content["import_button"].setFont(self.fonts["button"])
            self.player_screen_content["clear_playlist_button"].setFont(self.fonts["button"])

        if hasattr(self, 'dark_mode_toggle_button'):
            self.dark_mode_toggle_button.setFont(self.fonts["icon"]) # Specific icon font

        # For dynamically created AudioTrackWidgets, their update_theme method should handle fonts.
        for track_widget in self.playlist:
            if track_widget: # and track_widget.isVisible(): # Check if widget is valid
                 track_widget.update_theme()


    def _init_ui(self):
        self.setWindowTitle("Musicova")
        self.setGeometry(100, 100, 850, 750) # x, y, width, height

        self.central_widget = QWidget(self)
        self.central_widget.setObjectName("centralWidget")
        self.setCentralWidget(self.central_widget)

        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0,0,0,0) # Full window usage

        # Global buttons (e.g., dark mode toggle) can be part of a top bar or overlay
        # For simplicity, let's add it to a layout within the central widget for now.
        # A more common approach for a main window is to have a status bar or a dedicated controls bar.

        top_bar_layout = QHBoxLayout()
        top_bar_layout.addStretch()
        self.dark_mode_toggle_button = QPushButton(FA_ICONS["moon"])
        self.dark_mode_toggle_button.setObjectName("DarkModeButton") # For specific styling
        self.dark_mode_toggle_button.setToolTip("Toggle Dark/Light Mode")
        self.dark_mode_toggle_button.clicked.connect(self.toggle_dark_mode)
        self.dark_mode_toggle_button.setFixedSize(32,32) # Make it a bit larger and square
        top_bar_layout.addWidget(self.dark_mode_toggle_button)
        self.main_layout.addLayout(top_bar_layout)


        self.stacked_widget = QStackedWidget(self)
        self.main_layout.addWidget(self.stacked_widget)

        self.frames = {} # Store page widgets
        self.frames["home"] = self._create_home_screen()
        self.frames["player"] = self._create_player_screen()

        self.stacked_widget.addWidget(self.frames["home"])
        self.stacked_widget.addWidget(self.frames["player"])


    def toggle_dark_mode(self):
        self.current_theme = "dark" if self.current_theme == "light" else "light"
        new_icon = FA_ICONS['sun'] if self.current_theme == "dark" else FA_ICONS['moon']
        self.dark_mode_toggle_button.setText(new_icon)
        self._init_fonts() # Re-init fonts in case sizes change with theme (they do in THEME_COLORS)
        self.apply_stylesheet() # Re-apply all styles and fonts

    def _create_home_screen(self):
        home_widget = QWidget()
        home_widget.setObjectName("home_frame") # For QSS
        layout = QVBoxLayout(home_widget)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(20)

        self.home_screen_content = {} # Store refs to widgets for font updates

        # Logo
        logo_label = QLabel()
        try:
            pixmap = QPixmap(LOGO_PATH)
            if not pixmap.isNull():
                logo_label.setPixmap(pixmap.scaled(350, int(350 * pixmap.height() / pixmap.width() if pixmap.width() > 0 else 0), Qt.KeepAspectRatio, Qt.SmoothTransformation))
            else:
                logo_label.setText("Musicova Logo (Not Found)") # Fallback text
        except Exception as e:
            print(f"Error loading logo: {e}")
            logo_label.setText("Musicova Logo (Error)")
        logo_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(logo_label)

        title_label = QLabel("Musicova")
        title_label.setObjectName("TitleLabel") # For QSS
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        self.home_screen_content["title_label"] = title_label

        subtitle_label = QLabel("Your Personal Music Space")
        subtitle_label.setObjectName("SubtitleLabel") # For QSS
        subtitle_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(subtitle_label)
        self.home_screen_content["subtitle_label"] = subtitle_label

        access_button = QPushButton("Access Musicova Player")
        access_button.setObjectName("TButton") # General button style
        access_button.clicked.connect(lambda: self.show_frame("player"))
        access_button.setFixedHeight(50) # Make button taller
        layout.addWidget(access_button, alignment=Qt.AlignCenter)
        self.home_screen_content["access_button"] = access_button

        layout.addStretch() # Push content towards center/top

        return home_widget

    def _create_player_screen(self):
        player_widget = QWidget()
        player_widget.setObjectName("player_frame")
        main_layout = QVBoxLayout(player_widget)
        main_layout.setContentsMargins(10,10,10,10)
        main_layout.setSpacing(10)

        self.player_screen_content = {}

        # Top Bar: Back Button
        top_bar_layout = QHBoxLayout()
        back_button = QPushButton(f"{FA_ICONS['arrow-left']} Back")
        back_button.setObjectName("TButton")
        back_button.clicked.connect(lambda: self.show_frame("home"))
        top_bar_layout.addWidget(back_button, alignment=Qt.AlignLeft)
        top_bar_layout.addStretch()
        main_layout.addLayout(top_bar_layout)
        self.player_screen_content["back_button"] = back_button

        # Player Title
        player_title_label = QLabel("Musicova Player")
        player_title_label.setObjectName("PlayerTitleLabel")
        player_title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(player_title_label)
        self.player_screen_content["title_label"] = player_title_label

        # Import Controls
        import_controls_layout = QHBoxLayout()
        import_controls_layout.setAlignment(Qt.AlignCenter)
        self.import_type_combo = QComboBox()
        self.import_type_combo.addItems(["Import File(s)", "Import Folder"])
        self.player_screen_content["import_type_combo"] = self.import_type_combo

        import_button = QPushButton("Import")
        import_button.setObjectName("TButton")
        import_button.clicked.connect(self.handle_import)
        self.player_screen_content["import_button"] = import_button

        clear_playlist_button = QPushButton("Clear Playlist")
        clear_playlist_button.setObjectName("TButton")
        clear_playlist_button.clicked.connect(self.handle_clear_playlist)
        self.player_screen_content["clear_playlist_button"] = clear_playlist_button

        import_controls_layout.addWidget(self.import_type_combo)
        import_controls_layout.addWidget(import_button)
        import_controls_layout.addWidget(clear_playlist_button)
        main_layout.addLayout(import_controls_layout)

        # Tracks Area (Scrollable)
        self.tracks_scroll_area = QScrollArea()
        self.tracks_scroll_area.setWidgetResizable(True)
        self.tracks_scroll_area.setObjectName("TracksScrollArea") # For QSS

        self.audio_tracks_container_widget = QWidget() # This widget will contain the track cards
        self.tracks_list_layout = QVBoxLayout(self.audio_tracks_container_widget)
        self.tracks_list_layout.setAlignment(Qt.AlignTop) # Tracks added to top
        self.tracks_list_layout.setSpacing(5)

        self.tracks_scroll_area.setWidget(self.audio_tracks_container_widget)
        main_layout.addWidget(self.tracks_scroll_area)

        return player_widget

    def show_frame(self, frame_key):
        if frame_key in self.frames:
            self.stacked_widget.setCurrentWidget(self.frames[frame_key])
            # Fonts and styles should be reapplied if they depend on which frame is visible,
            # but with global QSS and direct font setting, this might not be strictly necessary
            # unless specific visibility-dependent styles are used.
            self.apply_stylesheet() # Re-apply to ensure styles are correct for the new view

    def handle_import(self):
        import_type = self.import_type_combo.currentText()
        files_to_add = []
        if import_type == "Import File(s)":
            selected_files, _ = QFileDialog.getOpenFileNames(
                self, "Select Audio Files", "",
                "Audio Files (*.mp3 *.wav *.ogg *.flac);;All files (*.*)"
            )
            if selected_files: files_to_add.extend(selected_files)
        elif import_type == "Import Folder":
            folder_path = QFileDialog.getExistingDirectory(self, "Select Folder")
            if folder_path:
                for item in os.listdir(folder_path):
                    full_path = os.path.join(folder_path, item)
                    if os.path.isfile(full_path) and item.lower().endswith(('.mp3', '.wav', '.ogg', '.flac')):
                        files_to_add.append(full_path)

        if files_to_add:
            for file_path in files_to_add:
                if any(track.file_path == file_path for track in self.playlist):
                    print(f"Track {file_path} already in playlist. Skipping.")
                    continue

                track_widget = AudioTrackWidget(self, file_path, len(self.playlist),
                                                self.handle_track_play_request,
                                                self.remove_track_from_playlist)
                self.tracks_list_layout.addWidget(track_widget)
                self.playlist.append(track_widget)
            self.apply_stylesheet() # Update styles for new cards


    def handle_clear_playlist(self):
        self.stop_current_playback()
        for widget in self.playlist:
            widget.deleteLater() # Safe deletion
        self.playlist.clear()
        self.currently_playing_widget = None
        if self.progress_update_timer.isActive():
            self.progress_update_timer.stop()
        # Clear layout (alternative to deleting one by one if container is recreated)
        # while self.tracks_list_layout.count():
        #     child = self.tracks_list_layout.takeAt(0)
        #     if child.widget():
        #         child.widget().deleteLater()


    def handle_track_play_request(self, track_widget_to_play):
        if self.currently_playing_widget == track_widget_to_play: # Clicked on already playing/paused track
            if track_widget_to_play.is_paused:
                track_widget_to_play.resume(self.audio_channel)
                self.playback_start_time_abs = pygame.time.get_ticks() - (self.paused_at_sec * 1000)
                if not self.progress_update_timer.isActive(): self.progress_update_timer.start()
            elif track_widget_to_play.is_playing: # Is playing, so pause it
                track_widget_to_play.pause(self.audio_channel)
                self.paused_at_sec = (pygame.time.get_ticks() - self.playback_start_time_abs) / 1000.0
                if self.progress_update_timer.isActive(): self.progress_update_timer.stop()
            # else: was stopped (neither playing nor paused), effectively a new play from start
        else: # Clicked on a new track
            if self.currently_playing_widget:
                self.currently_playing_widget.stop(self.audio_channel) # Stop previous track

            self.currently_playing_widget = track_widget_to_play
            self.currently_playing_widget.play(self.audio_channel)
            self.playback_start_time_abs = pygame.time.get_ticks() # Record when this new track started
            self.paused_at_sec = 0 # Reset paused position
            if not self.progress_update_timer.isActive(): self.progress_update_timer.start()

        # Synchronize volume for the newly active track
        if self.currently_playing_widget and self.currently_playing_widget.sound:
             current_master_volume = self.currently_playing_widget.volume_slider.value() / 100.0
             self.currently_playing_widget.sound.set_volume(current_master_volume)


    def stop_current_playback(self):
        if self.currently_playing_widget:
            self.currently_playing_widget.stop(self.audio_channel)
            self.currently_playing_widget = None
        if self.progress_update_timer.isActive():
            self.progress_update_timer.stop()

    def seek_playback(self, seek_time_sec):
        if self.currently_playing_widget and self.currently_playing_widget.sound:
            # Pygame Sound objects play from start or a specific time if re-played.
            # To seek, we stop, then play again with a start offset.
            # This is not ideal as it might cause a slight audio glitch.
            # mixer.music.set_pos() is better but we are using Sound objects on a channel.

            # For Sound objects on a channel, the channel itself doesn't support seeking.
            # We have to stop the sound on the channel and replay it.
            # The `start` argument to `play()` is for milliseconds.

            self.audio_channel.stop() # Stop current playback on the channel

            # Convert seek_time_sec to milliseconds for the 'maxtime' or 'fade_ms' like parameters
            # Sound.play(loops, maxtime, fade_ms)
            # There isn't a direct 'start_at_offset' for channel.play(Sound).
            # This means true seeking with Sound objects on channels is complex.
            # A common workaround is to use pygame.mixer.music for single track playback
            # or to manage segments of audio if precise seeking on Sound objects is needed.

            # Given the current structure with Sound objects:
            # The best we can do is restart the sound and it will play from the beginning.
            # The visual progress bar is updated, but audio restarts.
            # This is a limitation of pygame.mixer.Sound with channels for seeking.

            # Let's assume for now the visual seek is what's primarily achieved,
            # and if it was playing, it restarts from beginning but timer will reflect the new visual start.

            self.audio_channel.play(self.currently_playing_widget.sound) # Plays from beginning
            self.playback_start_time_abs = pygame.time.get_ticks() - (seek_time_sec * 1000) # Adjust timer to reflect seek

            if self.currently_playing_widget.is_paused: # If it was paused, re-pause it at the new (visual) position
                self.audio_channel.pause()
            elif not self.progress_update_timer.isActive(): # If it was stopped or just seeked, ensure timer runs if meant to be playing
                self.progress_update_timer.start()

            # Update the display to reflect the seeked time immediately
            if self.currently_playing_widget.duration_sec > 0:
                permille = (seek_time_sec / self.currently_playing_widget.duration_sec) * 1000
                self.currently_playing_widget.set_progress_display(seek_time_sec, permille)


    def _update_current_track_progress(self):
        if self.currently_playing_widget and self.currently_playing_widget.is_playing and \
           not self.currently_playing_widget.is_paused and self.audio_channel.get_busy():

            # Calculate elapsed time since playback_start_time_abs
            current_pos_msec = pygame.time.get_ticks() - self.playback_start_time_abs
            current_pos_sec = current_pos_msec / 1000.0

            if self.currently_playing_widget.duration_sec > 0:
                percentage_permille = (current_pos_sec / self.currently_playing_widget.duration_sec) * 1000
                self.currently_playing_widget.set_progress_display(current_pos_sec, percentage_permille)

                if current_pos_sec >= self.currently_playing_widget.duration_sec:
                    self.handle_track_ended(self.currently_playing_widget)
            else: # Duration is 0, perhaps error or not loaded
                 self.currently_playing_widget.set_progress_display(0,0)

        elif self.currently_playing_widget and self.currently_playing_widget.is_playing and \
             not self.currently_playing_widget.is_paused and not self.audio_channel.get_busy():
            # Sound finished playing (channel is not busy anymore but we thought it was playing)
            self.handle_track_ended(self.currently_playing_widget)


    def handle_track_ended(self, track_widget):
        if track_widget == self.currently_playing_widget:
            track_widget.stop(self.audio_channel) # Visually reset it

            current_idx = -1
            try:
                current_idx = self.playlist.index(track_widget)
            except ValueError: # Should not happen if logic is correct
                self.currently_playing_widget = None
                if self.progress_update_timer.isActive(): self.progress_update_timer.stop()
                return

            if current_idx + 1 < len(self.playlist): # If there's a next track
                next_track_widget = self.playlist[current_idx + 1]
                self.handle_track_play_request(next_track_widget) # Play next
            else: # End of playlist
                self.currently_playing_widget = None
                if self.progress_update_timer.isActive(): self.progress_update_timer.stop()


    def remove_track_from_playlist(self, track_widget_to_remove):
        if track_widget_to_remove == self.currently_playing_widget:
            self.stop_current_playback() # This also sets currently_playing_widget to None

        if track_widget_to_remove in self.playlist:
            self.playlist.remove(track_widget_to_remove)
            self.tracks_list_layout.removeWidget(track_widget_to_remove)
            track_widget_to_remove.deleteLater() # Important: schedule for deletion

        # Re-index not strictly necessary with object list, but if track_index property is used elsewhere:
        for i, track in enumerate(self.playlist):
            track.track_index = i


    def set_active_card_style(self, track_widget, is_active):
        # Use a dynamic property for QSS styling
        track_widget.setProperty("active", is_active)
        # Re-polish the widget to apply style changes from property
        track_widget.style().unpolish(track_widget)
        track_widget.style().polish(track_widget)
        # self.apply_stylesheet() # Could also reapply global, but might be too much. Polishing should be enough.

    def closeEvent(self, event): # Override QMainWindow's closeEvent
        self.stop_current_playback()
        if self.progress_update_timer.isActive():
            self.progress_update_timer.stop()
        pygame.mixer.quit()
        pygame.quit() # Quit pygame itself
        event.accept()

    main_window = MusicovaApp()
    main_window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    # It's good practice to set ApplicationName and OrganizationName for Qt settings, etc.
    QApplication.setApplicationName("Musicova")
    QApplication.setOrganizationName("MusicovaProject") # Example

    app = QApplication(sys.argv)
    # Apply a style that might look better cross-platform if default is too basic
    # app.setStyle("Fusion") # Or "Windows", "GTK+", etc. Fusion is often a good default.

    main_window = MusicovaApp()
    main_window.show()
    sys.exit(app.exec_())

import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QLabel,
                             QVBoxLayout, QWidget, QFileDialog, QComboBox,
                             QScrollArea, QHBoxLayout, QSlider, QGridLayout)
from PyQt5.QtCore import Qt, QUrl, QSettings
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent

class MusicovaApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings = QSettings('Musicova', 'Theme')
        self.dark_mode = self.settings.value('dark_mode', False, type=bool)
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Musicova')
        self.setMinimumSize(800, 600)

        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Create scroll area for playlist
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setMinimumHeight(200)
        self.playlist_widget = QWidget()
        self.playlist_layout = QVBoxLayout(self.playlist_widget)
        scroll_area.setWidget(self.playlist_widget)

        # Create media player
        self.media_player = QMediaPlayer()
        layout.setAlignment(Qt.AlignCenter)

        # Load and display logo
        logo_path = os.path.join(os.path.dirname(__file__), 'Musicova logo v2.png')
        logo_label = QLabel()
        pixmap = QPixmap(logo_path)
        scaled_pixmap = pixmap.scaled(400, 400, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        logo_label.setPixmap(scaled_pixmap)
        logo_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(logo_label)

        # Add title and subtitle
        title_label = QLabel('Musicova')
        title_label.setStyleSheet('font-family: "DynaPuff", sans-serif; font-size: 48px; font-weight: bold;')
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        subtitle_label = QLabel('The Open-Source music player')
        subtitle_label.setStyleSheet('font-family: "DynaPuff", sans-serif; font-size: 24px;')
        subtitle_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(subtitle_label)

        # Add access button
        access_button = QPushButton('Access')
        access_button.setStyleSheet("""
            QPushButton {
                background-color: #333333;
                color: white;
                border: none;
                border-radius: 25px;
                padding: 15px 30px;
                font-family: 'DynaPuff', sans-serif;
                font-size: 18px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #444444;
            }
        """)
        access_button.clicked.connect(self.show_player)
        layout.addWidget(access_button, alignment=Qt.AlignCenter)

        # Add theme toggle button
        self.theme_button = QPushButton('🌙')
        self.theme_button.setFixedSize(40, 40)
        self.theme_button.setStyleSheet("""QPushButton {
                background-color: transparent;
                border: none;
                font-size: 20px;
                position: absolute;
                top: 10px;
                right: 10px;
            }
            QPushButton:hover {
                background-color: rgba(128, 128, 128, 0.2);
                border-radius: 20px;
            }
        """)
        self.theme_button.clicked.connect(self.toggle_theme)
        layout.addWidget(self.theme_button, alignment=Qt.AlignRight)

        # Set initial theme
        self.apply_theme()

    def show_player(self):
        # Hide the main window and show the player window
        self.player_window = PlayerWindow(self)
        self.player_window.show()
        self.hide()

    def toggle_theme(self):
        self.dark_mode = not self.dark_mode
        self.settings.setValue('dark_mode', self.dark_mode)
        self.theme_button.setText('☀️' if self.dark_mode else '🌙')
        self.apply_theme()
        # Update player window theme if it exists
        if hasattr(self, 'player_window') and self.player_window is not None:
            self.player_window.apply_theme()

    def apply_theme(self):
        if self.dark_mode:
            self.setStyleSheet("""
                QMainWindow, QWidget {
                    background-color: #1a1a1a;
                    color: white;
                }
            """)
        else:
            self.setStyleSheet("""
                QMainWindow, QWidget {
                    background-color: blueviolet;
                    color: black;
                }
            """)

class PlayerWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.playlist = []
        self.current_player = None
        self.init_ui()

    def init_ui(self):
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

        # Create scroll area for playlist
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setMinimumHeight(200)
        self.playlist_widget = QWidget()
        self.playlist_layout = QVBoxLayout(self.playlist_widget)
        scroll_area.setWidget(self.playlist_widget)

        # Create media player
        self.media_player = QMediaPlayer()

        # Add title
        title_label = QLabel('Musicova Player')
        title_label.setStyleSheet('font-family: "DynaPuff", sans-serif; font-size: 36px; font-weight: bold;')
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        # Add import controls container
        self.import_container = QWidget()
        import_layout = QHBoxLayout(self.import_container)
        import_layout.setAlignment(Qt.AlignCenter)
        import_layout.setSpacing(10)

        self.file_select = QComboBox()
        self.file_select.addItem('Select import type')
        self.file_select.addItem('Choose Folder')
        self.file_select.addItem('Choose File')
        self.file_select.setFixedWidth(200)
        self.file_select.setStyleSheet("""
            QComboBox {
                background-color: white;
                color: blueviolet;
                border: none;
                border-radius: 20px;
                padding: 8px 15px;
                font-family: 'DynaPuff', sans-serif;
            }
        """)
        import_layout.addWidget(self.file_select)

        import_button = QPushButton('Import')
        import_button.setFixedWidth(100)
        import_button.setStyleSheet("""
            QPushButton {
                background-color: white;
                color: blueviolet;
                border: none;
                border-radius: 20px;
                padding: 8px 15px;
                font-family: 'DynaPuff', sans-serif;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #f0f0f0;
            }
        """)
        import_button.clicked.connect(self.import_files)
        import_layout.addWidget(import_button)

        layout.addWidget(self.import_container)

        # Create cards container with grid layout
        self.cards_container = QWidget()
        self.cards_layout = QGridLayout(self.cards_container)
        self.cards_layout.setSpacing(20)
        self.cards_layout.setAlignment(Qt.AlignCenter)
        
        # Add cards container to scroll area
        cards_scroll = QScrollArea()
        cards_scroll.setWidgetResizable(True)
        cards_scroll.setWidget(self.cards_container)
        cards_scroll.setMinimumHeight(400)
        cards_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        cards_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        layout.addWidget(cards_scroll)
        
        # Dictionary to store media players and their controls
        self.track_players = {}

        # Add back button
        back_button = QPushButton('Back to Home')
        back_button.clicked.connect(self.go_back)
        layout.addWidget(back_button)

        theme_button = QPushButton('Toggle Theme')
        theme_button.clicked.connect(self.parent.toggle_theme)
        layout.addWidget(theme_button)
        self.apply_theme()

        # Apply theme
        self.apply_theme()

    def import_files(self):
        # Clear existing playlist before importing new files
        self.clear_playlist()

        if self.file_select.currentText() == 'Choose Folder':
            folder = QFileDialog.getExistingDirectory(self, 'Select Folder')
            if folder:
                for root, _, files in os.walk(folder):
                    for file in files:
                        if file.lower().endswith(('.mp3', '.wav', '.ogg')):
                            self.add_to_playlist(os.path.join(root, file))
        elif self.file_select.currentText() == 'Choose File':
            file, _ = QFileDialog.getOpenFileName(self, 'Select File', '', 'Audio Files (*.mp3 *.wav *.ogg)')
            if file:
                self.add_to_playlist(file)

        # Update import controls visibility
        self.update_import_controls_visibility()

    def clear_playlist(self):
        # Clear the playlist array
        self.playlist.clear()

        # Stop and clean up all media players
        for controls in self.track_players.values():
            controls['player'].stop()
            controls['player'].deleteLater()

        # Clear the track_players dictionary
        self.track_players.clear()

        # Reset grid layout position trackers
        self.current_row = 0
        self.current_col = 0

        # Remove all widgets from the cards layout
        while self.cards_layout.count():
            item = self.cards_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Update the visibility of import controls
        self.update_import_controls_visibility()

    def add_to_playlist(self, file_path):
        # Normalize file path to use forward slashes consistently
        file_path = file_path.replace('\\', '/')
        self.playlist.append(file_path)
        
        # Create player card
        player_card = QWidget()
        player_card.setObjectName('player_card')
        player_card.setFixedWidth(300)
        player_card.setMinimumHeight(400)
        player_card.setStyleSheet("""
            QWidget#player_card {
                background-color: #2a2a2a;
                border-radius: 20px;
                padding: 20px;
                color: white;
            }
        """)
        
        card_layout = QVBoxLayout(player_card)
        
        # Add album art placeholder
        album_art = QLabel()
        album_art.setFixedSize(200, 200)
        album_art.setStyleSheet('background-color: blueviolet; border-radius: 10px;')
        album_art.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(album_art, alignment=Qt.AlignCenter)
        
        # Add track name
        track_name = os.path.basename(file_path)
        track_label = QLabel(track_name)
        track_label.setStyleSheet('color: white; font-weight: bold; font-size: 14px;')
        track_label.setAlignment(Qt.AlignCenter)
        track_label.setWordWrap(True)
        card_layout.addWidget(track_label)
        
        # Add progress bar and time labels
        progress_container = QWidget()
        progress_layout = QHBoxLayout(progress_container)
        
        time_current = QLabel('0:00')
        time_current.setStyleSheet('color: white;')
        progress_slider = QSlider(Qt.Horizontal)
        progress_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                background: #333333;
                height: 4px;
                border-radius: 2px;
            }
            QSlider::sub-page:horizontal {
                background: #7000a3;
                height: 4px;
                border-radius: 2px;
            }
            QSlider::handle:horizontal {
                background: #666666;
                width: 12px;
                height: 12px;
                margin: -4px 0;
                border-radius: 6px;
            }
        """)
        
        time_total = QLabel('0:00')
        time_total.setStyleSheet('color: white;')
        
        progress_layout.addWidget(time_current)
        progress_layout.addWidget(progress_slider)
        progress_layout.addWidget(time_total)
        
        card_layout.addWidget(progress_container)
        
        # Add playback controls
        controls_container = QWidget()
        controls_layout = QHBoxLayout(controls_container)
        controls_layout.setSpacing(20)
        
        play_button = QPushButton('▶')
        play_button.setFixedSize(50, 50)
        play_button.setStyleSheet("""
            QPushButton {
                background-color: blueviolet;
                color: white;
                border-radius: 25px;
                font-size: 20px;
            }
            QPushButton:hover {
                background-color: #8a2be2;
            }
        """)
        
        # Create media player for this track
        media_player = QMediaPlayer()
        content = QMediaContent(QUrl.fromLocalFile(file_path))
        media_player.setMedia(content)
        
        # Store player and controls
        self.track_players[file_path] = {
            'player': media_player,
            'progress': progress_slider,
            'time_current': time_current,
            'time_total': time_total,
            'play_button': play_button
        }
        
        # Connect signals
        media_player.durationChanged.connect(lambda duration: self.update_duration(duration, file_path))
        media_player.positionChanged.connect(lambda position: self.update_position(position, file_path))
        progress_slider.sliderPressed.connect(lambda: self.on_slider_pressed(file_path))
        progress_slider.sliderReleased.connect(lambda: self.on_slider_released(file_path))
        progress_slider.valueChanged.connect(lambda value: self.on_slider_value_changed(value, file_path))
        play_button.clicked.connect(lambda: self.play_pause(file_path))
        
        controls_layout.addStretch()
        controls_layout.addWidget(play_button)
        controls_layout.addStretch()
        
        card_layout.addWidget(controls_container)
        
        # Add player card to cards layout in grid format
        self.cards_layout.addWidget(player_card, self.current_row, self.current_col)
        self.current_col += 1
        if self.current_col >= self.max_columns:
            self.current_col = 0
            self.current_row += 1

    def update_import_controls_visibility(self):
        # Import controls should always be visible
        self.import_container.setVisible(True)
        # Show/hide cards container based on playlist content
        self.cards_container.setVisible(len(self.playlist) > 0)

    def apply_theme(self):
        if self.parent.dark_mode:
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
                    font-family: 'DynaPuff', sans-serif;
                    font-size: 18px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #3d3d3d;
                    transform: translateY(-2px);
                }
                QComboBox {
                    background-color: #3d3d3d;
                    color: white;
                    border: none;
                    border-radius: 25px;
                    padding: 15px 30px;
                    font-family: 'DynaPuff', sans-serif;
                    font-size: 18px;
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
                    background: #8a2be2;
                    border-radius: 2px;
                }
                QWidget#player_card {
                    background-color: #2d2d2d;
                    border-radius: 15px;
                    padding: 20px;
                }
                QLabel {
                    color: white;
                }
                QWidget#player_card QLabel {
                    color: white;
                }
            """)
        else:
            self.setStyleSheet("""
                QMainWindow, QWidget {
                    background-color: blueviolet;
                    color: black;
                }
                QPushButton {
                    background-color: white;
                    color: blueviolet;
                    border: none;
                    border-radius: 25px;
                    padding: 15px 30px;
                    font-family: 'DynaPuff', sans-serif;
                    font-size: 18px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #f0f0f0;
                    transform: translateY(-2px);
                }
                QComboBox {
                    background-color: white;
                    color: blueviolet;
                    border: none;
                    border-radius: 25px;
                    padding: 15px 30px;
                    font-family: 'DynaPuff', sans-serif;
                    font-size: 18px;
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
                    background: blueviolet;
                    border-radius: 2px;
                }
                QWidget#player_card {
                    background-color: white;
                    border-radius: 15px;
                    padding: 20px;
                }
                QLabel {
                    color: black;
                }
                QWidget#player_card QLabel {
                    color: black;
                }
            """)

    def play_track(self, file_path):
        content = QMediaContent(QUrl.fromLocalFile(file_path))
        self.media_player.setMedia(content)
        self.media_player.play()
        
        # Update track name
        self.track_name_label.setText(os.path.basename(file_path))
        
        # Set up progress slider
        self.media_player.durationChanged.connect(self.update_duration)
        self.media_player.positionChanged.connect(self.update_position)

    def update_duration(self, duration, file_path):
        controls = self.track_players[file_path]
        controls['progress'].setMaximum(duration)
        total_time = duration // 1000  # Convert to seconds
        minutes = total_time // 60
        seconds = total_time % 60
        controls['time_total'].setText(f'{minutes}:{seconds:02d}')

    def update_position(self, position, file_path):
        controls = self.track_players[file_path]
        if not controls['progress'].isSliderDown():
            controls['progress'].setValue(position)
            current_time = position // 1000  # Convert to seconds
            minutes = current_time // 60
            seconds = current_time % 60
            controls['time_current'].setText(f'{minutes}:{seconds:02d}')

    def on_slider_pressed(self, file_path):
        controls = self.track_players[file_path]
        self.was_playing = controls['player'].state() == QMediaPlayer.PlayingState
        if self.was_playing:
            controls['player'].pause()

    def on_slider_released(self, file_path):
        controls = self.track_players[file_path]
        controls['player'].setPosition(controls['progress'].value())
        if self.was_playing:
            controls['player'].play()

    def on_slider_value_changed(self, value, file_path):
        controls = self.track_players[file_path]
        if controls['progress'].isSliderDown():
            current_time = value // 1000  # Convert to seconds
            minutes = current_time // 60
            seconds = current_time % 60
            controls['time_current'].setText(f'{minutes}:{seconds:02d}')

    def play_pause(self, file_path):
        controls = self.track_players[file_path]
        player = controls['player']
        play_button = controls['play_button']
        
        if player.state() == QMediaPlayer.PlayingState:
            player.pause()
            play_button.setText('▶')
        else:
            player.play()
            play_button.setText('⏸')

    def go_back(self):
        # Stop all players
        for controls in self.track_players.values():
            controls['player'].stop()
        
        # Show the main window and close the player window
        self.parent.show()
        self.close()

    def play_previous(self):
        if not self.playlist:
            return
        
        # Find current track index
        current_file = self.media_player.media().canonicalUrl().toLocalFile()
        try:
            current_index = self.playlist.index(current_file)
            # Get previous track (wrap around to end if at start)
            prev_index = (current_index - 1) if current_index > 0 else len(self.playlist) - 1
            self.play_track(self.playlist[prev_index])
        except ValueError:
            # If current file not in playlist, play last track
            self.play_track(self.playlist[-1])

    def play_next(self):
        if not self.playlist:
            return
        
        # Find current track index
        current_file = self.media_player.media().canonicalUrl().toLocalFile()
        try:
            current_index = self.playlist.index(current_file)
            # Get previous track (wrap around to end if at start)
            prev_index = (current_index - 1) if current_index > 0 else len(self.playlist) - 1
            self.play_track(self.playlist[prev_index])
        except ValueError:
            # If current file not in playlist, play last track
            self.play_track(self.playlist[-1])

    def go_back(self):
        self.parent.show()
        self.close()

def main():
    app = QApplication(sys.argv)
    window = MusicovaApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
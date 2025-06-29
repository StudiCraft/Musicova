import tkinter as tk
from tkinter import ttk, font, filedialog
from PIL import Image, ImageTk
import pygame
import tkfontawesome as fa
import os
import time # Added for progress tracking
from mutagen.mp3 import MP3
from mutagen.wave import WAVE
from mutagen.oggvorbis import OggVorbis
from mutagen.flac import FLAC
from mutagen.easyid3 import EasyID3
from mutagen import File as MutagenFile

# --- THEME_COLORS Definition (unchanged) ---
THEME_COLORS = {
    "light": {
        "bg": "blueviolet", "text": "black", "button_bg": "white", "button_text": "blueviolet",
        "title_text": "black", "card_bg": "white", "hover_bg": "#f0f0f0",
        "progress_bg": "#e0e0e0", "progress_fill": "blueviolet", "font_family": "DynaPuff",
        "font_size_title": 48, "font_size_subtitle": 24, "font_size_button": 14,
        "font_size_player_title": 36, "font_size_track_name": 16, "font_size_time": 11,
        "font_size_icon_button": 10,
    },
    "dark": {
        "bg": "#1a1a1a", "text": "white", "button_bg": "#3d3d3d", "button_text": "white",
        "title_text": "white", "card_bg": "#2d2d2d", "hover_bg": "#3d3d3d",
        "progress_bg": "#404040", "progress_fill": "#8a2be2", "font_family": "DynaPuff",
        "font_size_title": 48, "font_size_subtitle": 24, "font_size_button": 14,
        "font_size_player_title": 36, "font_size_track_name": 16, "font_size_time": 11,
        "font_size_icon_button": 10,
    }
}

# --- AudioTrackWidget Class ---
class AudioTrackWidget(ttk.Frame):
    def __init__(self, parent, app_instance, file_path, track_index, on_play_callback, on_remove_callback):
        super().__init__(parent, style="Card.TFrame")
        self.parent_app = app_instance # Reference to the main MusicovaApp instance
        self.file_path = file_path
        self.track_index = track_index # Index in the playlist
        self.on_play_callback = on_play_callback
        self.on_remove_callback = on_remove_callback

        self.sound = None
        self.duration_sec = 0
        self.is_playing = False
        self.is_paused = False # Explicit pause state

        self._load_audio_meta()
        self._create_widgets()
        self.update_theme() # Apply initial theme

        try:
            self.sound = pygame.mixer.Sound(file_path)
            self.duration_sec = self.sound.get_length()
            self.total_time_label.config(text=self._format_time(self.duration_sec))
        except pygame.error as e:
            print(f"Error loading sound {file_path}: {e}")
            self.track_name_label.config(text=f"{self.track_name_label.cget('text')} (Error)")
            # Disable playback controls if sound fails to load
            self.play_pause_button.config(state=tk.DISABLED)


    def _load_audio_meta(self):
        self.display_name = os.path.basename(self.file_path)
        try:
            audio_file = MutagenFile(self.file_path, easy=True)
            if audio_file:
                if 'title' in audio_file and audio_file['title']:
                    self.display_name = audio_file['title'][0]
                if 'artist' in audio_file and audio_file['artist']:
                    self.display_name = f"{audio_file['artist'][0]} - {self.display_name}"
            # Album art extraction is more complex and platform-dependent, skipping for now
        except Exception as e:
            print(f"Error reading metadata for {self.file_path}: {e}")

        # Fallback if display_name is still just the extension or empty
        if '.' in self.display_name and self.display_name.rindex('.') == 0 or not self.display_name.strip():
            self.display_name = os.path.splitext(os.path.basename(self.file_path))[0]


    def _create_widgets(self):
        self.configure(padding=(10,10))
        # Album Art Placeholder
        self.album_art_placeholder = tk.Canvas(self, width=60, height=60, bd=0, highlightthickness=0)
        self.album_art_placeholder.grid(row=0, column=0, rowspan=3, padx=(0, 10), pady=5, sticky="ns")

        # Track Name
        self.track_name_label = ttk.Label(self, text=self.display_name, style="TrackName.TLabel", anchor="w", wraplength=280)
        self.track_name_label.grid(row=0, column=1, columnspan=3, sticky="ew", pady=(5,0))

        # Time Display (Current / Total)
        time_frame = ttk.Frame(self, style="CardInner.TFrame")
        time_frame.grid(row=1, column=1, columnspan=3, sticky="ew", pady=2)
        self.current_time_label = ttk.Label(time_frame, text="0:00", style="Time.TLabel")
        self.current_time_label.pack(side="left", padx=(0,5))
        separator_label = ttk.Label(time_frame, text="/", style="Time.TLabel")
        separator_label.pack(side="left")
        self.total_time_label = ttk.Label(time_frame, text=self._format_time(self.duration_sec), style="Time.TLabel")
        self.total_time_label.pack(side="left", padx=(5,0))

        # Progress Bar (Using ttk.Scale for now, could be custom)
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Scale(self, from_=0, to=100, orient="horizontal", variable=self.progress_var, command=self.seek_audio, style="Player.Horizontal.TScale")
        self.progress_bar.grid(row=2, column=1, columnspan=3, sticky="ew", pady=(0,5))

        # Controls Frame
        controls_frame = ttk.Frame(self, style="CardInner.TFrame")
        controls_frame.grid(row=3, column=0, columnspan=4, sticky="ew", pady=5)
        controls_frame.columnconfigure([0,1,2,3,4], weight=1) # Distribute space

        # Control Buttons
        self.play_pause_button = ttk.Button(controls_frame, text=fa.icons['play'], command=self.toggle_play_pause, style="Icon.TButton")
        self.play_pause_button.grid(row=0, column=1, padx=2)

        # Placeholder for Prev/Next - these are playlist level, not track level usually
        # prev_button = ttk.Button(controls_frame, text=fa.icons['backward-step'], style="Icon.TButton") # command=self.prev_track
        # prev_button.grid(row=0, column=0, padx=2)
        # next_button = ttk.Button(controls_frame, text=fa.icons['forward-step'], style="Icon.TButton") # command=self.next_track
        # next_button.grid(row=0, column=2, padx=2)

        self.volume_var = tk.DoubleVar(value=1.0) # Default 100% volume
        self.volume_slider = ttk.Scale(controls_frame, from_=0, to=1, orient="horizontal", variable=self.volume_var, command=self.set_volume, style="Player.Horizontal.TScale", length=80)
        self.volume_slider.grid(row=0, column=3, padx=5, sticky="e")

        remove_button = ttk.Button(controls_frame, text=fa.icons['trash-can'], command=self._remove_self, style="Icon.TButton")
        remove_button.grid(row=0, column=4, padx=2, sticky="e")

        # Make the frame itself expand
        self.columnconfigure(1, weight=1) # Allow track name and progress bar to expand

    def _format_time(self, seconds):
        if seconds is None: return "0:00"
        minutes = int(seconds // 60)
        seconds = int(seconds % 60)
        return f"{minutes}:{seconds:02d}"

    def update_progress(self):
        if self.is_playing and self.sound and pygame.mixer.get_busy(): # Check if the channel is busy
            current_pos_sec = pygame.mixer.music.get_pos() / 1000.0 if self.parent_app.currently_playing_widget == self else 0
            # ^ This needs to be specific to the Sound object, not pygame.mixer.music if using Sound objects
            # For Sound objects, there's no direct get_pos(). We need to track start time or use a channel.
            # This part will be tricky with individual Sound objects if not using channels.
            # Let's assume for now that the playlist manager handles this.
            # For simplicity in widget, let's assume the parent app updates this.
            # self.progress_var.set((current_pos_sec / self.duration_sec) * 100 if self.duration_sec > 0 else 0)
            # self.current_time_label.config(text=self._format_time(current_pos_sec))

        # If using Sound objects, the main app will need to poll and update this widget
        # Or, this widget needs its own timer to estimate progress.

    def set_progress_display(self, current_time_sec, percentage):
        self.current_time_label.config(text=self._format_time(current_time_sec))
        if not self.progress_bar.winfo_ismapped(): # Avoid error if widget is being destroyed
            return
        try: # Avoid error if widget is being destroyed during update
            current_slider_val = self.progress_var.get()
            # Only set if significantly different to avoid slider jitter or if user is not dragging
            # This simple check might not be enough for smooth user dragging override
            if abs(current_slider_val - percentage) > 0.5: # Threshold to prevent fighting with user drag
                 self.progress_var.set(percentage)
        except tk.TclError:
            pass # Widget might be gone


    def toggle_play_pause(self):
        self.on_play_callback(self) # Notify parent app

    def play(self):
        if self.sound:
            self.sound.play()
            self.is_playing = True
            self.is_paused = False
            self.play_pause_button.config(text=fa.icons['pause'])
            self.parent_app.set_active_card_style(self, True)

    def pause(self):
        if self.sound and self.is_playing:
            self.sound.pause() # For Sound objects, use pause()
            self.is_playing = False # Keep playing state true, but add paused state
            self.is_paused = True
            self.play_pause_button.config(text=fa.icons['play'])
            self.parent_app.set_active_card_style(self, False)

    def resume(self):
        if self.sound and self.is_paused:
            self.sound.unpause()
            self.is_playing = True
            self.is_paused = False
            self.play_pause_button.config(text=fa.icons['pause'])
            self.parent_app.set_active_card_style(self, True)

    def stop(self):
        if self.sound:
            self.sound.stop()
            self.is_playing = False
            self.is_paused = False
            self.play_pause_button.config(text=fa.icons['play'])
            self.progress_var.set(0)
            self.current_time_label.config(text="0:00")
            self.parent_app.set_active_card_style(self, False)

    def set_volume(self, val):
        if self.sound:
            self.sound.set_volume(float(val))

    def seek_audio(self, value): # Called by progress bar Scale
        if self.sound and self.duration_sec > 0:
            seek_time_sec = (float(value) / 100.0) * self.duration_sec

            # Update internal time tracking to reflect the seek
            # This makes the progress bar visually jump to the seeked position.
            self.parent_app.update_playback_time_for_seek(self, seek_time_sec)
            self.current_time_label.config(text=self._format_time(seek_time_sec)) # Update display immediately

            if self.parent_app.currently_playing_widget == self and self.parent_app.active_channel:
                # Stop current playback on the channel
                self.parent_app.active_channel.stop()

                # Pygame Sound objects cannot be started from an offset when played on a channel directly.
                # The sound will restart from the beginning when played on the channel.
                # However, we can play the Sound object itself with a start time,
                # and if it's on the active_channel, it will take over.

                # Play the sound object (which supports `start` in seconds)
                # Pygame will pick a channel; if our active_channel was free, it might pick that one.
                # Or, we can try to ensure it plays on our active_channel if that's desired,
                # but direct control is tricky.
                # For simplicity, let pygame handle channel for this play, then re-assign active_channel if needed.

                # The most reliable way is to play the sound and then check the channel.
                # However, to maintain the idea of an "active_channel" for volume etc.,
                # we'll play it on the designated active_channel, accepting it restarts from 0.
                # The visual progress is already updated.

                self.parent_app.active_channel.play(self.sound) # This will play from the beginning of the sound.

                if self.is_paused:
                    # If it was paused, it should remain paused (audio is at start, but visually at seeked pos)
                    self.parent_app.active_channel.pause()
                elif self.is_playing:
                    # If it was playing, it should continue playing
                    # (audio from start, visually from seeked pos, progress updater handles visual sync)
                    self.is_playing = True
                    self.is_paused = False
                    self.play_pause_button.config(text=fa.icons['pause'])
                    # The progress updater will now calculate progress from the new 'playback_start_time'
                    self.parent_app.start_progress_updater()
                # else: was stopped, seeking a stopped track. It's now loaded on channel, but not playing.

    def _remove_self(self):
        self.stop()
        self.on_remove_callback(self)
        self.destroy()

    def update_theme(self):
        theme = THEME_COLORS[self.parent_app.current_theme]
        s = ttk.Style()
        s.configure("Card.TFrame", background=theme["card_bg"], relief=tk.SOLID, borderwidth=1, bordercolor=theme.get("progress_fill", "grey"))
        s.configure("CardInner.TFrame", background=theme["card_bg"])
        s.configure("TrackName.TLabel", background=theme["card_bg"], foreground=theme["text"], font=self.parent_app.font_track_name)
        s.configure("Time.TLabel", background=theme["card_bg"], foreground=theme["text"], font=self.parent_app.font_time)
        s.configure("Icon.TButton", background=theme["card_bg"], foreground=theme["progress_fill"], font=self.parent_app.font_icon, padding=2) # Smaller padding
        s.map("Icon.TButton", background=[('active', theme["hover_bg"])])

        # Progress bar and Volume slider specific theming
        s.configure("Player.Horizontal.TScale", background=theme["card_bg"], troughcolor=theme["progress_bg"])
        # For TScale, thumb color often needs more direct manipulation or custom elements not easily done with ttk styles alone.
        # We can try to set the general background, but the thumb itself might retain system/theme appearance.
        self.progress_bar.configure(style="Player.Horizontal.TScale")
        self.volume_slider.configure(style="Player.Horizontal.TScale")


        self.album_art_placeholder.config(bg=theme["progress_fill"]) # Placeholder color

        # Apply to children
        for child in self.winfo_children():
            if isinstance(child, (ttk.Label, ttk.Button, ttk.Frame, ttk.Scale)):
                self.parent_app._recursive_theme_update(child) # Use app's recursive update
            elif isinstance(child, tk.Canvas): # For album art placeholder
                 child.config(bg=theme["progress_fill"])


# --- MusicovaApp Class ---
class MusicovaApp:
    def __init__(self, root_tk):
        self.root = root_tk
        self.root.title("Musicova")
        self.root.geometry("850x750")

        try:
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=2048)
            pygame.init() # Also init pygame itself for event loop if needed for timers
        except pygame.error as e:
            print(f"Error initializing pygame.mixer: {e}")

        self.current_theme = "light"
        self._init_fonts() # Initialize fonts first
        self._apply_styles() # Then apply styles that might use these fonts

        self.container = tk.Frame(self.root)
        self.container.pack(fill="both", expand=True)
        self._apply_theme_to_widget(self.container, "bg")

        self._create_global_buttons()

        self.frames = {}
        self.frames["home"] = self.create_home_screen(self.container)
        self.frames["player"] = self.create_player_screen(self.container)

        self.playlist = [] # Stores AudioTrackWidget instances
        self.currently_playing_widget = None
        self.progress_update_timer_id = None
        self.active_channel = None # Store the channel used for playback
        self.default_button_relief = None # Store default relief for TButton


        self.show_frame("home")
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)


    def _init_fonts(self): # Adjusted font sizes slightly
        theme = THEME_COLORS[self.current_theme]
        font_family = theme["font_family"]
        icon_font_family = "FontAwesome"
        default_font = "Arial"

        def get_font(family, size, weight="normal"):
            try:
                return font.Font(family=family, size=size, weight=weight)
            except tk.TclError:
                print(f"Warning: '{family}' font not found for size {size}. Using '{default_font}'.")
                return font.Font(family=default_font, size=size, weight=weight)

        self.font_title = get_font(font_family, theme["font_size_title"], "bold")
        self.font_subtitle = get_font(font_family, theme["font_size_subtitle"])
        self.font_button = get_font(font_family, theme["font_size_button"], "bold")
        self.font_player_title = get_font(font_family, theme["font_size_player_title"], "bold")
        self.font_track_name = get_font(font_family, theme["font_size_track_name"], "normal") # Normal weight for track names
        self.font_time = get_font(font_family, theme["font_size_time"])
        self.font_icon = get_font(icon_font_family, theme["font_size_button"]) # Icon size similar to button text
        self.font_icon_small = get_font(icon_font_family, theme["font_size_icon_button"])


    def _apply_styles(self, update_fonts=False):
        if update_fonts: self._init_fonts()
        style = ttk.Style()
        theme = THEME_COLORS[self.current_theme]
        style.theme_use('clam') # Using 'clam' as it's more customizable

        # Store default relief if not already stored
        if self.default_button_relief is None:
            # Create a dummy button to get its default relief, then destroy it
            dummy_button = ttk.Button(self.root)
            self.default_button_relief = dummy_button.cget("relief")
            dummy_button.destroy()

        # --- General Widget Styling ---
        style.configure("TFrame", background=theme["bg"])
        style.configure("TLabel", background=theme["bg"], foreground=theme["text"], font=self.font_subtitle)

        # General TButton style (for main navigation, import, clear etc.)
        style.configure("TButton",
                        background=theme["button_bg"],
                        foreground=theme["button_text"],
                        font=self.font_button,
                        padding=[12, 8], # Adjusted padding
                        borderwidth=1, # Minimal border
                        relief=tk.RAISED) # Use relief for a bit of depth
        style.map("TButton",
                  background=[('active', theme["hover_bg"]), ('!disabled', theme["button_bg"])],
                  foreground=[('!disabled', theme["button_text"])],
                  relief=[('pressed', tk.SUNKEN), ('!pressed', tk.RAISED)])

        # Icon TButton style (for track card controls: play/pause, remove)
        style.configure("Icon.TButton",
                        font=self.font_icon_small,
                        padding=3,
                        background=theme["card_bg"], # Background matches card
                        foreground=theme["progress_fill"], # Icon color from progress_fill
                        borderwidth=1,
                        relief=self.default_button_relief) # Flat look for icon buttons on cards
        style.map("Icon.TButton",
                  foreground=[('active', theme["text"]), ('!disabled', theme["progress_fill"])],
                  background=[('active', theme["hover_bg"]), ('!disabled', theme["card_bg"])])

        # --- Specific Named Styles ---
        style.configure("Title.TLabel", foreground=theme["title_text"], font=self.font_title, background=theme["bg"])
        style.configure("Subtitle.TLabel", foreground=theme["text"], font=self.font_subtitle, background=theme["bg"])
        style.configure("PlayerTitle.TLabel", foreground=theme["title_text"], font=self.font_player_title, background=theme["bg"])

        # Style for TCombobox
        style.configure("TCombobox",
                        font=self.font_button,
                        padding=5,
                        fieldbackground=theme["button_bg"],
                        selectbackground=theme["button_bg"], # Background of selected item in dropdown
                        selectforeground=theme["button_text"],
                        foreground=theme["button_text"],
                        arrowcolor=theme["button_text"],
                        borderwidth=1)
        style.map("TCombobox",
            fieldbackground=[('readonly', theme["button_bg"])],
            selectbackground=[('readonly', theme["button_bg"])], # Ensure dropdown selection bg matches
            selectforeground=[('readonly', theme["button_text"])],
            foreground=[('readonly', theme["button_text"])])
        self.root.option_add('*TCombobox*Listbox.font', self.font_button)
        self.root.option_add('*TCombobox*Listbox.background', theme["button_bg"])
        self.root.option_add('*TCombobox*Listbox.foreground', theme["button_text"])
        self.root.option_add('*TCombobox*Listbox.selectBackground', theme["progress_fill"]) # Highlight color for dropdown items
        self.root.option_add('*TCombobox*Listbox.selectForeground', theme.get("card_bg", "white"))


        # Style for Vertical.TScrollbar
        style.configure("Vertical.TScrollbar",
                        background=theme["button_bg"],
                        troughcolor=theme["progress_bg"],
                        borderwidth=0,
                        arrowcolor=theme["button_text"],
                        relief=tk.FLAT)
        style.map("Vertical.TScrollbar",
                  background=[('active', theme["hover_bg"])],
                  arrowcolor=[('!disabled', theme["button_text"])])

        # --- Card Styles (used by AudioTrackWidget) ---
        style.configure("Card.TFrame", background=theme["card_bg"], relief=tk.RIDGE, borderwidth=1) # Subtle ridge
        # Active Card Style - used when a track is playing
        style.configure("ActiveCard.TFrame", background=theme["card_bg"], relief=tk.RIDGE, borderwidth=2, bordercolor=theme["progress_fill"])

        style.configure("CardInner.TFrame", background=theme["card_bg"])
        style.configure("TrackName.TLabel", background=theme["card_bg"], foreground=theme["text"], font=self.font_track_name)
        style.configure("Time.TLabel", background=theme["card_bg"], foreground=theme["text"], font=self.font_time)

        # Style for Player.Horizontal.TScale (Progress bars and Volume sliders)
        style.configure("Player.Horizontal.TScale",
                        background=theme["card_bg"], # Background of the scale widget itself
                        troughcolor=theme["progress_bg"], # Color of the groove
                        sliderrelief=tk.FLAT, # Thumb relief
                        sliderthickness=12, # Thickness of the thumb
                        borderwidth=0,
                        relief=tk.FLAT)
        # Note: ttk.Scale thumb color is hard to style directly without custom elements.
        # The 'background' option in configure often refers to the widget background, not thumb.
        # Some themes/platforms might allow 'slidercolor' or similar, but it's not standard.
        # We rely on troughcolor for the track and the system/theme's default thumb appearance.

        self._update_all_widget_themes()

    def _apply_theme_to_widget(self, widget, *style_elements):
        theme = THEME_COLORS[self.current_theme]
        config = {}
        if "bg" in style_elements: config["background"] = theme["bg"]
        if "fg" in style_elements or "text" in style_elements: config["foreground"] = theme["text"]
        if "button_bg" in style_elements: config["background"] = theme["button_bg"]
        if "button_text" in style_elements: config["foreground"] = theme["button_text"]
        if "card_bg" in style_elements: config["background"] = theme["card_bg"]
        if "card_text" in style_elements: config["foreground"] = theme["text"]
        if "title_text" in style_elements: config["foreground"] = theme["title_text"]
        if "progress_fill" in style_elements: config["background"] = theme["progress_fill"] # For canvas placeholder

        if config:
            try:
                current_style = widget.cget("style") if isinstance(widget, ttk.Widget) else ""
                # For ttk.Scale, set background for the widget, troughcolor is part of its style
                if isinstance(widget, ttk.Scale) and "Player.Horizontal.TScale" in current_style:
                    pass # Already handled by style config
                else:
                    widget.configure(**config)

                # Special handling for Combobox listbox theming (applied via option_add previously)
                if isinstance(widget, ttk.Combobox):
                    # Re-apply listbox options as they might be reset or need theme update
                    widget.tk.call("eval", f"ttk::style theme settings {style.theme_use()} {{ \
                        ttk::combobox::PopdownWindow::background {theme['button_bg']}; \
                        ttk::combobox::PopdownWindow::foreground {theme['button_text']}; \
                    }}")

            except tk.TclError:
                pass

    def _update_all_widget_themes(self):
        self._apply_theme_to_widget(self.container, "bg")
        # Global buttons like dark_mode_toggle are placed on self.root, not self.container
        if hasattr(self, 'dark_mode_toggle_button') and self.dark_mode_toggle_button.winfo_exists():
            self._recursive_theme_update(self.dark_mode_toggle_button) # Theme this button too

        for frame_key in self.frames:
            frame = self.frames[frame_key]
            if frame.winfo_exists(): # Check if frame exists
                self._apply_theme_to_widget(frame, "bg")
                for child in frame.winfo_children():
                    self._recursive_theme_update(child)

        if hasattr(self, 'dark_mode_toggle_button') and self.dark_mode_toggle_button.winfo_exists():
            self._apply_theme_to_widget(self.dark_mode_toggle_button, "button_bg", "button_text")
            self.dark_mode_toggle_button.configure(font=self.font_icon)

        if hasattr(self, 'back_button_player') and self.back_button_player.winfo_exists():
             self._apply_theme_to_widget(self.back_button_player, "button_bg", "button_text")
             self.back_button_player.configure(font=self.font_button) # It has text and icon

        # Update playlist items
        for track_widget in self.playlist:
            if track_widget.winfo_exists():
                track_widget.update_theme()


    def _recursive_theme_update(self, widget):
        if not widget.winfo_exists(): return

        theme = THEME_COLORS[self.current_theme]
        widget_style_name = widget.winfo_class() # e.g. TButton, TFrame, TCombobox

        # General theming based on widget type
        if isinstance(widget, (ttk.Button)):
            if "Icon" in widget.cget("style"): # For Icon.TButton
                widget.configure(font=self.font_icon_small)
                self._apply_theme_to_widget(widget, "card_bg", "progress_fill") # Special case for icon buttons on cards
            else: # Normal TButton
                widget.configure(font=self.font_button)
                self._apply_theme_to_widget(widget, "button_bg", "button_text")
        elif isinstance(widget, ttk.Combobox):
            widget.configure(font=self.font_button)
            # Combobox theming is complex due to listbox and field parts
            self._apply_theme_to_widget(widget, "button_bg", "button_text") # Basic theming
        elif isinstance(widget, ttk.Scale):
            self._apply_theme_to_widget(widget, "card_bg") # Background of scale itself
            widget.configure(troughcolor=theme["progress_bg"])
        elif isinstance(widget, ttk.Label):
            style_name = widget.cget("style")
            if "Title.TLabel" in style_name or "PlayerTitle.TLabel" in style_name :
                widget.configure(font=self.font_player_title if "Player" in style_name else self.font_title)
                self._apply_theme_to_widget(widget, "bg", "title_text")
            elif "Subtitle.TLabel" in style_name:
                widget.configure(font=self.font_subtitle)
                self._apply_theme_to_widget(widget, "bg", "text")
            elif "TrackName.TLabel" in style_name:
                widget.configure(font=self.font_track_name)
                self._apply_theme_to_widget(widget, "card_bg", "text")
            elif "Time.TLabel" in style_name:
                widget.configure(font=self.font_time)
                self._apply_theme_to_widget(widget, "card_bg", "text")
            else: # Default TLabel
                widget.configure(font=self.font_subtitle) # Or a more generic font
                self._apply_theme_to_widget(widget, "bg", "text")
        elif isinstance(widget, (ttk.Frame, tk.Frame)):
             # For frames inside cards (CardInner.TFrame) or general frames (TFrame)
            style_name = widget.cget("style") if isinstance(widget, ttk.Frame) else ""
            if "Card" in style_name : # Catches Card.TFrame and CardInner.TFrame
                 self._apply_theme_to_widget(widget, "card_bg")
            else: # General TFrame or tk.Frame
                 self._apply_theme_to_widget(widget, "bg")
        elif isinstance(widget, tk.Canvas): # e.g., tracks_canvas or album_art_placeholder
            if widget == getattr(self, 'tracks_canvas', None): # Main tracks canvas
                self._apply_theme_to_widget(widget, "bg")
            else: # Album art canvas
                self._apply_theme_to_widget(widget, "progress_fill") # Use progress_fill as placeholder bg

        for child in widget.winfo_children():
            self._recursive_theme_update(child)


    def _create_global_buttons(self):
        self.dark_mode_toggle_button = ttk.Button(self.root, text=fa.icons['moon'], font=self.font_icon,
                                                 command=self.toggle_dark_mode, style="TButton", width=3)
        self.dark_mode_toggle_button.place(relx=0.98, rely=0.02, anchor="ne")
        self._apply_theme_to_widget(self.dark_mode_toggle_button, "button_bg", "button_text")

    def toggle_dark_mode(self):
        self.current_theme = "dark" if self.current_theme == "light" else "light"
        new_icon = fa.icons['sun'] if self.current_theme == "dark" else fa.icons['moon']
        self.dark_mode_toggle_button.config(text=new_icon)
        self._apply_styles(update_fonts=True)

    def create_home_screen(self, parent): # Largely unchanged, ensure fonts are from self.font_...
        home_frame = ttk.Frame(parent, style="TFrame", name="home_frame")
        home_frame.grid_columnconfigure(0, weight=1)
        try:
            logo_image = Image.open("Python/Musicova logo v2.png")
            aspect_ratio = logo_image.height / logo_image.width; new_width = 350
            new_height = int(new_width * aspect_ratio)
            logo_image = logo_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            self.logo_photo_image = ImageTk.PhotoImage(logo_image)
            logo_label = ttk.Label(home_frame, image=self.logo_photo_image, style="TLabel")
            logo_label.grid(row=0, column=0, pady=(60, 20))
        except Exception as e:
            logo_label = ttk.Label(home_frame, text="Musicova", style="Title.TLabel")
            logo_label.grid(row=0, column=0, pady=(60, 20))
        self._apply_theme_to_widget(logo_label, "bg")

        title_label = ttk.Label(home_frame, text="Musicova", style="Title.TLabel", font=self.font_title)
        title_label.grid(row=1, column=0, pady=10)
        subtitle_label = ttk.Label(home_frame, text="Your Personal Music Space", style="Subtitle.TLabel", font=self.font_subtitle)
        subtitle_label.grid(row=2, column=0, pady=(0, 30))
        access_button = ttk.Button(home_frame, text="Access Musicova Player", style="TButton",
                                   command=lambda: self.show_frame("player"), font=self.font_button)
        access_button.grid(row=3, column=0, pady=20, ipady=10)
        return home_frame

    def create_player_screen(self, parent): # Ensure fonts are from self.font_...
        player_frame = ttk.Frame(parent, style="TFrame", name="player_frame")
        player_frame.pack(fill="both", expand=True)
        top_bar = ttk.Frame(player_frame, style="TFrame", height=50)
        top_bar.pack(fill="x", side="top", pady=(5,0))

        self.back_button_player = ttk.Button(top_bar, text=f"{fa.icons['arrow-left']} Back", font=self.font_button,
                                 command=lambda: self.show_frame("home"), style="TButton")
        self.back_button_player.pack(side="left", padx=20, pady=10)

        player_title_label = ttk.Label(player_frame, text="Musicova Player", style="PlayerTitle.TLabel", font=self.font_player_title)
        player_title_label.pack(pady=(10, 20))

        import_controls_frame = ttk.Frame(player_frame, style="TFrame")
        import_controls_frame.pack(pady=10)
        self.import_type_var = tk.StringVar(value="Import File(s)")
        import_type_combo = ttk.Combobox(import_controls_frame, textvariable=self.import_type_var,
                                         values=["Import File(s)", "Import Folder"], state="readonly", font=self.font_button, style="TCombobox", width=15)
        import_type_combo.pack(side="left", padx=5)
        import_button = ttk.Button(import_controls_frame, text="Import", style="TButton", command=self.handle_import, font=self.font_button)
        import_button.pack(side="left", padx=5)
        clear_playlist_button = ttk.Button(import_controls_frame, text="Clear Playlist", style="TButton", command=self.handle_clear_playlist, font=self.font_button)
        clear_playlist_button.pack(side="left", padx=5)

        tracks_outer_frame = ttk.Frame(player_frame, style="TFrame")
        tracks_outer_frame.pack(fill="both", expand=True, padx=20, pady=10)
        self.tracks_canvas = tk.Canvas(tracks_outer_frame, borderwidth=0)
        self._apply_theme_to_widget(self.tracks_canvas, "bg")
        scrollbar = ttk.Scrollbar(tracks_outer_frame, orient="vertical", command=self.tracks_canvas.yview, style="Vertical.TScrollbar")
        self.tracks_canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.tracks_canvas.pack(side="left", fill="both", expand=True)
        self.audio_tracks_frame = ttk.Frame(self.tracks_canvas, style="TFrame") # This frame gets Card.TFrame style from children
        self.tracks_canvas_window = self.tracks_canvas.create_window((0, 0), window=self.audio_tracks_frame, anchor="nw")

        self.audio_tracks_frame.bind("<Configure>", lambda e: self._on_tracks_frame_configure())
        self.tracks_canvas.bind("<Configure>", lambda e: self._on_tracks_canvas_configure(e))

        return player_frame

    def _on_tracks_frame_configure(self):
        self.tracks_canvas.configure(scrollregion=self.tracks_canvas.bbox("all"))
        # Update the width of the items inside the canvas to match the canvas width minus scrollbar
        canvas_width = self.tracks_canvas.winfo_width()
        if canvas_width > 1: # Ensure valid width
             for widget in self.audio_tracks_frame.winfo_children():
                if isinstance(widget, AudioTrackWidget):
                    widget.winfo_width() # Force update of width if needed
                    # self.tracks_canvas.itemconfigure(self.tracks_canvas_window, width=canvas_width - 20) # Approx scrollbar width
                    # widget.configure(width=canvas_width - 25) # Give a little padding
                    # widget.track_name_label.config(wraplength=canvas_width - 150) # Adjust wraplength
                    pass # Width of AudioTrackWidget is managed by its grid and packing

    def _on_tracks_canvas_configure(self, event):
        # Update the width of the frame inside the canvas to match the canvas width
        canvas_width = event.width
        if canvas_width > 1 :
             self.tracks_canvas.itemconfigure(self.tracks_canvas_window, width=canvas_width)


    def handle_import(self):
        import_type = self.import_type_var.get()
        files_to_add = []
        if import_type == "Import File(s)":
            selected_files = filedialog.askopenfilenames(
                title="Select Audio Files",
                filetypes=(("Audio Files", "*.mp3 *.wav *.ogg *.flac"), ("All files", "*.*"))
            )
            if selected_files: files_to_add.extend(list(selected_files))
        elif import_type == "Import Folder":
            folder_path = filedialog.askdirectory(title="Select Folder")
            if folder_path:
                for item in os.listdir(folder_path):
                    full_path = os.path.join(folder_path, item)
                    if os.path.isfile(full_path) and item.lower().endswith(('.mp3', '.wav', '.ogg', '.flac')):
                        files_to_add.append(full_path)

        if files_to_add:
            for idx, file_path in enumerate(files_to_add):
                # Check if track already exists
                if any(track.file_path == file_path for track in self.playlist):
                    print(f"Track {file_path} already in playlist. Skipping.")
                    continue

                track_widget = AudioTrackWidget(self.audio_tracks_frame, self, file_path,
                                                track_index=len(self.playlist),
                                                on_play_callback=self.handle_track_play_request,
                                                on_remove_callback=self.remove_track_from_playlist)
                track_widget.pack(pady=5, padx=5, fill="x", expand=True)
                self.playlist.append(track_widget)
            self._update_all_widget_themes() # Apply theme to new cards


    def handle_clear_playlist(self):
        if self.currently_playing_widget:
            self.currently_playing_widget.stop()
            self.currently_playing_widget = None

        for widget in self.playlist:
            widget.destroy()
        self.playlist.clear()

        if self.progress_update_timer_id:
            self.root.after_cancel(self.progress_update_timer_id)
            self.progress_update_timer_id = None

        pygame.mixer.music.stop() # Stop the global music stream if it was somehow used

    def handle_track_play_request(self, track_widget_to_play):
        if self.currently_playing_widget == track_widget_to_play: # Clicked on already playing/paused track
            if track_widget_to_play.is_paused:
                track_widget_to_play.resume()
                self.start_progress_updater()
            elif track_widget_to_play.is_playing:
                track_widget_to_play.pause()
                if self.progress_update_timer_id:
                    self.root.after_cancel(self.progress_update_timer_id)
                    self.progress_update_timer_id = None
            else: # Was stopped, play from start
                track_widget_to_play.play()
                self.start_progress_updater()

        else: # Clicked on a new track
            if self.currently_playing_widget:
                self.currently_playing_widget.stop() # Stop previous track

            self.currently_playing_widget = track_widget_to_play
            self.currently_playing_widget.play()
            self.start_progress_updater()

    def start_progress_updater(self):
        if self.progress_update_timer_id:
            self.root.after_cancel(self.progress_update_timer_id)
        self._update_current_track_progress()

    def _update_current_track_progress(self):
        if self.currently_playing_widget and self.currently_playing_widget.is_playing and not self.currently_playing_widget.is_paused:
            if self.currently_playing_widget.sound:
                # This is the tricky part: pygame.mixer.Sound objects don't have a get_pos()
                # We need to simulate it or use a channel which does.
                # For now, this will not update accurately without further changes to how Sound objects are handled.
                # A simple approach: if sound is playing and get_busy() is false for its channel, it finished.

                # To get position for a Sound object, you'd typically manage it via a Channel.
                # pygame.mixer.find_channel().get_sound() == self.currently_playing_widget.sound
                # However, managing channels explicitly adds complexity.
                # A simpler, less accurate way for demonstration if not using channels:
                # Assume it's playing until it's explicitly stopped or another starts.
                # The progress bar won't auto-advance without more work here.

                # --- Placeholder for accurate progress update ---
                # This requires a more involved solution, possibly timing based or using channels.
                # For now, the progress bar is mainly user-draggable or updated on state changes.
                # If we had a reliable way to get current_pos_sec for a Sound object:
                # current_pos_sec = get_current_pos_for_sound(self.currently_playing_widget.sound)
                # if self.currently_playing_widget.duration_sec > 0:
                #    percentage = (current_pos_sec / self.currently_playing_widget.duration_sec) * 100
                #    self.currently_playing_widget.set_progress_display(current_pos_sec, percentage)
                #
                #    if current_pos_sec >= self.currently_playing_widget.duration_sec:
                #        self.handle_track_ended(self.currently_playing_widget)
                #        return # Stop timer for this track

                # Check if sound finished (very basic check, might not be robust)
                # This check is not reliable for Sound objects without using Channels.
                # A Sound object once started will play until its end or stopped.
                # There's no simple "is_still_playing_on_its_own" status.
                # We'll rely on the track ending to trigger next or stop.
                # pygame.mixer.music.set_endevent(pygame.USEREVENT + 1) and checking for that event is for mixer.music, not Sound.

                # Let's simulate a simple check for now - if it's marked as playing but somehow not busy (this is flawed)
                # This part is highly dependent on how playback is managed.
                # If using Sound.play(), it plays and forgets.
                # We need to check if the sound is *actually* still making noise.
                # This often means associating the Sound object with a Channel when playing.

                # For now, the timer will just run. Manual seeking and play/pause works. Auto-next needs track end detection.
                pass


            self.progress_update_timer_id = self.root.after(250, self._update_current_track_progress) # Update ~4 times a second
        else:
            if self.progress_update_timer_id:
                self.root.after_cancel(self.progress_update_timer_id)
                self.progress_update_timer_id = None

    def handle_track_ended(self, track_widget): # Called when a track finishes
        if track_widget == self.currently_playing_widget:
            track_widget.stop() # Visually reset it
            # Implement auto-play next or stop behavior here
            current_idx = self.playlist.index(track_widget)
            if current_idx + 1 < len(self.playlist): # If there's a next track
                next_track_widget = self.playlist[current_idx + 1]
                self.handle_track_play_request(next_track_widget) # Play next
            else: # End of playlist
                self.currently_playing_widget = None
                # Stop progress updater if it was running
                if self.progress_update_timer_id:
                    self.root.after_cancel(self.progress_update_timer_id)
                    self.progress_update_timer_id = None


    def remove_track_from_playlist(self, track_widget_to_remove):
        if track_widget_to_remove == self.currently_playing_widget:
            track_widget_to_remove.stop() # Ensure it's stopped
            self.currently_playing_widget = None
            if self.progress_update_timer_id:
                self.root.after_cancel(self.progress_update_timer_id)
                self.progress_update_timer_id = None

        if track_widget_to_remove in self.playlist:
            self.playlist.remove(track_widget_to_remove)
        # Re-index subsequent tracks if necessary (optional, depends on how indices are used)
        for i, track in enumerate(self.playlist):
            track.track_index = i

        # Update canvas scroll region
        self.audio_tracks_frame.update_idletasks() # Ensure layout is updated
        self.tracks_canvas.configure(scrollregion=self.tracks_canvas.bbox("all"))


    def set_active_card_style(self, track_widget, is_active):
        theme = THEME_COLORS[self.current_theme]
        border_color = theme["progress_fill"] if is_active else theme.get("progress_bg","grey")
        border_width = 2 if is_active else 1

        try:
            if track_widget.winfo_exists():
                 track_widget.configure(relief=tk.SOLID, borderwidth=border_width, style="Card.TFrame")
                 # The style itself should define the bordercolor based on theme, but this direct config might be needed for dynamic changes.
                 # However, ttk widgets are best styled via ttk.Style.
                 # A better way: define an "ActiveCard.TFrame" style and switch the widget's style.
                 # For now, direct configuration of border for simplicity, though not ideal for pure ttk.
                 # This direct border configuration on ttk.Frame might not work as expected.
                 # Let's ensure Card.TFrame style is updated or a new one is applied.
                 # A simpler visual cue: change background slightly or add a specific label.
                 # For now, we rely on the play/pause icon and this border attempt.
        except tk.TclError:
            pass # Widget might be gone


    def show_frame(self, frame_key):
        for frame_widget_key in self.frames:
            self.frames[frame_widget_key].pack_forget()

        frame_to_show = self.frames.get(frame_key)
        if frame_to_show:
            frame_to_show.pack(fill="both", expand=True)
            if hasattr(self, 'back_button_player'):
                is_player_screen = (frame_key == "player")
                if is_player_screen: self.back_button_player.pack(side="left", padx=20, pady=10)
                else: self.back_button_player.pack_forget()
            self._apply_styles() # Re-apply styles to ensure consistency

    def _on_closing(self):
        if self.progress_update_timer_id:
            self.root.after_cancel(self.progress_update_timer_id)
        if self.currently_playing_widget:
            self.currently_playing_widget.stop()
        pygame.mixer.quit()
        pygame.quit()
        self.root.destroy()


if __name__ == "__main__":
    root_tk = tk.Tk()
    app = MusicovaApp(root_tk)
    root_tk.mainloop()

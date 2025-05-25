# Musicova

## Introduction

Musicova is an open-source music player application designed for a simple and enjoyable music listening experience. It offers both a web-based version for easy access through any modern browser and a Python-based desktop version for a native experience. The project aims to provide a clean interface with essential music playback functionalities.

## Features

Musicova comes with a range of features to enhance your listening experience:

*   **Multiple Versions:**
    *   **Web Version:** Accessible via any modern web browser.
    *   **Desktop Version:** Native application built with Python and PyQt5.
*   **Audio Playback:** Supports playback of local audio files in common formats (MP3, WAV, OGG).
*   **Music Importing:**
    *   Import individual audio files.
    *   Import all audio files from an entire folder.
*   **User Interface:**
    *   Clean, user-friendly interface for easy navigation.
    *   Dynamic audio card display for each track in the playlist.
*   **Themes:** Dark and Light theme options to suit user preference, with settings saved (localStorage for web, QSettings for Python).
*   **Playback Controls:**
    *   Play and Pause functionality.
    *   Interactive progress bar to seek through tracks.
    *   Current time and total duration display.
    *   Next/Previous track navigation (Note: Functionality might vary slightly or have known limitations between versions, especially regarding automatic play of next track).

## Technology Stack

The project utilizes the following technologies:

*   **Web Version:**
    *   HTML
    *   CSS
    *   JavaScript
*   **Desktop Version:**
    *   Python 3
    *   PyQt5 (for the graphical user interface)

## Getting Started / How to Use

### Web Version

1.  Navigate to the `HTML` directory in your file explorer.
2.  Open the `index.html` file (which should redirect to `home.html`) in your preferred web browser.
3.  Click the **"Access"** button on the home page to navigate to the music player interface.
4.  In the player:
    *   Use the dropdown menu to select either **"Choose Folder"** or **"Choose File"**.
    *   Click the **"Import"** button.
    *   Your browser's file/folder selection dialog will open. Select your music and confirm.
    *   Audio cards for the selected tracks will appear.

### Desktop Version (Python)

**Prerequisites:**

*   Python 3 installed on your system.
*   PyQt5 library. You can install it using pip:
    ```bash
    pip install PyQt5
    ```

**Instructions:**

1.  Open your terminal or command prompt.
2.  Navigate to the `Python` directory within the project.
    ```bash
    cd path/to/Musicova/Python
    ```
3.  Run the application using the Python interpreter:
    ```bash
    python musicova.py
    ```
4.  The Musicova welcome window will appear. Click the **"Access"** button to open the player window.
5.  In the player window:
    *   Use the dropdown menu to select either **"Choose Folder"** or **"Choose File"**.
    *   Click the **"Import"** button.
    *   A file/folder selection dialog will open. Select your music and confirm.
    *   Audio cards for the selected tracks will appear in the player.

### Desktop Version (Executable - if available)

If a pre-built executable is provided (e.g., `Musicova.exe` or `Musicova.app` typically found in a `dist` folder after packaging with PyInstaller):

1.  Locate the executable file (e.g., in the `dist/Musicova` directory).
2.  Double-click the executable to run the application directly.
3.  Follow the same steps as the Python version to access the player and import music.

## Screenshots

<!-- Add screenshots of the application here.
     For example:
     **Home Page (Light/Dark):**
     ![Musicova Home Light](path/to/home_light_screenshot.png)
     ![Musicova Home Dark](path/to/home_dark_screenshot.png)

     **Player Interface (Light/Dark):**
     ![Musicova Player Light](path/to/player_light_screenshot.png)
     ![Musicova Player Dark](path/to/player_dark_screenshot.png)
-->
Screenshots demonstrating the UI and themes would be beneficial here.

## Contributing

Contributions are welcome! If you'd like to improve Musicova or add new features:

1.  Fork the repository.
2.  Create a new branch for your feature or bug fix.
3.  Make your changes and commit them with clear messages.
4.  Push your changes to your fork.
5.  Submit a pull request to the main repository for review.

## License

This project is open source. Please refer to the `LICENSE` file if one is included in the repository. (If no license file is present, consider adding one, e.g., MIT License).
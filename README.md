# Dron Stream Catcher

A lightweight Python/PySide6 application designed to capture, decode, and display real-time video streams from DJI drones using MonaServer and FFplay.

---

## Key Features

- **Real-Time Video Capture:** Ingests live RTSP / UDP / RTMP video feeds directly from DJI controllers or SDK pipelines.
- **MonaServer & FFplay Integration:** Bundled server and player components for low-latency streaming.
- **PySide6 Graphical Interface:** Modern and responsive GUI for stream control.
- **Standalone Build Support:** Fully packaged application export using PyInstaller.

---

## Prerequisites & Installation

### 1. Requirements
- **Python 3.8+**
- **FFmpeg / FFplay:** The application requires `ffplay.exe`. Download it from the official FFmpeg release build and place `ffplay.exe` directly in the project root directory alongside `mona_launcher.py`.

### 2. Clone the Repository
```bash
git clone https://github.com/tomodjuro/Drone-live-stream-catching-app.git
cd Drone-live-stream-catching-app
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

---

## Running the Application (Development)

1. Ensure `ffplay.exe` is present in the project folder.
2. Run the main script:
   ```bash
   python mona_launcher.py
   ```

---

## Building Standalone Executable (.exe)

To compile the application into a standalone Windows executable using **PyInstaller**, run the following command in your terminal/command prompt:

```bash
pyinstaller --noconsole --onedir --icon=icon.ico --hidden-import PySide6 --add-data "MonaServer;MonaServer" --add-data "ffplay.exe;." --add-data "app_instructions.txt;." --add-data "icon.ico;." --name="Dron Stream Catcher" mona_launcher.py
```

After the build process completes, the output executable and its assets will be available in the `dist/Dron Stream Catcher/` folder.

---

## Project Structure

```text
Drone-live-stream-catching-app/
├── MonaServer/                             # MonaServer binaries and dependencies
├── ffplay.exe                              # FFplay executable (manually added)
├── icon.ico                                # Application icon
├── mona_launcher.py                        # Main Python GUI entry point
├── app_instructions.txt                    # User instructions guide
├── requirements.txt                        # Python dependencies
└── README.md                               # Project documentation
```

## Third-Party Software & Acknowledgments

This project bundles or integrates with the following third-party software:

- **[MonaServer](https://github.com/MonaServer/MonaServer)** - Distributed under the GNU General Public License v3.0 (GPLv3).
- **[FFmpeg / FFplay](https://ffmpeg.org/)** - Distributed under the GNU Lesser General Public License (LGPL) / GPL.

---

## License

Distributed under the MIT License. See `LICENSE` for more information.

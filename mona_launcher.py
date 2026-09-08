import sys
from datetime import datetime
import os
import subprocess

from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QSystemTrayIcon,
    QMenu,
    QDialog,
    QTextEdit,
    QHBoxLayout,
    QMessageBox
)

from PySide6.QtGui import (
    QIcon,
    QAction,
    QPixmap,
    QPainter,
    QColor
)

from PySide6.QtCore import (
    QTimer,
    Qt
)

from network import get_local_ip

from monaserver import (
    is_running,
    is_streaming,
    start_server,
    stop_server,
    get_pid
)


# Ispravno određivanje bazične mape za resurse (ikona, upute, ffplay)
if getattr(sys, "frozen", False):
    BASE_DIR = sys._MEIPASS
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

ICON_PATH = os.path.join(BASE_DIR, "icon.ico")
UPUTE_PATH = os.path.join(BASE_DIR, "upute.txt")
FFPLAY_PATH = os.path.join(BASE_DIR, "ffplay.exe")


def get_app_icon():
    """Vraća ikonu iz datoteke ili generira zamjensku ako ikona ne postoji."""
    # Ovo sada koristi ažurirani, točni ICON_PATH unutar sys._MEIPASS
    if os.path.exists(ICON_PATH):
        return QIcon(ICON_PATH)
    
    pixmap = QPixmap(32, 32)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setBrush(QColor("#0B84FF"))
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawRect(0, 0, 32, 32)
    painter.end()
    return QIcon(pixmap)


class UputeDialog(QDialog):
    """Prozor za prikaz tekstualnih uputa iz upute.md."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Upute za korištenje")
        self.resize(500, 400)
        self.setWindowIcon(get_app_icon())

        self.setStyleSheet("""
        QDialog {
            background-color: #202124;
            color: white;
            font-family: Segoe UI;
        }
        QTextEdit {
            background-color: #121212;
            color: white;
            font-size: 10pt;
            border: 1px solid #333333;
            border-radius: 6px;
            padding: 8px;
        }
        QPushButton {
            background-color: #0B84FF;
            color: white;
            border: none;
            border-radius: 6px;
            padding: 8px;
            font-size: 10pt;
        }
        QPushButton:hover {
            background-color: #3498FF;
        }
        """)

        layout = QVBoxLayout()

        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)

        if os.path.exists(UPUTE_PATH):
            try:
                with open(UPUTE_PATH, "r", encoding="utf-8", errors="replace") as f:
                    self.text_edit.setText(f.read())
            except Exception as e:
                self.text_edit.setText(f"Greška pri čitanju datoteke upute.md:\n{e}")
        else:
            self.text_edit.setText("Datoteka 'upute.md' nije pronađena u mapi aplikacije.")

        close_button = QPushButton("Zatvori")
        close_button.clicked.connect(self.accept)

        layout.addWidget(self.text_edit)
        layout.addSpacing(10)
        layout.addWidget(close_button)

        self.setLayout(layout)


class MainWindow(QWidget):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("MonaServer Launcher")
        self.setFixedSize(520, 550)

        self.app_icon = get_app_icon()
        self.setWindowIcon(self.app_icon)

        self.setStyleSheet("""
        QWidget {
            background-color: #202124;
            color: white;
            font-size: 11pt;
            font-family: Segoe UI;
        }

        QPushButton {
            background-color: #0B84FF;
            color: white;
            border: none;
            border-radius: 6px;
            padding: 10px;
            font-size: 12pt;
        }

        QPushButton:hover {
            background-color: #3498FF;
        }

        QPushButton:disabled {
            background-color: #555555;
            color: #AAAAAA;
        }

        QLabel {
            color: white;
        }
        """)

        # IP adresa
        self.ipLabel = QLabel(get_local_ip())
        self.ipLabel.setTextInteractionFlags(Qt.TextSelectableByMouse)

        # RTMP adresa s tokom /live/dron
        self.rtmpLabel = QLabel(f"rtmp://{get_local_ip()}:1935/live/dron")
        self.rtmpLabel.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.rtmpLabel.setStyleSheet("""
        color:#4DA3FF;
        font-weight:bold;
        """)

        # 1. Server Status lampica i tekst
        self.statusLight = QLabel()
        self.statusLight.setFixedSize(18, 18)
        self.statusLabel = QLabel()

        server_status_layout = QHBoxLayout()
        server_status_layout.addWidget(self.statusLight)
        server_status_layout.addWidget(self.statusLabel)
        server_status_layout.addStretch()

        # 2. Stream Status lampica i tekst (Dron)
        self.streamLight = QLabel()
        self.streamLight.setFixedSize(18, 18)
        self.streamLabel = QLabel()

        stream_status_layout = QHBoxLayout()
        stream_status_layout.addWidget(self.streamLight)
        stream_status_layout.addWidget(self.streamLabel)
        stream_status_layout.addStretch()

        # PID i Vrijeme
        self.pidLabel = QLabel("PID: -")
        self.timeLabel = QLabel("Zadnja provjera: -")

        # Gumbi
        self.uputeButton = QPushButton("Upute")
        self.playStreamButton = QPushButton("Otvori Live Stream")
        self.startButton = QPushButton("Pokreni MonaServer")
        self.stopButton = QPushButton("Zaustavi MonaServer")

        # Izgled Upute gumba
        self.uputeButton.setStyleSheet("""
        QPushButton {
            background-color: #333438;
            color: white;
            border: 1px solid #444444;
            border-radius: 6px;
            padding: 10px;
            font-size: 12pt;
        }
        QPushButton:hover {
            background-color: #44454A;
        }
        """)

        # Izgled Stream gumba (zelenkasti naglasak)
        self.playStreamButton.setStyleSheet("""
        QPushButton {
            background-color: #27AE60;
            color: white;
            border: none;
            border-radius: 6px;
            padding: 10px;
            font-size: 12pt;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #2ECC71;
        }
        QPushButton:disabled {
            background-color: #555555;
            color: #AAAAAA;
            font-weight: normal;
        }
        """)

        # Main Layout
        layout = QVBoxLayout()

        layout.addWidget(QLabel("IP adresa računala:"))
        layout.addWidget(self.ipLabel)

        layout.addSpacing(10)

        layout.addWidget(QLabel("RTMP Stream:"))
        layout.addWidget(self.rtmpLabel)

        layout.addSpacing(15)

        layout.addWidget(QLabel("Status MonaServera:"))
        layout.addLayout(server_status_layout)

        layout.addSpacing(5)

        layout.addWidget(QLabel("Status Dron Streama:"))
        layout.addLayout(stream_status_layout)

        layout.addSpacing(5)

        layout.addWidget(self.pidLabel)
        layout.addWidget(self.timeLabel)

        layout.addSpacing(15)

        layout.addWidget(self.uputeButton)
        layout.addWidget(self.playStreamButton)
        layout.addWidget(self.startButton)
        layout.addWidget(self.stopButton)

        self.setLayout(layout)

        # Signali
        self.uputeButton.clicked.connect(self.show_upute)
        self.playStreamButton.clicked.connect(self.open_stream_player)
        self.startButton.clicked.connect(self.start_clicked)
        self.stopButton.clicked.connect(self.stop_clicked)

        # Timer za osvježavanje statusa
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_status)
        self.timer.start(2000)

        # System Tray
        self.create_tray()

        # Prvo osvježavanje statusa
        self.update_status()

        # Automatsko pokretanje MonaServera pri pokretanju Launchera
        start_server()

    def show_upute(self):
        dialog = UputeDialog(self)
        dialog.exec()

    def open_stream_player(self):
        """Pokreće ffplay u ultraniskom latencijskom načinu rada s točnom stazom streama (/live/dron)."""
        if not os.path.exists(FFPLAY_PATH):
            QMessageBox.critical(
                self,
                "Datoteka nije pronađena",
                f"Datoteka 'ffplay.exe' nije pronađena na putanji:\n\n{FFPLAY_PATH}\n\n"
                "Provjeri je li ffplay.exe u istoj mapi gdje je i mona_launcher.py!"
            )
            return

        base_ip = get_local_ip()
        rtmp_url = f"rtmp://{base_ip}:1935/live/dron"

        cmd = [
            FFPLAY_PATH,
            "-rtmp_live", "live",
            "-fflags", "nobuffer",
            "-flags", "low_delay",
            "-framedrop",
            "-strict", "experimental",
            "-window_title", "Dron Live Stream (Low Latency)",
            rtmp_url
        ]

        try:
            subprocess.Popen(cmd)
        except Exception as e:
            QMessageBox.critical(
                self,
                "Greška pri pokretanju",
                f"Nije moguće pokrenuti FFplay:\n\n{str(e)}"
            )

    def update_status(self):
        now = datetime.now().strftime("%H:%M:%S")
        self.timeLabel.setText(f"Zadnja provjera: {now}")

        if is_running():
            self.statusLabel.setText("MonaServer radi")
            self.pidLabel.setText(f"PID: {get_pid()}")
            self.statusLight.setStyleSheet("""
            background-color:#2ECC71;
            border-radius:9px;
            """)
            self.startButton.setEnabled(False)
            self.stopButton.setEnabled(True)

            # Provjera primanja streama
            if is_streaming():
                self.streamLabel.setText("Stream aktivan (Dron spojen)")
                self.streamLight.setStyleSheet("""
                background-color:#2ECC71;
                border-radius:9px;
                """)
                self.playStreamButton.setEnabled(True)
            else:
                self.streamLabel.setText("Nema aktivnog streama")
                self.streamLight.setStyleSheet("""
                background-color:#E74C3C;
                border-radius:9px;
                """)
                self.playStreamButton.setEnabled(False)
        else:
            self.statusLabel.setText("MonaServer nije pokrenut")
            self.pidLabel.setText("PID: -")
            self.statusLight.setStyleSheet("""
            background-color:#E74C3C;
            border-radius:9px;
            """)

            self.streamLabel.setText("Server isključen")
            self.streamLight.setStyleSheet("""
            background-color:#555555;
            border-radius:9px;
            """)

            self.startButton.setEnabled(True)
            self.stopButton.setEnabled(False)
            self.playStreamButton.setEnabled(False)

    def start_clicked(self):
        start_server()
        self.update_status()

    def stop_clicked(self):
        stop_server()
        self.update_status()

    def create_tray(self):
        self.tray = QSystemTrayIcon(self)
        self.tray.setIcon(self.app_icon)

        menu = QMenu()

        showAction = QAction("Otvori", self)
        quitAction = QAction("Izlaz", self)

        showAction.triggered.connect(self.show_window)
        quitAction.triggered.connect(QApplication.quit)

        menu.addAction(showAction)
        menu.addAction(quitAction)

        self.tray.setContextMenu(menu)
        self.tray.show()

    def show_window(self):
        self.show()
        self.activateWindow()

    def closeEvent(self, event):
        self.tray.hide()
        self.tray.deleteLater()
        QApplication.quit()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
import subprocess
import psutil
import os
import sys

if getattr(sys, "frozen", False):
    BASE_DIR = os.path.dirname(sys.executable)
    BASE_DIR = os.path.dirname(BASE_DIR)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MONA_PATH = os.path.join(
    BASE_DIR,
    "MonaServer",
    "MonaServer.exe"
)


def is_running():
    for proc in psutil.process_iter(["name"]):
        try:
            if proc.info["name"] == "MonaServer.exe":
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    return False


def is_streaming():
    """Provjerava ima li MonaServer uspostavljenu aktivnu vezu (stream drona) na RTMP/SRT portovima."""
    for proc in psutil.process_iter(["name", "pid"]):
        try:
            if proc.info["name"] == "MonaServer.exe":
                connections = proc.connections(kind="inet")
                for conn in connections:
                    # RTMP port je 1935, SRT je 9710
                    if conn.status == psutil.CONN_ESTABLISHED and conn.laddr.port in (1935, 9710):
                        return True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    return False


def start_server():
    if is_running():
        return

    CREATE_NO_WINDOW = 0x08000000

    try:
        subprocess.Popen(
            [MONA_PATH],
            cwd=os.path.dirname(MONA_PATH),
            creationflags=CREATE_NO_WINDOW
        )
    except Exception as e:
        with open("launcher_error.txt", "w", encoding="utf-8") as f:
            f.write(str(e))


def stop_server():
    for proc in psutil.process_iter(["name"]):
        try:
            if proc.info["name"] == "MonaServer.exe":
                proc.terminate()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass


def get_pid():
    for proc in psutil.process_iter(["name", "pid"]):
        try:
            if proc.info["name"] == "MonaServer.exe":
                return proc.info["pid"]
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    return None
import socket


def get_local_ip():
    """Vrati aktivnu IPv4 adresu računala."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = "Nepoznato"
    finally:
        s.close()

    return ip
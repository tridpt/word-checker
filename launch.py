"""Launcher cho ban dong goi: chay web server va tu mo trinh duyet.

Dung cho file .exe (double-click la chay). Khi chay se mo http://127.0.0.1:<port>.
"""

import socket
import threading
import time
import webbrowser

from webapp import app


def _free_port(preferred: int = 5000) -> int:
    """Tra ve cong rong; uu tien 5000, neu ban thi xin cong bat ky."""
    for port in (preferred, 5001, 5002, 5050, 8000):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(("127.0.0.1", port)) != 0:
                return port
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def main():
    port = _free_port()
    url = f"http://127.0.0.1:{port}"

    def open_browser():
        time.sleep(1.2)
        webbrowser.open(url)

    threading.Thread(target=open_browser, daemon=True).start()
    print(f"Word Checker dang chay tai: {url}")
    print("Dong cua so nay de tat chuong trinh.")
    app.run(host="127.0.0.1", port=port)


if __name__ == "__main__":
    main()

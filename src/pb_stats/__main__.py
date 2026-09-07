"""Launch a loopback-only coordinator with a per-launch browser credential."""

import argparse
import secrets
import time
import webbrowser
from pathlib import Path
from threading import Thread
from urllib.error import URLError
from urllib.request import urlopen

import uvicorn

from pb_stats.app import create_app


def open_when_ready(url: str) -> None:
    """Wait for the shell response before opening a browser tab."""
    for _ in range(100):
        try:
            with urlopen(url.split("#", 1)[0], timeout=0.5) as response:
                if response.status == 200:
                    webbrowser.open(url)
                    return
        except (URLError, OSError):
            pass
        time.sleep(0.1)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", type=Path, default=Path(".local-workspace"))
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--no-browser", action="store_true")
    arguments = parser.parse_args()
    port = int(arguments.port)
    if not 1 <= port <= 65535:
        parser.error("port must be between 1 and 65535")
    token = secrets.token_urlsafe(32)
    static_dir = Path(__file__).resolve().parents[2] / "frontend" / "dist"
    if not (static_dir / "index.html").is_file():
        parser.error(
            "Build the UI first: npm --prefix frontend ci && npm --prefix frontend run build"
        )
    app = create_app(Path(arguments.workspace) / "metadata.sqlite3", static_dir, token, port)
    url = f"http://127.0.0.1:{port}/#session={token}"
    print(f"Open the local session: {url}", flush=True)
    if not arguments.no_browser:
        Thread(target=open_when_ready, args=(url,), daemon=True).start()
    uvicorn.run(app, host="127.0.0.1", port=port, proxy_headers=False)


if __name__ == "__main__":
    main()

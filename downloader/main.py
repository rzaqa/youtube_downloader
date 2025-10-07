import os
import sys
import tkinter as tk

from app_ui import AppUI
from downloader_service import DownloaderService, Settings


def get_yt_dlp_path():
    """Find the correct yt-dlp path inside the .app bundle."""
    if getattr(sys, "frozen", False):
        base_path = os.path.dirname(sys.executable)
        yt_dlp_path = os.path.join(base_path, "yt-dlp")
        if os.path.exists(yt_dlp_path):
            return yt_dlp_path
        else:
            print("Error: yt-dlp not found in the bundled app!")
            return None
    else:
        return "yt-dlp"


# bootstrap
YT_DLP_CMD = get_yt_dlp_path()
if not YT_DLP_CMD:
    print("yt-dlp not found! Please install yt-dlp.")
    sys.exit(1)

app = tk.Tk()
settings = Settings(downloads_dir=os.path.expanduser("~/Downloads"))
service = DownloaderService(yt_dlp_path=YT_DLP_CMD, settings=settings)
_ui = AppUI(app, service)
app.mainloop()

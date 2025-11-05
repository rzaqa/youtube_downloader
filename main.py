import os
import sys
import tkinter as tk
import traceback

from logger_config import app_logger
from app_ui import AppUI
from downloader_service import DownloaderService, Settings


def get_yt_dlp_path():
    """Find the correct yt-dlp path inside the .app bundle."""
    try:
        app_logger.log_info("Determining yt-dlp path...")
        
        if getattr(sys, "frozen", False):
            app_logger.log_info("Running as frozen/bundled app")
            
            # Try multiple possible locations for yt-dlp in the bundle
            possible_paths = [
                os.path.join(os.path.dirname(sys.executable), "yt-dlp"),  # Contents/MacOS/
                os.path.join(os.path.dirname(sys.executable), "..", "Resources", "yt-dlp"),  # Contents/Resources/
                os.path.join(os.path.dirname(sys.executable), "..", "..", "Resources", "yt-dlp"),  # Alternative path
            ]
            
            for yt_dlp_path in possible_paths:
                yt_dlp_path = os.path.abspath(yt_dlp_path)
                app_logger.log_info(f"Looking for yt-dlp at: {yt_dlp_path}")
                
                if os.path.exists(yt_dlp_path):
                    app_logger.log_info(f"yt-dlp found at: {yt_dlp_path}")
                    # Make sure it's executable
                    if not os.access(yt_dlp_path, os.X_OK):
                        app_logger.log_info("Making yt-dlp executable...")
                        os.chmod(yt_dlp_path, 0o755)
                    return yt_dlp_path
            
            app_logger.log_error("yt-dlp not found in any of the expected locations!")
            return None
        else:
            app_logger.log_info("Running in development mode")
            return "yt-dlp"
    except Exception as e:
        app_logger.log_exception("Error in get_yt_dlp_path")
        return None


def get_ffmpeg_path():
    """Find the correct ffmpeg path inside the .app bundle, if bundled.
    Returns None if not found; yt-dlp may still use a system ffmpeg if available.
    """
    try:
        app_logger.log_info("Determining ffmpeg path...")

        if getattr(sys, "frozen", False):
            app_logger.log_info("Running as frozen/bundled app (ffmpeg)")

            possible_paths = [
                os.path.join(os.path.dirname(sys.executable), "ffmpeg"),
                os.path.join(os.path.dirname(sys.executable), "..", "Resources", "ffmpeg"),
                os.path.join(os.path.dirname(sys.executable), "..", "Frameworks", "ffmpeg"),
                # Common Homebrew locations (Finder/open often lacks PATH)
                "/usr/local/bin/ffmpeg",           # Intel macs
                "/opt/homebrew/bin/ffmpeg",        # Apple Silicon macs
            ]

            for ffmpeg_path in possible_paths:
                ffmpeg_path = os.path.abspath(ffmpeg_path)
                app_logger.log_info(f"Looking for ffmpeg at: {ffmpeg_path}")
                if os.path.exists(ffmpeg_path):
                    app_logger.log_info(f"ffmpeg found at: {ffmpeg_path}")
                    if not os.access(ffmpeg_path, os.X_OK):
                        app_logger.log_info("Making ffmpeg executable...")
                        os.chmod(ffmpeg_path, 0o755)
                    return ffmpeg_path

            app_logger.log_warning("ffmpeg not found in bundled locations; audio extraction may rely on system ffmpeg")
            return None
        else:
            # In development, prefer system ffmpeg if present
            return "ffmpeg"
    except Exception:
        app_logger.log_exception("Error in get_ffmpeg_path")
        return None


def main():
    """Main application entry point with comprehensive error handling"""
    try:
        app_logger.log_system_info()
        
        # Get yt-dlp path
        app_logger.log_info("Getting yt-dlp path...")
        YT_DLP_CMD = get_yt_dlp_path()
        
        if not YT_DLP_CMD:
            app_logger.log_error("yt-dlp not found! Please install yt-dlp.")
            print("yt-dlp not found! Please install yt-dlp.")
            sys.exit(1)
        
        app_logger.log_info(f"Using yt-dlp: {YT_DLP_CMD}")
        FFMPG = get_ffmpeg_path()
        if FFMPG:
            app_logger.log_info(f"Using ffmpeg: {FFMPG}")
        else:
            app_logger.log_warning("ffmpeg not found; audio extraction may fail unless system ffmpeg is available")
        
        # Initialize Tkinter
        app_logger.log_info("Initializing Tkinter application...")
        app = tk.Tk()
        
        # Configure downloads directory
        downloads_dir = os.path.expanduser("~/Downloads")
        app_logger.log_info(f"Downloads directory: {downloads_dir}")
        
        # Create settings and service
        app_logger.log_info("Creating settings and downloader service...")
        settings = Settings(downloads_dir=downloads_dir, ffmpeg_path=FFMPG)
        service = DownloaderService(yt_dlp_path=YT_DLP_CMD, settings=settings)
        
        # Create UI
        app_logger.log_info("Creating application UI...")
        _ui = AppUI(app, service)
        
        app_logger.log_info("Starting main application loop...")
        app.mainloop()
        
        app_logger.log_info("Application closed normally")
        
    except Exception as e:
        app_logger.log_exception("Fatal error in main application")
        print(f"Fatal error: {e}")
        print("Check logs/app_logs.txt for detailed error information")
        sys.exit(1)


if __name__ == "__main__":
    main()

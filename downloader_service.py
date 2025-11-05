import os
import subprocess
import threading
from typing import Callable, List, Optional
from logger_config import app_logger


class Settings:
    def __init__(self, downloads_dir: str, ffmpeg_path: Optional[str] = None):
        self.downloads_dir = downloads_dir
        self.ffmpeg_path = ffmpeg_path


class DownloadRequest:
    def __init__(self, url: str, format_: str, quality: str):
        self.url = url
        self.format_ = format_
        self.quality = quality


class DownloaderService:
    def __init__(self, yt_dlp_path: str, settings: Settings):
        self.yt_dlp_path = yt_dlp_path
        self.settings = settings
        app_logger.log_info(f"DownloaderService initialized with yt-dlp: {yt_dlp_path}")
        app_logger.log_info(f"Downloads directory: {settings.downloads_dir}")

    def build_command(self, req: DownloadRequest) -> List[str]:
        try:
            app_logger.log_info(f"Building command for URL: {req.url}")
            app_logger.log_info(f"Format: {req.format_}, Quality: {req.quality}")
            
            command: List[str] = [
                self.yt_dlp_path,
                "-o",
                os.path.join(self.settings.downloads_dir, "%(title)s.%(ext)s"),
            ]

            # If ffmpeg is bundled or available, point yt-dlp to it explicitly
            if self.settings.ffmpeg_path:
                app_logger.log_info(f"Using ffmpeg from: {self.settings.ffmpeg_path}")
                command += ["--ffmpeg-location", self.settings.ffmpeg_path]

            if req.format_ == "Audio":
                app_logger.log_info("Adding audio extraction parameters")
                command += [
                    "--extract-audio",
                    "--audio-format",
                    "mp3",
                    "--audio-quality",
                    "0",
                    "--output",
                    os.path.join(self.settings.downloads_dir, "%(title)s.mp3"),
                ]

            if req.quality == "High":
                command += ["-f", "bestaudio/best"]
                app_logger.log_info("Using high quality format")
            elif req.quality == "Medium":
                command += ["-f", "worstaudio/worst"]
                app_logger.log_info("Using medium quality format")
            elif req.quality == "Low":
                command += ["-f", "worstaudio"]
                app_logger.log_info("Using low quality format")

            command.append(req.url)
            app_logger.log_info(f"Final command: {' '.join(command)}")
            return command
            
        except Exception as e:
            app_logger.log_exception("Error building command")
            raise

    def run(
        self,
        req: DownloadRequest,
        on_line: Callable[[str], None],
        on_done: Callable[[bool, Optional[str], Optional[str]], None],
    ) -> None:
        """Run yt-dlp in a background thread, streaming stdout lines."""

        def worker():
            try:
                app_logger.log_info("Starting download worker thread")
                
                if not self.yt_dlp_path:
                    error_msg = "yt-dlp not found! Ensure it is bundled in the app."
                    app_logger.log_error(error_msg)
                    on_line(error_msg)
                    on_done(False, None, "yt-dlp path is not configured")
                    return

                command = self.build_command(req)
                on_line("Download Started...\n")
                on_line("Running command: " + " ".join(command))

                app_logger.log_info("Starting subprocess for yt-dlp")
                # Ensure ffmpeg directory is on PATH if provided
                popen_env = None
                if self.settings.ffmpeg_path:
                    ffmpeg_dir = os.path.dirname(self.settings.ffmpeg_path)
                    popen_env = os.environ.copy()
                    popen_env["PATH"] = ffmpeg_dir + os.pathsep + popen_env.get("PATH", "")

                process = subprocess.Popen(
                    command,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    bufsize=1,
                    env=popen_env,
                )
                app_logger.log_info(f"Process started with PID: {process.pid}")

                destination_path: Optional[str] = None
                if process.stdout is not None:
                    for line in process.stdout:
                        clean = line.rstrip()
                        on_line(clean)
                        app_logger.log_debug(f"yt-dlp output: {clean}")
                        
                        if (
                            "[download]" in clean
                            and "Destination:" in clean
                            and destination_path is None
                        ):
                            destination_path = clean.split("Destination:")[-1].strip()
                            app_logger.log_info(f"Destination path found: {destination_path}")

                app_logger.log_info("Waiting for process to complete...")
                process.wait()
                app_logger.log_info(f"Process completed with return code: {process.returncode}")

                if process.returncode != 0:
                    error_message = (
                        process.stderr.read().strip()
                        if process.stderr
                        else "Unknown error"
                    )
                    app_logger.log_error(f"Download failed with return code {process.returncode}: {error_message}")
                    on_line(f"Download failed!\n{error_message}")
                    on_done(False, destination_path, error_message)
                    return

                app_logger.log_info("Download completed successfully")
                on_done(True, destination_path, None)
                
            except Exception as exc:
                app_logger.log_exception("Error in download worker thread")
                on_done(False, None, str(exc))

        threading.Thread(target=worker, daemon=True).start()

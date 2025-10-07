import os
import subprocess
import threading
from typing import Callable, List, Optional


class Settings:
    def __init__(self, downloads_dir: str):
        self.downloads_dir = downloads_dir


class DownloadRequest:
    def __init__(self, url: str, format_: str, quality: str):
        self.url = url
        self.format_ = format_
        self.quality = quality


class DownloaderService:
    def __init__(self, yt_dlp_path: str, settings: Settings):
        self.yt_dlp_path = yt_dlp_path
        self.settings = settings

    def build_command(self, req: DownloadRequest) -> List[str]:
        command: List[str] = [
            self.yt_dlp_path,
            "-o",
            os.path.join(self.settings.downloads_dir, "%(title)s.%(ext)s"),
        ]

        if req.format_ == "Audio":
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
        elif req.quality == "Medium":
            command += ["-f", "worstaudio/worst"]
        elif req.quality == "Low":
            command += ["-f", "worstaudio"]

        command.append(req.url)
        return command

    def run(
        self,
        req: DownloadRequest,
        on_line: Callable[[str], None],
        on_done: Callable[[bool, Optional[str], Optional[str]], None],
    ) -> None:
        """Run yt-dlp in a background thread, streaming stdout lines."""

        def worker():
            try:
                if not self.yt_dlp_path:
                    on_line("Error: yt-dlp not found! Ensure it is bundled in the app.")
                    on_done(False, None, "yt-dlp path is not configured")
                    return

                command = self.build_command(req)
                on_line("Download Started...\n")
                on_line("Running command: " + " ".join(command))

                process = subprocess.Popen(
                    command,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    bufsize=1,
                )

                destination_path: Optional[str] = None
                if process.stdout is not None:
                    for line in process.stdout:
                        clean = line.rstrip()
                        on_line(clean)
                        if (
                            "[download]" in clean
                            and "Destination:" in clean
                            and destination_path is None
                        ):
                            destination_path = clean.split("Destination:")[-1].strip()

                process.wait()

                if process.returncode != 0:
                    error_message = (
                        process.stderr.read().strip()
                        if process.stderr
                        else "Unknown error"
                    )
                    on_line(f"Download failed!\n{error_message}")
                    on_done(False, destination_path, error_message)
                    return

                on_done(True, destination_path, None)
            except Exception as exc:
                on_done(False, None, str(exc))

        threading.Thread(target=worker, daemon=True).start()

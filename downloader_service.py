import os
import subprocess
import threading
import sys
import shutil
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
    def __init__(self, yt_dlp_path: Optional[str], settings: Settings):
        self.yt_dlp_path = yt_dlp_path
        self.settings = settings
        self.use_python_module = False

        module_available = False
        try:
            import yt_dlp
            module_available = True
            app_logger.log_info(f"yt_dlp module file: {getattr(yt_dlp, '__file__', 'unknown')}")
            app_logger.log_info(
                f"yt_dlp module version: {getattr(getattr(yt_dlp, 'version', None), '__version__', 'unknown')}"
            )
        except ImportError:
            module_available = False

        binary_available = self._binary_is_available(yt_dlp_path)

        if binary_available and yt_dlp_path:
            try:
                result = subprocess.run(
                    [yt_dlp_path, "--version"],
                    capture_output=True,
                    text=True,
                    timeout=10,
                )
                app_logger.log_info(f"yt-dlp binary version: {result.stdout.strip()}")
            except Exception as e:
                app_logger.log_warning(f"Could not get yt-dlp binary version: {e}")

        if getattr(sys, "frozen", False):
            if module_available:
                self.use_python_module = True
                app_logger.log_info("Using yt-dlp Python module in frozen app")
            elif binary_available:
                self.use_python_module = False
                app_logger.log_info(f"Using yt-dlp binary in frozen app: {yt_dlp_path}")
            else:
                app_logger.log_error("Neither yt-dlp module nor binary is available!")
        else:
            if module_available:
                self.use_python_module = True
                app_logger.log_info("Using yt-dlp Python module in development")
            elif binary_available:
                self.use_python_module = False
                app_logger.log_info(f"Using yt-dlp binary in development: {yt_dlp_path}")
            else:
                app_logger.log_error("Neither yt-dlp module nor binary is available!")

        app_logger.log_info(f"Downloads directory: {settings.downloads_dir}")

    def _resolved_ffmpeg(self) -> Optional[str]:
        """Absolute path to ffmpeg if Settings points at a real binary or PATH name."""
        path = self.settings.ffmpeg_path
        if not path:
            return None
        if os.path.isfile(path) and os.access(path, os.X_OK):
            return os.path.abspath(path)
        resolved = shutil.which(path)
        if resolved and os.path.isfile(resolved) and os.access(resolved, os.X_OK):
            return os.path.abspath(resolved)
        return None

    @staticmethod
    def _binary_is_available(yt_dlp_path: Optional[str]) -> bool:
        if not yt_dlp_path:
            return False
        if os.path.isabs(yt_dlp_path):
            return os.path.exists(yt_dlp_path) and os.access(yt_dlp_path, os.X_OK)
        return shutil.which(yt_dlp_path) is not None

    @staticmethod
    def _audio_quality_setting(quality: str) -> str:
        """Map UI quality to ffmpeg mp3 quality (0=best, 9=smaller/lower)."""
        if quality == "High":
            return "0"
        if quality == "Medium":
            return "5"
        return "9"

    @staticmethod
    def _yt_dlp_format_selector(req: DownloadRequest) -> str:
        """Return a yt-dlp format selector: one output file when ffmpeg is available."""
        if req.format_ == "Audio":
            # Prefer m4a (aac) for reliable FFmpeg → mp3; avoid bare `best` as first pick (can confuse merge/extract).
            return "bestaudio[ext=m4a]/bestaudio/bestaudio/ba/b"

        # Video: prefer progressive MP4 when good enough; else merge DASH → one mp4 (needs ffmpeg).
        if req.quality == "High":
            return (
                "bestvideo*[height<=1080]+bestaudio/bestvideo*+bestaudio/"
                "best[ext=mp4]/best"
            )
        if req.quality == "Medium":
            return (
                "best[height<=720][ext=mp4]/bv*[height<=720]+ba/"
                "b[height<=720][ext=mp4]/b[height<=720]"
            )
        return (
            "best[height<=480][ext=mp4]/bv*[height<=480]+ba/"
            "b[height<=480][ext=mp4]/b[height<=480]"
        )

    @staticmethod
    def _safe_format_selector(req: DownloadRequest) -> str:
        """Very permissive selector used only for retry paths."""
        if req.format_ == "Audio":
            return "bestaudio/ba/b"
        return "bestvideo*+bestaudio/best[ext=mp4]/best"

    @staticmethod
    def _is_format_unavailable_error(exc: Exception) -> bool:
        message = str(exc).lower()
        return (
            "requested format is not available" in message
            or "format is not available" in message
        )

    def build_options(self, req: DownloadRequest, force_safe_format: bool = False) -> dict:
        format_selector = (
            self._safe_format_selector(req)
            if force_safe_format
            else self._yt_dlp_format_selector(req)
        )

        options = {
            "outtmpl": os.path.join(self.settings.downloads_dir, "%(title)s.%(ext)s"),
            "quiet": False,
            "no_warnings": False,
            "noplaylist": True,
            "format": format_selector,
            "merge_output_format": "mp4",
        }

        ffmpeg_exe = self._resolved_ffmpeg()
        if ffmpeg_exe:
            options["ffmpeg_location"] = ffmpeg_exe
            app_logger.log_info(f"Using ffmpeg from: {ffmpeg_exe}")

        if req.format_ == "Audio":
            options.update({
                "postprocessors": [{
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": self._audio_quality_setting(req.quality),
                    "keepvideo": False,
                }],
            })

        return options

    def build_command(self, req: DownloadRequest, force_safe_format: bool = False) -> List[str]:
        app_logger.log_info(f"Building command for URL: {req.url}")
        app_logger.log_info(f"Format: {req.format_}, Quality: {req.quality}")

        command: List[str] = [
            self.yt_dlp_path,
            "-o",
            os.path.join(self.settings.downloads_dir, "%(title)s.%(ext)s"),
            "--no-playlist",
            "--merge-output-format",
            "mp4",
        ]

        ffmpeg_exe = self._resolved_ffmpeg()
        if ffmpeg_exe:
            app_logger.log_info(f"Using ffmpeg from: {ffmpeg_exe}")
            command += ["--ffmpeg-location", ffmpeg_exe]

        if req.format_ == "Audio":
            command += [
                "--extract-audio",
                "--audio-format", "mp3",
                "--audio-quality", self._audio_quality_setting(req.quality),
            ]

        format_selector = (
            self._safe_format_selector(req)
            if force_safe_format
            else self._yt_dlp_format_selector(req)
        )
        command += ["-f", format_selector, req.url]

        app_logger.log_info(f"Final command: {' '.join(command)}")
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
                app_logger.log_info("Starting download worker thread")
                force_safe_binary_format = False

                ffmpeg_exe = self._resolved_ffmpeg()
                if ffmpeg_exe:
                    ffmpeg_bin_dir = os.path.dirname(ffmpeg_exe)
                    os.environ["PATH"] = (
                        ffmpeg_bin_dir + os.pathsep + os.environ.get("PATH", "")
                    )

                # Use Python module if available (better SSL support)
                if self.use_python_module:
                    try:
                        import yt_dlp
                        
                        options = self.build_options(req)
                        on_line("Download Started...\n")
                        on_line(f"Using yt-dlp Python module with options: {options}")
                        
                        # Create yt-dlp downloader with options
                        ydl = yt_dlp.YoutubeDL(options)
                        
                        # Create a custom progress hook to capture output
                        destination_path: Optional[str] = None
                        
                        def progress_hook(d):
                            nonlocal destination_path
                            status = d.get('status', '')
                            if status == 'downloading':
                                percent = d.get('_percent_str', 'N/A')
                                speed = d.get('_speed_str', 'N/A')
                                total = d.get('_total_bytes_str', 'N/A')
                                downloaded = d.get('downloaded_bytes', 0)
                                on_line(f"[download] {percent} of ~{total} at {speed} ETA {d.get('_eta_str', 'N/A')}")
                            elif status == 'finished':
                                filename = d.get('filename') or d.get('filepath')
                                if filename:
                                    destination_path = filename
                                total_bytes = d.get('_total_bytes_str', d.get('total_bytes', 'N/A'))
                                on_line(f"[download] 100% of {total_bytes}")
                                if destination_path:
                                    on_line(f"[download] Saved to: {destination_path}")
                        
                        ydl.add_progress_hook(progress_hook)
                        
                        # Download
                        app_logger.log_info(f"Downloading URL: {req.url}")
                        info = ydl.extract_info(req.url, download=True)
                        
                        # Determine the final file path
                        final_path = destination_path
                        if not final_path:
                            # Try to get path from info
                            if isinstance(info, dict):
                                # For playlists, get the first entry
                                if 'entries' in info and info['entries']:
                                    entry = info['entries'][0]
                                    if isinstance(entry, dict) and 'requested_downloads' in entry:
                                        if entry['requested_downloads']:
                                            final_path = entry['requested_downloads'][0].get('filepath')
                                    elif isinstance(entry, dict):
                                        final_path = entry.get('filepath') or entry.get('filename')
                                # For single videos
                                elif 'requested_downloads' in info and info['requested_downloads']:
                                    final_path = info['requested_downloads'][0].get('filepath')
                                elif 'filepath' in info:
                                    final_path = info['filepath']
                                elif 'filename' in info:
                                    final_path = info['filename']
                            
                            # Last resort: construct filename
                            if not final_path:
                                try:
                                    final_path = ydl.prepare_filename(info)
                                except:
                                    final_path = os.path.join(self.settings.downloads_dir, f"{info.get('title', 'video')}.{info.get('ext', 'mp4')}")
                        
                        app_logger.log_info(f"Download completed successfully. File: {final_path}")
                        on_done(True, final_path, None)
                        return
                        
                    except Exception as e:
                        app_logger.log_exception("Error using yt-dlp Python module")
                        error_msg = f"Python module error: {str(e)}"
                        on_line(f"Error: {error_msg}")

                        # Retry once using a very permissive selector when format matching fails.
                        if self._is_format_unavailable_error(e):
                            try:
                                import yt_dlp

                                on_line("Retrying with fallback format selector...")
                                app_logger.log_info(
                                    "Retrying Python module with fallback format selector"
                                )
                                fallback_options = self.build_options(
                                    req, force_safe_format=True
                                )
                                ydl = yt_dlp.YoutubeDL(fallback_options)
                                info = ydl.extract_info(req.url, download=True)
                                final_path = ydl.prepare_filename(info)
                                on_done(True, final_path, None)
                                return
                            except Exception:
                                app_logger.log_exception(
                                    "Fallback Python module attempt failed"
                                )
                                force_safe_binary_format = True

                        # If binary is available, continue to binary fallback instead of failing early.
                        if self.yt_dlp_path:
                            on_line("Falling back to yt-dlp binary...")
                            app_logger.log_info(
                                "Falling back to yt-dlp binary after Python module failure"
                            )
                        else:
                            on_done(False, None, error_msg)
                            return
                
                # Fallback to binary if module not available
                if not self.yt_dlp_path:
                    error_msg = "yt-dlp not found! Ensure it is bundled in the app or install yt-dlp Python package."
                    app_logger.log_error(error_msg)
                    on_line(error_msg)
                    on_done(False, None, "yt-dlp path is not configured")
                    return

                command = self.build_command(req, force_safe_format=force_safe_binary_format)
                on_line("Download Started...\n")
                on_line("Running command: " + " ".join(command))

                app_logger.log_info("Starting subprocess for yt-dlp binary")
                # Prepare environment for subprocess
                popen_env = os.environ.copy()
                
                # Ensure ffmpeg directory is on PATH if provided
                ffmpeg_exe_cmd = self._resolved_ffmpeg()
                if ffmpeg_exe_cmd:
                    ffmpeg_dir = os.path.dirname(ffmpeg_exe_cmd)
                    popen_env["PATH"] = ffmpeg_dir + os.pathsep + popen_env.get("PATH", "")
                
                # Ensure SSL certificate environment variables are passed to yt-dlp subprocess
                # These are set by configure_ssl_certificates() in main.py
                if "SSL_CERT_FILE" in os.environ:
                    popen_env["SSL_CERT_FILE"] = os.environ["SSL_CERT_FILE"]
                    app_logger.log_info(f"Passing SSL_CERT_FILE to yt-dlp: {os.environ['SSL_CERT_FILE']}")
                if "REQUESTS_CA_BUNDLE" in os.environ:
                    popen_env["REQUESTS_CA_BUNDLE"] = os.environ["REQUESTS_CA_BUNDLE"]
                    app_logger.log_info(f"Passing REQUESTS_CA_BUNDLE to yt-dlp: {os.environ['REQUESTS_CA_BUNDLE']}")

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

                stderr_output = process.stderr.read().strip() if process.stderr else ""
                if stderr_output:
                    app_logger.log_info(f"yt-dlp stderr: {stderr_output}")
                    on_line(stderr_output)

                if process.returncode != 0:
                    error_message = stderr_output or "Unknown error"
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

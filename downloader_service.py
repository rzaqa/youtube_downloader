import os
import subprocess
import threading
import sys
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
        
        # Try to use yt-dlp as Python module first (better SSL support)
        try:
            import yt_dlp
            self.use_python_module = True
            app_logger.log_info("Using yt-dlp Python module (better SSL certificate support)")
        except ImportError:
            app_logger.log_info(f"yt-dlp Python module not available, using binary: {yt_dlp_path}")
            if not yt_dlp_path:
                app_logger.log_error("Neither yt-dlp module nor binary is available!")
        
        app_logger.log_info(f"Downloads directory: {settings.downloads_dir}")

    def build_options(self, req: DownloadRequest) -> dict:
        """Build yt-dlp options dictionary for Python API."""
        options = {
            'outtmpl': os.path.join(self.settings.downloads_dir, '%(title)s.%(ext)s'),
            'quiet': False,
            'no_warnings': False,
        }
        
        # Add ffmpeg location if available
        if self.settings.ffmpeg_path and os.path.exists(self.settings.ffmpeg_path):
            options['ffmpeg_location'] = self.settings.ffmpeg_path
            app_logger.log_info(f"Using ffmpeg from: {self.settings.ffmpeg_path}")
        
        # Audio extraction options
        if req.format_ == "Audio":
            options.update({
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '0',
                }],
                'outtmpl': os.path.join(self.settings.downloads_dir, '%(title)s.%(ext)s'),
            })
        else:
            # Video quality options
            if req.quality == "High":
                options['format'] = 'best'
            elif req.quality == "Medium":
                options['format'] = 'worst'
            elif req.quality == "Low":
                options['format'] = 'worst'
        
        return options

    def build_command(self, req: DownloadRequest) -> List[str]:
        try:
            app_logger.log_info(f"Building command for URL: {req.url}")
            app_logger.log_info(f"Format: {req.format_}, Quality: {req.quality}")
            
            command: List[str] = [
                self.yt_dlp_path,
                "-o",
                os.path.join(self.settings.downloads_dir, "%(title)s.%(ext)s"),
            ]

            # Note: yt-dlp should respect SSL_CERT_FILE and REQUESTS_CA_BUNDLE environment variables
            # which are set in the subprocess environment (see run() method)
            # yt-dlp doesn't have a --cert command-line option

            # If ffmpeg is bundled or available, point yt-dlp to it explicitly
            if self.settings.ffmpeg_path:
                # The path should already be absolute from get_ffmpeg_path()
                # But ensure it's absolute and exists before using it
                ffmpeg_path = self.settings.ffmpeg_path
                
                # If somehow it's not absolute, make it absolute (but this shouldn't happen)
                if not os.path.isabs(ffmpeg_path):
                    app_logger.log_warning(f"ffmpeg path is not absolute: {ffmpeg_path}, making it absolute")
                    ffmpeg_path = os.path.abspath(ffmpeg_path)
                
                # Verify it exists
                if os.path.exists(ffmpeg_path):
                    app_logger.log_info(f"Using ffmpeg from: {ffmpeg_path}")
                    # yt-dlp --ffmpeg-location can accept either the binary path or directory
                    # We'll pass the binary path directly
                    command += ["--ffmpeg-location", ffmpeg_path]
                else:
                    app_logger.log_error(f"ffmpeg path does not exist: {ffmpeg_path}")
                    # Don't add --ffmpeg-location if path doesn't exist

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
                        on_done(False, None, error_msg)
                        return
                
                # Fallback to binary if module not available
                if not self.yt_dlp_path:
                    error_msg = "yt-dlp not found! Ensure it is bundled in the app or install yt-dlp Python package."
                    app_logger.log_error(error_msg)
                    on_line(error_msg)
                    on_done(False, None, "yt-dlp path is not configured")
                    return

                command = self.build_command(req)
                on_line("Download Started...\n")
                on_line("Running command: " + " ".join(command))

                app_logger.log_info("Starting subprocess for yt-dlp binary")
                # Prepare environment for subprocess
                popen_env = os.environ.copy()
                
                # Ensure ffmpeg directory is on PATH if provided
                if self.settings.ffmpeg_path:
                    ffmpeg_dir = os.path.dirname(self.settings.ffmpeg_path)
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

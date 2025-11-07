import os
import sys
import tkinter as tk
import traceback
import ssl

from logger_config import app_logger
from app_ui import AppUI
from downloader_service import DownloaderService, Settings

import certifi, os
print("Certifi path:", certifi.where())
print("Exists:", os.path.exists(certifi.where()))


def extract_macos_certificates():
    """Extract root certificates from macOS keychain and create a PEM file."""
    try:
        import subprocess
        import tempfile
        
        # Create a temporary file for certificates
        cert_file = os.path.join(tempfile.gettempdir(), "macos_certs.pem")
        
        # Extract certificates from macOS keychain using security command
        # This gets all root certificates trusted by the system
        try:
            result = subprocess.run(
                ['security', 'find-certificate', '-a', '-p', '/System/Library/Keychains/SystemRootCertificates.keychain'],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0 and result.stdout:
                with open(cert_file, 'w') as f:
                    f.write(result.stdout)
                app_logger.log_info(f"Extracted macOS certificates to: {cert_file}")
                return cert_file
        except Exception as e:
            app_logger.log_warning(f"Could not extract certificates from keychain: {e}")
        
        return None
    except Exception as e:
        app_logger.log_exception("Error extracting macOS certificates")
        return None


def configure_ssl_certificates():
    """Configure SSL certificates for bundled app on macOS."""
    try:
        if getattr(sys, "frozen", False):
            # Running as bundled app
            app_logger.log_info("Configuring SSL certificates for bundled app...")
            
            # Get the base directory of the executable (Contents/MacOS/)
            base_dir = os.path.dirname(os.path.abspath(sys.executable))
            contents_dir = os.path.dirname(base_dir)  # Contents/
            
            # Try bundled certifi certificate first (if bundled with PyInstaller)
            # PyInstaller places data files in different locations depending on the mode
            bundled_cert_paths = [
                os.path.join(contents_dir, "Resources", "certifi", "cacert.pem"),  # One-file mode
                os.path.join(contents_dir, "Resources", "certifi", "cacert.pem"),  # One-dir mode
                os.path.join(base_dir, "certifi", "cacert.pem"),  # Alternative location
                os.path.join(sys._MEIPASS, "certifi", "cacert.pem") if hasattr(sys, '_MEIPASS') else None,  # PyInstaller temp dir
            ]
            
            # Also check if certifi module is available in the bundle
            try:
                import certifi
                module_cert = certifi.where()
                if module_cert and os.path.exists(module_cert):
                    bundled_cert_paths.insert(0, module_cert)  # Check this first
            except ImportError:
                pass
            
            cert_path = None
            
            # Check bundled locations first
            for bundled_path in bundled_cert_paths:
                if bundled_path and os.path.exists(bundled_path):
                    cert_path = bundled_path
                    app_logger.log_info(f"Found bundled certificate at: {cert_path}")
                    break
            
            # If not found in bundle, try certifi module
            if not cert_path:
                try:
                    import certifi
                    cert_path = certifi.where()
                    if os.path.exists(cert_path):
                        app_logger.log_info(f"Using certifi certificates from: {cert_path}")
                    else:
                        cert_path = None
                except ImportError:
                    app_logger.log_warning("certifi not available")
            
            # If still no certificate, try extracting from macOS keychain
            if not cert_path or not os.path.exists(cert_path):
                app_logger.log_info("Attempting to extract certificates from macOS keychain...")
                macos_cert = extract_macos_certificates()
                if macos_cert and os.path.exists(macos_cert):
                    cert_path = macos_cert
            
            # If certifi path exists, use it
            if cert_path and os.path.exists(cert_path):
                # Set SSL certificate path for requests/urllib/yt-dlp
                os.environ['SSL_CERT_FILE'] = cert_path
                os.environ['REQUESTS_CA_BUNDLE'] = cert_path
                app_logger.log_info(f"SSL certificate environment variables set to: {cert_path}")
                
                # Create default SSL context with certifi certificates
                try:
                    ssl_context = ssl.create_default_context(cafile=cert_path)
                    ssl._create_default_https_context = lambda: ssl_context
                    app_logger.log_info("Default SSL context configured")
                except Exception as e:
                    app_logger.log_warning(f"Could not set default SSL context: {e}")
            else:
                app_logger.log_error("No SSL certificates found! SSL verification may fail.")
                # Try macOS system certificates as last resort
                try:
                    system_certs = [
                        "/etc/ssl/cert.pem",
                        "/usr/local/etc/openssl/cert.pem",
                        "/opt/homebrew/etc/openssl/cert.pem",
                    ]
                    
                    for cert_file in system_certs:
                        if os.path.exists(cert_file):
                            app_logger.log_info(f"Found system certificates at: {cert_file}")
                            os.environ['SSL_CERT_FILE'] = cert_file
                            os.environ['REQUESTS_CA_BUNDLE'] = cert_file
                            break
                except Exception as e:
                    app_logger.log_warning(f"Could not configure system certificates: {e}")
                
    except Exception as e:
        app_logger.log_exception("Error configuring SSL certificates")


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
            
            # Get the absolute path of sys.executable first
            executable_abs = os.path.abspath(sys.executable)
            app_logger.log_info(f"sys.executable: {sys.executable}")
            app_logger.log_info(f"sys.executable (absolute): {executable_abs}")
            
            # Get the base directory of the executable (Contents/MacOS/)
            base_dir = os.path.dirname(executable_abs)
            contents_dir = os.path.dirname(base_dir)  # Contents/
            
            app_logger.log_info(f"base_dir (MacOS): {base_dir}")
            app_logger.log_info(f"contents_dir: {contents_dir}")
            
            # Build absolute paths relative to the bundle structure
            # Use os.path.join with already-absolute paths to ensure we get absolute results
            possible_paths = [
                os.path.join(base_dir, "ffmpeg"),  # Contents/MacOS/ffmpeg
                os.path.join(contents_dir, "Resources", "ffmpeg"),  # Contents/Resources/ffmpeg
                os.path.join(contents_dir, "Frameworks", "ffmpeg"),  # Contents/Frameworks/ffmpeg
                # Common Homebrew locations (Finder/open often lacks PATH)
                "/usr/local/bin/ffmpeg",           # Intel macs
                "/opt/homebrew/bin/ffmpeg",        # Apple Silicon macs
            ]

            for ffmpeg_path in possible_paths:
                # Normalize path (this preserves absolute paths)
                ffmpeg_path = os.path.normpath(ffmpeg_path)
                
                app_logger.log_info(f"Looking for ffmpeg at: {ffmpeg_path}")
                app_logger.log_info(f"Path exists: {os.path.exists(ffmpeg_path)}")
                
                if os.path.exists(ffmpeg_path):
                    # Resolve symlinks to get the actual binary path
                    real_path = os.path.realpath(ffmpeg_path)
                    app_logger.log_info(f"ffmpeg found at: {ffmpeg_path} (resolved to: {real_path})")
                    
                    # Use the resolved path (real binary, not symlink)
                    if os.path.exists(real_path):
                        final_path = real_path
                    else:
                        final_path = ffmpeg_path
                    
                    # Ensure it's an absolute path (realpath should already be absolute, but be sure)
                    if not os.path.isabs(final_path):
                        final_path = os.path.abspath(final_path)
                    
                    # Make sure it's executable
                    if not os.access(final_path, os.X_OK):
                        app_logger.log_info("Making ffmpeg executable...")
                        os.chmod(final_path, 0o755)
                    
                    app_logger.log_info(f"Using ffmpeg absolute path: {final_path}")
                    return final_path

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
        
        # Configure SSL certificates first (important for bundled apps)
        configure_ssl_certificates()
        
        # Get yt-dlp path (optional if Python module is available)
        app_logger.log_info("Getting yt-dlp path...")
        YT_DLP_CMD = get_yt_dlp_path()
        
        # Check if yt-dlp Python module is available
        try:
            import yt_dlp
            app_logger.log_info("yt-dlp Python module is available - will use it instead of binary")
            # YT_DLP_CMD can be None if Python module is available
        except ImportError:
            if not YT_DLP_CMD:
                app_logger.log_error("yt-dlp not found! Please install yt-dlp (pip install yt-dlp).")
                print("yt-dlp not found! Please install yt-dlp.")
                sys.exit(1)
            app_logger.log_info(f"Using yt-dlp binary: {YT_DLP_CMD}")
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

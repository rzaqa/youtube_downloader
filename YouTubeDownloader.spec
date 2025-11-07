# -*- mode: python ; coding: utf-8 -*-

import certifi

import os
from PyInstaller.utils.hooks import collect_submodules

block_cipher = None

# Get bundled binary paths
yt_dlp_path = os.path.abspath("app_binaries/yt-dlp")
ffmpeg_path = os.path.abspath("app_binaries/ffmpeg")

# Verify yt-dlp exists (required)
if not os.path.exists(yt_dlp_path):
    raise FileNotFoundError(f"yt-dlp binary not found at {yt_dlp_path}")

# Data files to include (place under Resources via BUNDLE; COLLECT will carry them along)
datas = [(yt_dlp_path, ".")]

# Optionally include ffmpeg if present
if os.path.exists(ffmpeg_path):
    datas.append((ffmpeg_path, "."))
else:
    print("[WARN] ffmpeg not found in app_binaries/. Audio extraction may require system ffmpeg.")

# Include certifi's certificate bundle for SSL verification
try:
    import certifi
    cert_path = certifi.where()
    if os.path.exists(cert_path):
        # Bundle the certificate file - place it in Resources so it's easy to find
        # The path will be: Contents/Resources/certifi/cacert.pem
        datas.append((cert_path, os.path.join("certifi", "")))
        print(f"[INFO] Bundling SSL certificates from: {cert_path}")
        print(f"[INFO] Certificate will be available at: Contents/Resources/certifi/cacert.pem")
    else:
        print("[WARN] certifi certificate file not found")
except ImportError:
    print("[WARN] certifi not installed, SSL certificates may not work in bundled app")

# Hidden imports for tkinter, certifi, and yt_dlp
hiddenimports = collect_submodules('tkinter')
hiddenimports.append('certifi')
# Collect all yt_dlp submodules for Python API usage
try:
    yt_dlp_modules = collect_submodules('yt_dlp')
    hiddenimports.extend(yt_dlp_modules)
    print(f"[INFO] Collected {len(yt_dlp_modules)} yt_dlp submodules")
except Exception as e:
    print(f"[WARN] Could not collect yt_dlp submodules: {e}")
    hiddenimports.append('yt_dlp')  # At least add the main module

# Analysis configuration
a = Analysis(
    ['main.py'],
    pathex=['.'],
    binaries=[],
    datas=datas + [(certifi.where(), "certifi")],
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# Remove duplicate files
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# Create the executable
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='YouTube Downloader',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # You can add an icon file here if you have one
)

# Create the macOS app bundle
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='YouTube Downloader',
)

# Create macOS app bundle
app = BUNDLE(
    coll,
    name='YouTube Downloader.app',
    icon=None,  # Add icon path here if you have one
    bundle_identifier='com.yourname.youtubedownloader',
    version='1.0.0',
    info_plist={
        'NSPrincipalClass': 'NSApplication',
        'NSAppleScriptEnabled': False,
        'CFBundleDisplayName': 'YouTube Downloader',
        'CFBundleShortVersionString': '1.0.0',
        'CFBundleVersion': '1.0.0',
        'CFBundleName': 'YouTube Downloader',
        'NSHighResolutionCapable': True,
        'LSMinimumSystemVersion': '10.14.0',  # macOS Mojave and later
        'NSHumanReadableCopyright': 'Copyright © 2024',
        'NSAppleEventsUsageDescription': 'This app does not use Apple Events.',
    },
)
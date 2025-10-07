1. Install node
'''
$ brew install node
'''

Build the .app file

'''
$ pyinstaller --onefile --windowed --add-binary "/Users/zakirovrjicloud.com/Python/downloader/down_venv/bin/yt-dlp:." --name "YouTubeDownloader" main.py


'''

Created a .dmg file
$ hdiutil create -volname "YouTube Downloader" -srcfolder "dist/YouTubeDownloader.app" -ov -format UDZO "dist/YouTubeDownloader.dmg"



Delete previous version of app
$ rm -rf build dist YouTubeDownloader.spec 
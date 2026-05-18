@echo off
pyinstaller --clean --noconfirm --onefile --windowed --icon=WebCam.ico --add-binary "ffmpeg.exe;." DP_Web_Cam.py

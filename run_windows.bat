@echo off
chcp 65001 > nul
title KickSync - Windows Hizmeti
echo [*] KickSync başlatılıyor...
pip install -r requirements.txt >nul 2>&1
python app/main.py
pause

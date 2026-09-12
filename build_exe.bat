@echo off
chcp 65001 > nul
title KickSync - Windows EXE Derleyici
echo =========================================================
echo       KickSync - Windows EXE Derleyici (PyInstaller)
echo =========================================================
echo.

:: Python kontrolü
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [HATA] Bilgisayarınızda Python kurulu değil veya PATH'e eklenmemiş!
    echo Lütfen https://www.python.org/downloads/ adresinden Python'ı indirin.
    echo Kurulum ekranında EN ALTTTAKİ "Add python.exe to PATH" seçeneğini İŞARETLEYİN.
    echo.
    pause
    exit /b 1
)

echo [*] Gerekli Python kütüphaneleri kontrol ediliyor ve kuruluyor...
pip install -r requirements.txt

echo.
echo [*] KickSync.exe oluşturuluyor (Tek dosya / Arka plan modu)...
echo Lütfen 15-30 saniye bekleyin...
pyinstaller --noconsole --onefile --name "KickSync" app/main.py

if exist "dist\KickSync.exe" (
    echo.
    echo =========================================================
    echo  [BASARILI!] KickSync.exe başarıyla oluşturuldu!
    echo  Dosya konumu: dist\KickSync.exe
    echo =========================================================
    echo.
    echo KickSync.exe dosyasını masaüstünüze taşıyıp çift tıklayarak çalıştırabilirsiniz.
    echo OBS'ten yayına girdiğiniz anda Discord'unuz otomatik güncellenecektir!
    echo.
    explorer dist
) else (
    echo.
    echo [HATA] Derleme sırasında bir sorun oluştu.
)

pause

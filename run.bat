@echo off
setlocal
cd /d "%~dp0"
title CellGuys BMS Telemetry Dashboard - Python Edition

echo =====================================================================
echo          CELLGUYS BMS - TELEMETRY ^& PROTECTION DASHBOARD
echo           Samsung Innovation Campus (SIC) Stage 2 Project
echo =====================================================================
echo.

REM 1. Verifikasi instalasi Python
where python >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python tidak terdeteksi di sistem PATH Anda!
    echo.
    echo Silakan ikuti langkah berikut:
    echo 1. Unduh Python versi 3.10 atau lebih baru dari: https://www.python.org/downloads/
    echo 2. PENTING: Saat instalasi, centang kotak "Add python.exe to PATH".
    echo 3. Setelah instalasi selesai, buka kembali file run.bat ini.
    echo.
    pause
    exit /b 1
)

set VENV_DIR=.venv
set PYTHON_EXE=%VENV_DIR%\Scripts\python.exe

REM 2. Buat virtual environment jika belum ada
if not exist "%PYTHON_EXE%" (
    echo [1/3] Menyiapkan Virtual Environment Python .venv ...
    python -m venv %VENV_DIR%
    if %ERRORLEVEL% NEQ 0 (
        echo [PERINGATAN] Gagal membuat virtual environment. Menggunakan Python global...
        set PYTHON_EXE=python
    ) else (
        echo [OK] Virtual Environment berhasil dibuat.
    )
)

REM 3. Verifikasi dependensi
echo [2/3] Memeriksa dependensi aplikasi...
"%PYTHON_EXE%" -c "import PyQt6, pyqtgraph, paho.mqtt, serial" >nul 2>&1
if %ERRORLEVEL% EQU 0 goto launch_app

echo [INFO] Menginstal dependensi yang dibutuhkan: PyQt6, PyQtGraph, Paho-MQTT, PySerial...
echo        Proses ini hanya berjalan sekali saat setup awal.
"%PYTHON_EXE%" -m pip install --upgrade pip --quiet
"%PYTHON_EXE%" -m pip install -r requirements.txt
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Gagal menginstal dependensi dari requirements.txt!
    echo Pastikan komputer Anda terhubung ke internet.
    pause
    exit /b 1
)
echo [OK] Seluruh dependensi berhasil terpasang!

:launch_app
echo [OK] Dependensi lengkap.
echo.
echo [3/3] Meluncurkan CellGuys BMS Dashboard...
echo =====================================================================
echo.
"%PYTHON_EXE%" main.py %*

REM Jika aplikasi keluar dengan kode error (crash), tahan jendela CMD agar terbaca
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Aplikasi tertutup dengan error code: %ERRORLEVEL%
    echo Tekan tombol apa saja untuk menutup jendela...
    pause >nul
)

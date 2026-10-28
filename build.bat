@echo off
title Build CellGuys BMS Executable
echo ========================================================
echo  Building CellGuys BMS Standalone Executable
echo ========================================================
echo.
echo [1/3] Checking dependencies...
python -m pip install -r requirements.txt

echo.
echo [2/3] Building with PyInstaller...
pyinstaller --noconfirm --onedir --windowed --name "CellGuys_BMS" --add-data "resources;resources" --clean main.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================================
    echo  BUILD SUCCESSFUL!
    echo  Executable created at: dist\CellGuys_BMS\CellGuys_BMS.exe
    echo ========================================================
) else (
    echo.
    echo [ERROR] Build failed with error code %ERRORLEVEL%.
)
pause

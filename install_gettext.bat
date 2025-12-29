@echo off
echo ========================================
echo Installing gettext for Windows
echo ========================================
echo.
echo This script will help you install gettext tools.
echo.
echo Step 1: Download gettext
echo.
echo Please download gettext from:
echo https://mlocati.github.io/articles/gettext-iconv-windows.html
echo.
echo Download the STATIC version (not shared)
echo.
pause
echo.
echo Step 2: Extract the ZIP file
echo.
echo Extract to: C:\gettext
echo.
pause
echo.
echo Step 3: Adding to PATH...
echo.

REM Check if gettext exists
if exist "C:\gettext\bin\msgfmt.exe" (
    echo gettext found at C:\gettext\bin
    echo.
    echo Adding to PATH...
    
    REM Add to user PATH
    setx PATH "%PATH%;C:\gettext\bin" /M
    
    echo.
    echo ========================================
    echo Installation complete!
    echo ========================================
    echo.
    echo Please RESTART your terminal/IDE for changes to take effect.
    echo.
    echo Then run: python manage.py compilemessages
    echo.
) else (
    echo gettext not found at C:\gettext\bin
    echo.
    echo Please:
    echo 1. Download gettext from the link above
    echo 2. Extract to C:\gettext
    echo 3. Run this script again
    echo.
)

pause


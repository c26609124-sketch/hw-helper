@echo off
REM ============================================================
REM Homework Helper AI - Automated Setup and Launch Script
REM Windows Batch Script for Non-Technical Users
REM ============================================================

echo.
echo ========================================
echo  Homework Helper AI Setup
echo ========================================
echo.

REM Step 1: Detect Python and pip
echo [1/5] Detecting Python installation...

set PYTHON_CMD=
set PIP_CMD=

REM Test python
python --version >nul 2>&1
if %errorlevel%==0 (
    set PYTHON_CMD=python
    echo    Found: python
) else (
    REM Test python3
    python3 --version >nul 2>&1
    if %errorlevel%==0 (
        set PYTHON_CMD=python3
        echo    Found: python3
    )
)

if "%PYTHON_CMD%"=="" (
    echo.
    echo [ERROR] Python not found!
    echo.
    echo Please install Python from: https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)

echo    Python detected: %PYTHON_CMD%

REM Step 2: Detect pip
echo.
echo [2/5] Detecting pip installation...

REM Test pip
pip --version >nul 2>&1
if %errorlevel%==0 (
    set PIP_CMD=pip
    echo    Found: pip
    goto pip_found
)

REM Test pip3
pip3 --version >nul 2>&1
if %errorlevel%==0 (
    set PIP_CMD=pip3
    echo    Found: pip3
    goto pip_found
)

REM Test python -m pip
%PYTHON_CMD% -m pip --version >nul 2>&1
if %errorlevel%==0 (
    set PIP_CMD=%PYTHON_CMD% -m pip
    echo    Found: %PYTHON_CMD% -m pip
    goto pip_found
)

echo.
echo [ERROR] pip not found!
echo.
echo Please install pip using: %PYTHON_CMD% -m ensurepip --upgrade
echo.
pause
exit /b 1

:pip_found
echo    pip detected: %PIP_CMD%

REM Step 3: Install requirements
echo.
echo [3/5] Installing Python dependencies...
echo    This may take a few minutes...
echo.

%PIP_CMD% install -r requirements.txt

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Failed to install requirements!
    echo.
    echo Please check your internet connection and try again.
    echo If the problem persists, install manually:
    echo    %PIP_CMD% install customtkinter Pillow selenium requests protobuf
    echo.
    pause
    exit /b 1
)

echo.
echo    All dependencies installed successfully!

REM Step 4: Check for Brave browser
echo.
echo [4/5] Checking for Brave browser...

set BRAVE_PATH=C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe

if exist "%BRAVE_PATH%" (
    echo    Brave browser found: %BRAVE_PATH%
) else (
    echo.
    echo [WARNING] Brave browser not found at expected location:
    echo    %BRAVE_PATH%
    echo.
    echo Please install Brave from: https://brave.com/download/
    echo.
    echo You can continue setup, but the screenshot capture
    echo feature will not work until Brave is installed.
    echo.
    pause
)

REM Step 5: Check configuration
echo.
echo [5/5] Checking configuration...

if exist "config.json" (
    echo    Configuration file found: config.json
) else (
    echo    Creating default configuration file...
    (
        echo {
        echo     "api_key": "",
        echo     "selected_model": "google/gemini-2.5-flash"
        echo }
    ) > config.json
    echo    Created: config.json
    echo.
    echo    [NOTE] Please add your OpenRouter API key in the Settings panel
    echo           after the application launches.
)

REM Launch application
echo.
echo ========================================
echo  Setup Complete!
echo ========================================
echo.
echo Launching Homework Helper AI...
echo.

%PYTHON_CMD% ui.py

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Application failed to start!
    echo.
    echo Please check the error messages above.
    echo.
    pause
    exit /b 1
)

pause

@echo off
REM AxiomSon auto-setup and launch script for Windows

echo.
echo ========================================
echo AxiomSon - Auto Setup
echo ========================================
echo.

REM Check if Python 3.14 is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python 3.14 is required.
    pause
    exit /b 1
)

REM Verify the version of Python
python --version | findstr "3.14" >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python 3.14 is required.
    pause
    exit /b 1
)

REM Create virtual environment if it doesn't exist
if not exist ".venv" (
    echo [1/3] Creating virtual environment...
    python -m venv .venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment.
        pause
        exit /b 1
    )
)

REM Activate virtual environment
echo [2/3] Activating virtual environment...
call .venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment.
    pause
    exit /b 1
)

REM Install requirements
echo [3/3] Installing dependencies from requirements.txt...
pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo ERROR: Failed to install dependencies.
    echo Try running: pip install -r requirements.txt
    pause
    exit /b 1
)

echo.
echo ========================================
echo Setup complete! Launching AxiomSon...
echo ========================================
echo.

REM Launch the application
python alpha.py --gui

REM Keep window open if there's an error
if errorlevel 1 (
    echo.
    echo ERROR: Application exited with code %errorlevel%
    pause
)

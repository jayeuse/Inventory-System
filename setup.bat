@echo off
REM Quick setup script for Windows users
REM Run this after cloning the repository

echo ================================================================================
echo INVENTORY SYSTEM - AUTOMATED SETUP
echo ================================================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.11+ and try again
    pause
    exit /b 1
)

echo Step 1: Creating virtual environment...
if not exist "env" (
    python -m venv env
    echo Virtual environment created!
) else (
    echo Virtual environment already exists.
)
echo.

echo Step 2: Activating virtual environment...
call env\Scripts\activate
echo.

echo Step 3: Installing dependencies...
pip install -r requirements.txt
echo.

echo Step 4: Initializing database...
echo NOTE: Make sure PostgreSQL is running and credentials are configured!
echo.
python manage.py init_db
echo.

echo ================================================================================
echo SETUP COMPLETE!
echo ================================================================================
echo.
echo Next steps:
echo 1. Create a superuser: python manage.py createsuperuser
echo 2. Run the server: python manage.py runserver
echo 3. Visit: http://localhost:8000
echo.
echo To activate the virtual environment in future sessions, run:
echo    env\Scripts\activate
echo.
pause

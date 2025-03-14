@echo off
echo Setting up Task Management System environment...

:: Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Python is not installed! Please install Python 3.x and try again.
    pause
    exit /b 1
)

:: Check if virtual environment exists, if not create it
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

:: Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate

:: Install required packages
echo Installing required packages...
pip install flask
pip install flask-sqlalchemy
pip install flask-login
pip install flask-migrate
pip install werkzeug
pip install requests

:: Initialize database
echo Initializing database...
python -c "from app import db, app; app.app_context().push(); db.create_all()"

:: Create uploads directory if it doesn't exist
if not exist static\uploads (
    echo Creating uploads directory...
    mkdir static\uploads
)

echo.
echo Installation completed successfully!
echo To run the application, use: 
python app.py


pause 
@echo off
REM Quick start script for EverMemOS Memory Server (Windows)

echo 🚀 Starting EverMemOS Memory Server...
echo.

REM Check if .env file exists
if not exist .env (
    echo ⚠️  .env file not found!
    echo 📋 Copying .env.example to .env...
    copy .env.example .env
    echo ✅ Please edit .env file and set your EVERMEMOS_API_KEY
    echo.
)

REM Check if dependencies are installed
python -c "import fastapi" 2>nul
if errorlevel 1 (
    echo 📦 Installing dependencies...
    pip install -r requirements.txt
    echo.
)

REM Start the server
echo 🔌 Starting server on http://localhost:8000
echo 📖 API docs available at http://localhost:8000/docs
echo.
python main.py

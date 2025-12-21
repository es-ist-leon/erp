@echo off
title HolzbauERP
cd /d "%~dp0"

:: Try to find Python - check common paths first to avoid Windows Store alias
set PYTHON_EXE=
if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" (
    set PYTHON_EXE=%LOCALAPPDATA%\Programs\Python\Python312\python.exe
) else if exist "%LOCALAPPDATA%\Programs\Python\Python311\python.exe" (
    set PYTHON_EXE=%LOCALAPPDATA%\Programs\Python\Python311\python.exe
) else if exist "%LOCALAPPDATA%\Programs\Python\Python310\python.exe" (
    set PYTHON_EXE=%LOCALAPPDATA%\Programs\Python\Python310\python.exe
) else if exist "C:\Python312\python.exe" (
    set PYTHON_EXE=C:\Python312\python.exe
) else if exist "C:\Python311\python.exe" (
    set PYTHON_EXE=C:\Python311\python.exe
) else if exist "C:\Program Files\Python312\python.exe" (
    set PYTHON_EXE=C:\Program Files\Python312\python.exe
) else if exist "C:\Program Files\Python311\python.exe" (
    set PYTHON_EXE=C:\Program Files\Python311\python.exe
)

if "%PYTHON_EXE%"=="" (
    echo Python wurde nicht gefunden!
    echo Bitte installieren Sie Python von https://www.python.org/
    echo.
    echo WICHTIG: Bei der Installation "Add Python to PATH" aktivieren!
    pause
    exit /b 1
)

echo Python gefunden: %PYTHON_EXE%

:: Check if venv exists
if not exist "venv" (
    echo Erstelle virtuelle Python-Umgebung...
    %PYTHON_EXE% -m venv venv
)

:: Activate venv and run
call venv\Scripts\activate.bat

:: Check if dependencies are installed
"%~dp0venv\Scripts\python.exe" -c "import PyQt6" >nul 2>&1
if errorlevel 1 (
    echo Installiere Abhaengigkeiten...
    echo Dies kann einige Minuten dauern...
    "%~dp0venv\Scripts\pip.exe" install -r requirements.txt
)

:: Run the application
echo.
echo Starte HolzbauERP...
echo.
"%~dp0venv\Scripts\python.exe" -m app.main

:: If error occurred
if errorlevel 1 (
    echo.
    echo Fehler beim Starten der Anwendung.
    echo.
    pause
)

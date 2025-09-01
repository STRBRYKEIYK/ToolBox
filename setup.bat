@echo off
REM WorkBox Setup Helper Script for Windows
REM This script helps run the WorkBox application with the correct Python path

echo === WorkBox Setup Helper ===
echo.

REM Find Python executable
set PYTHON_PATH="C:/Program Files/Python313/python.exe"
if not exist %PYTHON_PATH% (
    echo Trying to find Python...
    where python > nul 2>&1
    if %ERRORLEVEL% equ 0 (
        set PYTHON_PATH=python
    ) else (
        echo Python not found in PATH
        echo Looking for Python in common locations...
        
        if exist "C:\Python311\python.exe" (
            set PYTHON_PATH="C:\Python311\python.exe"
        ) else if exist "C:\Python310\python.exe" (
            set PYTHON_PATH="C:\Python310\python.exe"
        ) else if exist "C:\Python39\python.exe" (
            set PYTHON_PATH="C:\Python39\python.exe"
        ) else if exist "C:\Program Files\Python310\python.exe" (
            set PYTHON_PATH="C:\Program Files\Python310\python.exe"
        ) else if exist "C:\Program Files\Python39\python.exe" (
            set PYTHON_PATH="C:\Program Files\Python39\python.exe"
        ) else (
            echo Python not found. Please install Python and try again.
            goto :eof
        )
    )
)

echo Using Python at: %PYTHON_PATH%
echo.

if "%1"=="" goto showMenu

if "%1"=="install" (
    echo Installing dependencies...
    %PYTHON_PATH% -m pip install -r requirements.txt
    goto :eof
)

if "%1"=="setup" (
    echo Running MySQL setup...
    %PYTHON_PATH% setup_mysql.py
    goto :eof
)

if "%1"=="init" (
    echo Initializing database...
    %PYTHON_PATH% init_db.py
    goto :eof
)

if "%1"=="run" (
    echo Starting WorkBox server...
    %PYTHON_PATH% main.py
    goto :eof
)

if "%1"=="manage" (
    echo Running connection manager...
    %PYTHON_PATH% manage_connection.py
    goto :eof
)

if "%1"=="migrate" (
    if "%2"=="" (
        echo Missing migration command
        echo Usage: setup.bat migrate [setup^|create^|apply^|rollback^|history] [message]
        goto :eof
    )
    if "%2"=="create" (
        if "%3"=="" (
            echo Missing migration message
            echo Usage: setup.bat migrate create "Your migration message"
            goto :eof
        )
        %PYTHON_PATH% migrations.py create "%3"
    ) else (
        %PYTHON_PATH% migrations.py %2
    )
    goto :eof
)

:showMenu
echo Please select an option:
echo.
echo 1. Install dependencies
echo 2. Setup MySQL connection
echo 3. Initialize database
echo 4. Start WorkBox server
echo 5. Manage database connection
echo 6. Run migrations
echo 0. Exit
echo.

set /p choice=Enter your choice (0-6): 

if "%choice%"=="1" (
    %PYTHON_PATH% -m pip install -r requirements.txt
) else if "%choice%"=="2" (
    %PYTHON_PATH% setup_mysql.py
) else if "%choice%"=="3" (
    %PYTHON_PATH% init_db.py
) else if "%choice%"=="4" (
    %PYTHON_PATH% main.py
) else if "%choice%"=="5" (
    %PYTHON_PATH% manage_connection.py
) else if "%choice%"=="6" (
    echo Migration options:
    echo  a. Setup migration system
    echo  b. Create new migration
    echo  c. Apply migrations
    echo  d. Rollback migration
    echo  e. Show migration history
    echo  x. Back to main menu
    
    set /p migChoice=Enter your choice (a-e, x): 
    
    if "%migChoice%"=="a" (
        %PYTHON_PATH% migrations.py setup
    ) else if "%migChoice%"=="b" (
        set /p message=Enter migration message: 
        %PYTHON_PATH% migrations.py create "%message%"
    ) else if "%migChoice%"=="c" (
        %PYTHON_PATH% migrations.py apply
    ) else if "%migChoice%"=="d" (
        %PYTHON_PATH% migrations.py rollback
    ) else if "%migChoice%"=="e" (
        %PYTHON_PATH% migrations.py history
    ) else if "%migChoice%"=="x" (
        goto :showMenu
    )
) else if "%choice%"=="0" (
    echo Goodbye!
) else (
    echo Invalid choice
)

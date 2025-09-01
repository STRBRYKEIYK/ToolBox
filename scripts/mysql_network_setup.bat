@echo off
REM =========================================
REM MySQL Network Setup - Complete Solution
REM =========================================

echo ======================================================
echo   MySQL Network Configuration - Complete Solution
echo ======================================================
echo.

REM Check if running as administrator
NET SESSION >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo This script requires administrator privileges to configure MySQL properly.
    echo Please right-click this script and select "Run as administrator"
    pause
    exit /b 1
)

REM Find Python executable
for %%A in (
    "C:\Program Files\Python313\python.exe"
    "C:\Program Files\Python312\python.exe"
    "C:\Program Files\Python311\python.exe"
    "C:\Program Files\Python310\python.exe"
    "C:\Program Files\Python39\python.exe"
    "C:\Program Files\Python38\python.exe"
    "C:\Python313\python.exe"
    "C:\Python312\python.exe"
    "C:\Python311\python.exe"
    "C:\Python310\python.exe"
    "C:\Python39\python.exe"
    "C:\Python38\python.exe"
    "python.exe"
) do (
    if exist %%A (
        set PYTHON_PATH=%%A
        goto python_found
    )
)

echo Python not found! Please install Python 3.8 or newer.
exit /b 1

:python_found
echo Using Python at: %PYTHON_PATH%
echo.

:menu
echo Please select an option:
echo.
echo 1. Configure MySQL for Network Access (All-in-One Setup)
echo 2. Configure MySQL bind-address only
echo 3. Configure MySQL user permissions only
echo 4. Update application database settings
echo 5. Test MySQL network connectivity
echo 6. Start WorkBox server after configuration
echo 0. Exit
echo.

set /p choice=Enter your choice (0-6): 

if "%choice%"=="1" (
    goto configure_all
) else if "%choice%"=="2" (
    goto configure_bind_address
) else if "%choice%"=="3" (
    goto configure_mysql_user
) else if "%choice%"=="4" (
    goto update_db_connection
) else if "%choice%"=="5" (
    goto test_connection
) else if "%choice%"=="6" (
    goto start_server
) else if "%choice%"=="0" (
    echo Exiting...
    exit /b 0
) else (
    echo Invalid choice
    goto menu
)

:configure_all
echo.
echo === STEP 1: Configuring MySQL bind-address ===
echo.
call :configure_bind_address

echo.
echo === STEP 2: Configuring MySQL user permissions ===
echo.
call :configure_mysql_user

echo.
echo === STEP 3: Updating application database settings ===
echo.
call :update_db_connection

echo.
echo === STEP 4: Testing MySQL network connectivity ===
echo.
call :test_connection

echo.
echo === ALL STEPS COMPLETED SUCCESSFULLY ===
echo.
echo Your MySQL server should now be properly configured for network access.
echo.
set /p start_now=Would you like to start the WorkBox server now? (y/n): 
if /i "%start_now%"=="y" (
    call :start_server
) else (
    goto menu
)

:configure_bind_address
echo Configuring MySQL bind-address to allow remote connections...
echo.

set MYSQL_CONF_FOUND=0
set MYSQL_CONF_PATH=

REM Detect possible MySQL configuration locations
for %%v in (8.0 8.1 5.7 5.8) do (
    if exist "C:\ProgramData\MySQL\MySQL Server %%v\my.ini" (
        set MYSQL_CONF_PATH=C:\ProgramData\MySQL\MySQL Server %%v\my.ini
        set MYSQL_CONF_FOUND=1
        goto found_mysql_conf
    )
)

REM Check other common locations
if exist "C:\my.ini" (
    set MYSQL_CONF_PATH=C:\my.ini
    set MYSQL_CONF_FOUND=1
    goto found_mysql_conf
)

if exist "C:\Program Files\MySQL\my.ini" (
    set MYSQL_CONF_PATH=C:\Program Files\MySQL\my.ini
    set MYSQL_CONF_FOUND=1
    goto found_mysql_conf
)

:found_mysql_conf
if %MYSQL_CONF_FOUND%==0 (
    echo Could not automatically locate your MySQL configuration file.
    echo.
    echo Please enter the full path to your MySQL configuration file (my.ini or my.cnf):
    set /p MYSQL_CONF_PATH=Path: 
)

if not exist "%MYSQL_CONF_PATH%" (
    echo Error: The file %MYSQL_CONF_PATH% does not exist.
    goto menu
)

echo Found MySQL configuration at: %MYSQL_CONF_PATH%
echo.

REM Check if bind-address is already set to 0.0.0.0
findstr /C:"bind-address = 0.0.0.0" "%MYSQL_CONF_PATH%" >nul
if %ERRORLEVEL%==0 (
    echo MySQL is already configured to accept connections from any IP address.
    echo bind-address = 0.0.0.0 already set.
    echo.
    goto restart_mysql_service
)

REM Create backup of config file
copy "%MYSQL_CONF_PATH%" "%MYSQL_CONF_PATH%.bak" >nul
echo Backup created at %MYSQL_CONF_PATH%.bak

REM Check if bind-address exists with a different value
findstr /C:"bind-address" "%MYSQL_CONF_PATH%" >nul
if %ERRORLEVEL%==0 (
    echo Found existing bind-address setting. Updating to 0.0.0.0...
    
    REM Use PowerShell to replace the existing bind-address
    powershell -Command "(Get-Content '%MYSQL_CONF_PATH%') -replace 'bind-address\s*=\s*\S+', 'bind-address = 0.0.0.0' | Set-Content '%MYSQL_CONF_PATH%'"
) else (
    echo No bind-address setting found. Adding it to [mysqld] section...
    
    REM Use PowerShell to add bind-address after [mysqld]
    powershell -Command "$content = Get-Content '%MYSQL_CONF_PATH%'; $index = [array]::IndexOf($content, '[mysqld]'); if($index -ge 0) { $content[$index] = $content[$index] + \"`n# Network settings for remote access`nbind-address = 0.0.0.0\"; $content | Set-Content '%MYSQL_CONF_PATH%' }"
)

echo Updated MySQL configuration with bind-address = 0.0.0.0

:restart_mysql_service
echo.
echo MySQL service needs to be restarted for changes to take effect.
set /p restart=Would you like to restart MySQL service now? (y/n): 

if /i "%restart%"=="y" (
    echo Restarting MySQL service...
    net stop MySQL80 >nul 2>&1
    if %ERRORLEVEL% NEQ 0 (
        net stop MySQL >nul 2>&1
    )
    
    net start MySQL80 >nul 2>&1
    if %ERRORLEVEL% NEQ 0 (
        net start MySQL >nul 2>&1
    )
    echo MySQL service restarted.
) else (
    echo.
    echo Please remember to restart MySQL service manually for changes to take effect:
    echo net stop MySQL
    echo net start MySQL
)
goto :eof

:configure_mysql_user
echo Configuring MySQL user for remote access...
echo.

echo You'll need your MySQL root username and password.
echo.

set /p MYSQL_USER=Enter your MySQL root username (default: root): 
if "%MYSQL_USER%"=="" set MYSQL_USER=root

set /p MYSQL_PASS=Enter your MySQL root password: 
echo.

echo Checking MySQL connection...
mysql -u%MYSQL_USER% -p%MYSQL_PASS% -e "SELECT VERSION();" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Error: Could not connect to MySQL server with the provided credentials.
    goto menu
)

echo Connection successful.
echo.

echo Checking for existing workbox_user...
mysql -u%MYSQL_USER% -p%MYSQL_PASS% -e "SELECT EXISTS(SELECT 1 FROM mysql.user WHERE user = 'workbox_user') AS user_exists;" > mysql_check.tmp
type mysql_check.tmp | find "1" >nul
if %ERRORLEVEL% EQU 0 (
    echo User 'workbox_user' exists. Checking for remote access...
    
    mysql -u%MYSQL_USER% -p%MYSQL_PASS% -e "SELECT user, host FROM mysql.user WHERE user = 'workbox_user';" > mysql_hosts.tmp
    type mysql_hosts.tmp | find "%%" >nul
    
    if %ERRORLEVEL% EQU 0 (
        echo User already has access from any host ('%%').
    ) else (
        echo User exists but doesn't have access from any host. Granting access...
        
        set /p WB_PASS=Enter password for workbox_user (or press Enter to use 'password'): 
        if "%WB_PASS%"=="" set WB_PASS=password
        
        mysql -u%MYSQL_USER% -p%MYSQL_PASS% -e "CREATE USER IF NOT EXISTS 'workbox_user'@'%%' IDENTIFIED BY '%WB_PASS%'; GRANT ALL PRIVILEGES ON workbox_db.* TO 'workbox_user'@'%%'; FLUSH PRIVILEGES;"
        
        if %ERRORLEVEL% EQU 0 (
            echo Access granted successfully.
        ) else (
            echo Error granting access.
        )
    )
) else (
    echo User 'workbox_user' doesn't exist. Creating user with remote access...
    
    set /p WB_PASS=Enter password for new workbox_user (or press Enter to use 'password'): 
    if "%WB_PASS%"=="" set WB_PASS=password
    
    mysql -u%MYSQL_USER% -p%MYSQL_PASS% -e "CREATE USER 'workbox_user'@'%%' IDENTIFIED BY '%WB_PASS%'; CREATE DATABASE IF NOT EXISTS workbox_db; GRANT ALL PRIVILEGES ON workbox_db.* TO 'workbox_user'@'%%'; FLUSH PRIVILEGES;"
    
    if %ERRORLEVEL% EQU 0 (
        echo User created successfully with remote access.
    ) else (
        echo Error creating user.
    )
)

echo.
echo Verifying configuration...
mysql -u%MYSQL_USER% -p%MYSQL_PASS% -e "SELECT user, host FROM mysql.user WHERE user = 'workbox_user';"

REM Cleanup temporary files
del mysql_check.tmp 2>nul
del mysql_hosts.tmp 2>nul

goto :eof

:update_db_connection
echo Updating database connection settings...
echo.
%PYTHON_PATH% update_db_connection.py
goto :eof

:test_connection
echo Testing MySQL network connectivity...
echo.
echo Getting local IP address...
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /R /C:"IPv4 Address"') do (
    set IP_ADDRESS=%%a
    goto got_ip
)

:got_ip
set IP_ADDRESS=%IP_ADDRESS:~1%
echo Your computer's IP address: %IP_ADDRESS%
echo.

echo Testing if MySQL is listening on all interfaces...
netstat -an | findstr ":3306"
echo.

echo You should see 0.0.0.0:3306 in the list above.
echo If you only see 127.0.0.1:3306, MySQL is not properly configured for remote access.
echo.

echo To test from another device, run this command on that device:
echo mysql -h %IP_ADDRESS% -u workbox_user -p workbox_db
echo.

echo API server will be available at: http://%IP_ADDRESS%:8000/docs
echo.

pause
goto :eof

:start_server
echo Starting WorkBox server...
call setup.bat run
goto :eof

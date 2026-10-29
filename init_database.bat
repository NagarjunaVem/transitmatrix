@echo off
setlocal enabledelayedexpansion

title TransitMatrix Database Initializer
echo ===============================================================================
echo TransitMatrix: Intelligent Railway and Public Transit Management System
echo One-Click Database Setup and Verification Utility
echo ===============================================================================
echo.

:: -----------------------------------------------------------------------------
:: Step 1: Resolve Working Directory & Load .env
:: -----------------------------------------------------------------------------
set "PROJECT_DIR=%~dp0"
cd /d "%PROJECT_DIR%"
set "FORWARD_SLASH_DIR=%PROJECT_DIR:\=/%"

set "DB_HOST=localhost"
set "DB_PORT=3306"
set "DB_USER=root"
set "DB_PASS="
set "DB_NAME=transitmatrix"

if exist "%PROJECT_DIR%.env" (
    for /f "usebackq tokens=1,* delims==" %%A in ("%PROJECT_DIR%.env") do (
        set "ENV_KEY=%%A"
        set "ENV_VAL=%%B"
        for /f "tokens=* delims= " %%K in ("!ENV_KEY!") do set "ENV_KEY=%%K"
        for /f "tokens=* delims= " %%V in ("!ENV_VAL!") do set "ENV_VAL=%%V"
        if "!ENV_KEY!"=="MYSQL_HOST" set "DB_HOST=!ENV_VAL!"
        if "!ENV_KEY!"=="MYSQL_PORT" set "DB_PORT=!ENV_VAL!"
        if "!ENV_KEY!"=="MYSQL_USER" set "DB_USER=!ENV_VAL!"
        if "!ENV_KEY!"=="MYSQL_PASSWORD" set "DB_PASS=!ENV_VAL!"
        if "!ENV_KEY!"=="MYSQL_DATABASE" set "DB_NAME=!ENV_VAL!"
    )
)

echo [INFO] Target Database: %DB_USER%@%DB_HOST%:%DB_PORT%/%DB_NAME%
echo.

:: -----------------------------------------------------------------------------
:: Step 2: Locate MySQL Executable
:: -----------------------------------------------------------------------------
set "MYSQL_BIN="

if exist "C:\xampp\mysql\bin\mysql.exe" (
    set "MYSQL_BIN=C:\xampp\mysql\bin\mysql.exe"
    set "MYSQL_DIR=C:\xampp\mysql"
) else if exist "D:\xampp\mysql\bin\mysql.exe" (
    set "MYSQL_BIN=D:\xampp\mysql\bin\mysql.exe"
    set "MYSQL_DIR=D:\xampp\mysql"
) else (
    where mysql.exe >nul 2>&1
    if !errorlevel! equ 0 (
        set "MYSQL_BIN=mysql.exe"
    )
)

if "%MYSQL_BIN%"=="" (
    echo [ERROR] MySQL client executable could not be found.
    echo Please verify that XAMPP or MySQL 8.0 is installed on C: or D: drive,
    echo or ensure mysql.exe is in your system PATH.
    echo.
    pause
    exit /b 1
)

echo [OK] Using MySQL client: %MYSQL_BIN%
echo.

:: -----------------------------------------------------------------------------
:: Step 3: Build Base Command and Verify Connectivity
:: -----------------------------------------------------------------------------
if not "!DB_PASS!"=="" (
    set MYSQL_EXEC="%MYSQL_BIN%" -h !DB_HOST! -P !DB_PORT! -u !DB_USER! -p!DB_PASS!
) else (
    set MYSQL_EXEC="%MYSQL_BIN%" -h !DB_HOST! -P !DB_PORT! -u !DB_USER!
)

echo [INFO] Verifying MySQL connectivity on !DB_HOST!:!DB_PORT!...
!MYSQL_EXEC! -e "SELECT 1;" >nul 2>&1
if !errorlevel! neq 0 (
    echo [WARNING] MySQL server is not currently responding on !DB_HOST!:!DB_PORT!.
    if defined MYSQL_DIR (
        if exist "%MYSQL_DIR%\bin\mysqld.exe" (
            echo [INFO] Attempting to start MySQL server from %MYSQL_DIR%...
            start "" "%MYSQL_DIR%\bin\mysqld.exe" --defaults-file="%MYSQL_DIR%\bin\my.ini" --standalone
            ping 127.0.0.1 -n 4 >nul
        )
    )
    !MYSQL_EXEC! -e "SELECT 1;" >nul 2>&1
    if !errorlevel! neq 0 (
        echo [ERROR] Could not establish connection to MySQL server.
        echo Please ensure MySQL is started in XAMPP Control Panel and check credentials in .env.
        echo.
        pause
        exit /b 1
    )
)

echo [OK] Successfully connected to MySQL server.
echo.

:: -----------------------------------------------------------------------------
:: Step 4: Execute Database Scripts in Strict Topological Sequence
:: -----------------------------------------------------------------------------
echo [1/7] Creating schema and core relational tables (schema.sql)...
!MYSQL_EXEC! -e "source %FORWARD_SLASH_DIR%database/schema.sql"
if !errorlevel! neq 0 (
    echo [ERROR] Failed to execute database/schema.sql
    pause
    exit /b 1
)

echo [2/7] Creating query-driven performance indexes (indexes.sql)...
!MYSQL_EXEC! -e "source %FORWARD_SLASH_DIR%database/indexes.sql"
if !errorlevel! neq 0 (
    echo [ERROR] Failed to execute database/indexes.sql
    pause
    exit /b 1
)

echo [3/7] Creating reporting and analytical views (views.sql)...
!MYSQL_EXEC! -e "source %FORWARD_SLASH_DIR%database/views.sql"
if !errorlevel! neq 0 (
    echo [ERROR] Failed to execute database/views.sql
    pause
    exit /b 1
)

echo [4/7] Installing operational and audit triggers (triggers.sql)...
!MYSQL_EXEC! -e "source %FORWARD_SLASH_DIR%database/triggers.sql"
if !errorlevel! neq 0 (
    echo [ERROR] Failed to execute database/triggers.sql
    pause
    exit /b 1
)

echo [5/7] Deploying transactional stored procedures (procedures.sql)...
!MYSQL_EXEC! -e "source %FORWARD_SLASH_DIR%database/procedures.sql"
if !errorlevel! neq 0 (
    echo [ERROR] Failed to execute database/procedures.sql
    pause
    exit /b 1
)

echo [6/7] Configuring RBAC roles and user privileges (security.sql)...
!MYSQL_EXEC! -e "source %FORWARD_SLASH_DIR%database/security.sql"
if !errorlevel! neq 0 (
    echo [ERROR] Failed to execute database/security.sql
    pause
    exit /b 1
)

echo [7/7] Populating referentially valid seed dataset (seed.sql)...
!MYSQL_EXEC! -e "source %FORWARD_SLASH_DIR%database/seed.sql"
if !errorlevel! neq 0 (
    echo [ERROR] Failed to execute database/seed.sql
    pause
    exit /b 1
)

echo.
echo ===============================================================================
echo [SUCCESS] TransitMatrix Database successfully initialized and seeded.
echo ===============================================================================
echo.

:: -----------------------------------------------------------------------------
:: Step 5: Verification - Display Row Counts Across All Tables
:: -----------------------------------------------------------------------------
echo [INFO] Live Database Table Row Count Verification:
echo -------------------------------------------------------------------------------
!MYSQL_EXEC! -e "USE !DB_NAME!; SELECT 'users' AS table_name, COUNT(*) AS row_count FROM users UNION ALL SELECT 'passengers', COUNT(*) FROM passengers UNION ALL SELECT 'stations', COUNT(*) FROM stations UNION ALL SELECT 'routes', COUNT(*) FROM routes UNION ALL SELECT 'route_stops', COUNT(*) FROM route_stops UNION ALL SELECT 'services', COUNT(*) FROM services UNION ALL SELECT 'vehicles', COUNT(*) FROM vehicles UNION ALL SELECT 'seats', COUNT(*) FROM seats UNION ALL SELECT 'trips', COUNT(*) FROM trips UNION ALL SELECT 'trip_seat_inventory', COUNT(*) FROM trip_seat_inventory UNION ALL SELECT 'bookings', COUNT(*) FROM bookings UNION ALL SELECT 'tickets', COUNT(*) FROM tickets UNION ALL SELECT 'payments', COUNT(*) FROM payments UNION ALL SELECT 'cancellations', COUNT(*) FROM cancellations UNION ALL SELECT 'waitlists', COUNT(*) FROM waitlists UNION ALL SELECT 'delays', COUNT(*) FROM delays UNION ALL SELECT 'audit_logs', COUNT(*) FROM audit_logs UNION ALL SELECT 'demand_predictions', COUNT(*) FROM demand_predictions;"
echo.

:: -----------------------------------------------------------------------------
:: Step 6: Optional Demonstration of the 21 Advanced SQL Queries
:: -----------------------------------------------------------------------------
if "%~1"=="--auto" (
    set "RUN_QUERIES=N"
) else (
    set /p RUN_QUERIES="Do you want to run the 21 Advanced SQL Query demonstrations now? (Y/N): "
)

if /i "!RUN_QUERIES!"=="Y" (
    echo.
    echo ===============================================================================
    echo Running 21 Advanced SQL Demonstration Queries...
    echo ===============================================================================
    !MYSQL_EXEC! -e "source %FORWARD_SLASH_DIR%database/queries/all_queries_demonstration.sql"
    echo.
    echo [SUCCESS] All 21 demonstration queries completed.
)

echo.
if not "%~1"=="--auto" (
    echo Setup process finished. Press any key to exit.
    pause >nul
) else (
    echo [OK] Setup process finished successfully.
)

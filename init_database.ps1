# =============================================================================
# TransitMatrix: One-Click Database Initialization and Verification Script
# Platform: Windows PowerShell / PowerShell Core
# Storage Engine: MySQL 8.0+ / MariaDB 10.4+ on InnoDB
# =============================================================================

Write-Host "===============================================================================" -ForegroundColor Cyan
Write-Host "TransitMatrix: Intelligent Railway and Public Transit Management System" -ForegroundColor Cyan
Write-Host "One-Click Database Setup and Verification Utility" -ForegroundColor Cyan
Write-Host "===============================================================================" -ForegroundColor Cyan
Write-Host ""

# -----------------------------------------------------------------------------
# 1. Locate MySQL Executable
# -----------------------------------------------------------------------------
$mysqlPaths = @(
    "C:\xampp\mysql\bin\mysql.exe",
    "D:\xampp\mysql\bin\mysql.exe"
)

$mysqlBin = $null
foreach ($path in $mysqlPaths) {
    if (Test-Path $path) {
        $mysqlBin = $path
        break
    }
}

if (-not $mysqlBin) {
    $cmd = Get-Command mysql.exe -ErrorAction SilentlyContinue
    if ($cmd) {
        $mysqlBin = $cmd.Source
    }
}

if (-not $mysqlBin) {
    Write-Host "[ERROR] Could not locate mysql.exe. Ensure XAMPP or MySQL is installed." -ForegroundColor Red
    pause
    exit 1
}

Write-Host "[OK] Using MySQL client: $mysqlBin" -ForegroundColor Green

# -----------------------------------------------------------------------------
# 2. Check Connection
# -----------------------------------------------------------------------------
Write-Host "[INFO] Verifying connection to MySQL on localhost:3306..." -ForegroundColor Yellow

try {
    & $mysqlBin -u root -e "SELECT 1;" 2>$null | Out-Null
    if ($LASTEXITCODE -ne 0) {
        throw "Connection failed"
    }
} catch {
    Write-Host "[WARNING] MySQL is not responding. Checking for XAMPP mysqld..." -ForegroundColor Yellow
    $mysqldPath = (Split-Path (Split-Path $mysqlBin)) + "\mysql\bin\mysqld.exe"
    $myIniPath = (Split-Path (Split-Path $mysqlBin)) + "\mysql\bin\my.ini"
    
    if (Test-Path $mysqldPath) {
        Write-Host "[INFO] Starting MySQL daemon: $mysqldPath" -ForegroundColor Cyan
        Start-Process -FilePath $mysqldPath -ArgumentList "--defaults-file=$myIniPath", "--standalone"
        Start-Sleep -Seconds 4
    }
    
    & $mysqlBin -u root -e "SELECT 1;" 2>$null | Out-Null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ERROR] Failed to connect to MySQL server. Please start it in XAMPP." -ForegroundColor Red
        pause
        exit 1
    }
}

Write-Host "[OK] Connected to MySQL successfully." -ForegroundColor Green
Write-Host ""

# -----------------------------------------------------------------------------
# 3. Path Normalization
# -----------------------------------------------------------------------------
$scriptRoot = $PSScriptRoot
$normalizedRoot = $scriptRoot.Replace("\", "/")

# -----------------------------------------------------------------------------
# 4. Sequenced Execution of Scripts
# -----------------------------------------------------------------------------
$scripts = @(
    @{ Name = "Schema & Core Tables"; File = "$normalizedRoot/database/schema.sql" },
    @{ Name = "Query-Driven Indexes"; File = "$normalizedRoot/database/indexes.sql" },
    @{ Name = "Reporting Views"; File = "$normalizedRoot/database/views.sql" },
    @{ Name = "Operational & Audit Triggers"; File = "$normalizedRoot/database/triggers.sql" },
    @{ Name = "Stored Procedures"; File = "$normalizedRoot/database/procedures.sql" },
    @{ Name = "Security Roles & Users"; File = "$normalizedRoot/database/security.sql" },
    @{ Name = "Sample Seed Dataset"; File = "$normalizedRoot/database/seed.sql" }
)

$step = 1
foreach ($s in $scripts) {
    Write-Host "[$step/7] Executing $($s.Name)..." -ForegroundColor Cyan
    & $mysqlBin -u root -e "source $($s.File)"
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ERROR] Failed executing $($s.File)" -ForegroundColor Red
        pause
        exit 1
    }
    $step++
}

Write-Host ""
Write-Host "===============================================================================" -ForegroundColor Green
Write-Host "[SUCCESS] TransitMatrix database successfully initialized and seeded." -ForegroundColor Green
Write-Host "===============================================================================" -ForegroundColor Green
Write-Host ""

# -----------------------------------------------------------------------------
# 5. Row Count Verification
# -----------------------------------------------------------------------------
Write-Host "[INFO] Table Row Counts Verification:" -ForegroundColor Yellow
$verifySql = "USE transitmatrix; SELECT 'users' AS table_name, COUNT(*) AS row_count FROM users UNION ALL SELECT 'passengers', COUNT(*) FROM passengers UNION ALL SELECT 'stations', COUNT(*) FROM stations UNION ALL SELECT 'routes', COUNT(*) FROM routes UNION ALL SELECT 'route_stops', COUNT(*) FROM route_stops UNION ALL SELECT 'services', COUNT(*) FROM services UNION ALL SELECT 'vehicles', COUNT(*) FROM vehicles UNION ALL SELECT 'seats', COUNT(*) FROM seats UNION ALL SELECT 'trips', COUNT(*) FROM trips UNION ALL SELECT 'trip_seat_inventory', COUNT(*) FROM trip_seat_inventory UNION ALL SELECT 'bookings', COUNT(*) FROM bookings UNION ALL SELECT 'tickets', COUNT(*) FROM tickets UNION ALL SELECT 'payments', COUNT(*) FROM payments UNION ALL SELECT 'cancellations', COUNT(*) FROM cancellations UNION ALL SELECT 'waitlists', COUNT(*) FROM waitlists UNION ALL SELECT 'delays', COUNT(*) FROM delays UNION ALL SELECT 'audit_logs', COUNT(*) FROM audit_logs UNION ALL SELECT 'demand_predictions', COUNT(*) FROM demand_predictions;"

& $mysqlBin -u root -e $verifySql
Write-Host ""

# -----------------------------------------------------------------------------
# 6. Advanced SQL Queries Prompt
# -----------------------------------------------------------------------------
$runDemo = Read-Host "Do you want to run the 21 Advanced SQL Query demonstrations now? (Y/N)"
if ($runDemo -eq "Y" -or $runDemo -eq "y") {
    Write-Host ""
    Write-Host "Running 21 Advanced SQL Query demonstrations..." -ForegroundColor Cyan
    & $mysqlBin -u root -e "source $normalizedRoot/database/queries/all_queries_demonstration.sql"
    Write-Host "[SUCCESS] All 21 demonstration queries completed." -ForegroundColor Green
}

Write-Host ""
Write-Host "Database initialization finished. Press any key to exit." -ForegroundColor Green
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")


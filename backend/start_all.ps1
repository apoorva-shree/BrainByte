

Write-Host "╔═══════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║   🚀 PERISHABLE FOOD OPTIMIZER - FULL STACK LAUNCHER 🚀  ║" -ForegroundColor Cyan
Write-Host "╚═══════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""


Write-Host "🔍 Checking MongoDB..." -ForegroundColor Yellow
$mongoCheck = Get-Command mongod -ErrorAction SilentlyContinue
if (-not $mongoCheck) {
    Write-Host " MongoDB not found. Please install MongoDB first." -ForegroundColor Red
    Write-Host "   Download from: https://www.mongodb.com/try/download/community" -ForegroundColor Gray
    exit 1
}


Write-Host "🔍 Checking Python..." -ForegroundColor Yellow
$pythonCheck = Get-Command python -ErrorAction SilentlyContinue
if (-not $pythonCheck) {
    Write-Host "Python not found. Please install Python 3.8+ first." -ForegroundColor Red
    exit 1
}


Write-Host "🔍 Checking Node.js..." -ForegroundColor Yellow
$nodeCheck = Get-Command node -ErrorAction SilentlyContinue
if (-not $nodeCheck) {
    Write-Host "Node.js not found. Skipping Node.js backend." -ForegroundColor Yellow
} else {
    Write-Host "Node.js found" -ForegroundColor Green
}

Write-Host ""
Write-Host "Installing Python dependencies..." -ForegroundColor Cyan
python -m pip install -r requirements.txt --quiet

Write-Host ""
Write-Host " Starting all services..." -ForegroundColor Green
Write-Host ""


Write-Host "1️Starting MongoDB" -ForegroundColor Magenta
Start-Process -FilePath "mongod" -ArgumentList "--dbpath", ".\data\db" -WindowStyle Minimized
Write-Host "MongoDB started (port 27017)" -ForegroundColor Green
Start-Sleep -Seconds 2


if ($nodeCheck) {
    Write-Host " Starting Node.js Backend..." -ForegroundColor Magenta
    Start-Process -FilePath "node" -ArgumentList "server.js" -WindowStyle Normal
    Write-Host "   Node.js Backend started (port 3000)" -ForegroundColor Green
    Start-Sleep -Seconds 2
}

Write-Host " Starting FastAPI Backend..." -ForegroundColor Magenta
Start-Process -FilePath "python" -ArgumentList "-m", "uvicorn", "main:app", "--reload", "--port", "8000" -WindowStyle Normal
Write-Host "   FastAPI Backend started (port 8000)" -ForegroundColor Green
Start-Sleep -Seconds 3


Write-Host ""
Write-Host "╔═══════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║                    ALL SERVICES RUNNING                 ║" -ForegroundColor Green
Write-Host "╚═══════════════════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""
Write-Host "Frontend:         http://localhost:3000" -ForegroundColor Cyan
Write-Host " Node.js API:      http://localhost:3000/api" -ForegroundColor Cyan
Write-Host "FastAPI:          http://localhost:8000" -ForegroundColor Cyan
Write-Host "PI Docs:         http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "MongoDB:          mongodb://localhost:27017" -ForegroundColor Cyan
Write-Host ""
Write-Host " Press Ctrl+C in each window to stop individual services" -ForegroundColor Yellow
Write-Host ""

# Trading Platform API - Quick Setup Script for Windows PowerShell

param(
    [switch]$SkipVenv = $false,
    [switch]$SkipDependencies = $false
)

Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "Trading Platform API - Setup Script for Windows" -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan

# Check if Python is installed
Write-Host "`n[1/5] Checking Python installation..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
} else {
    Write-Host "❌ Python not found. Please install Python 3.8+" -ForegroundColor Red
    exit 1
}

# Create virtual environment
if (-not $SkipVenv) {
    Write-Host "`n[2/5] Creating virtual environment..." -ForegroundColor Yellow
    if (Test-Path "venv") {
        Write-Host "⚠️  Virtual environment already exists. Skipping..." -ForegroundColor Yellow
    } else {
        python -m venv venv
        Write-Host "✅ Virtual environment created" -ForegroundColor Green
    }
    
    # Activate virtual environment
    Write-Host "Activating virtual environment..." -ForegroundColor Yellow
    & ".\venv\Scripts\Activate.ps1"
    Write-Host "✅ Virtual environment activated" -ForegroundColor Green
} else {
    Write-Host "[2/5] Skipping virtual environment creation" -ForegroundColor Yellow
}

# Install dependencies
if (-not $SkipDependencies) {
    Write-Host "`n[3/5] Installing Python dependencies..." -ForegroundColor Yellow
    pip install --upgrade pip -q
    pip install -r requirements.txt -q
    Write-Host "✅ Dependencies installed" -ForegroundColor Green
} else {
    Write-Host "[3/5] Skipping dependency installation" -ForegroundColor Yellow
}

# Create/verify .env file
Write-Host "`n[4/5] Checking environment configuration..." -ForegroundColor Yellow
if (Test-Path ".env") {
    Write-Host "✅ .env file exists" -ForegroundColor Green
    Write-Host "   Note: Update .env with your API credentials" -ForegroundColor Cyan
} else {
    Write-Host "⚠️  .env file not found. Please copy from template and add credentials" -ForegroundColor Yellow
}

# Verify system
Write-Host "`n[5/5] Verifying system configuration..." -ForegroundColor Yellow
Write-Host "Running verification script..." -ForegroundColor Cyan
python verify_system.py

Write-Host "`n======================================================================" -ForegroundColor Cyan
Write-Host "✅ Setup Complete!" -ForegroundColor Green
Write-Host "======================================================================" -ForegroundColor Cyan

Write-Host "`n📝 Next Steps:" -ForegroundColor Yellow
Write-Host "1. Edit .env file with your API credentials" -ForegroundColor Cyan
Write-Host "   - OpenAI: https://platform.openai.com/api-keys" -ForegroundColor Gray
Write-Host "   - GitHub: https://github.com/settings/tokens" -ForegroundColor Gray
Write-Host "   - Azure: https://portal.azure.com" -ForegroundColor Gray
Write-Host "   - Coinbase: https://coinbase.com/settings/api" -ForegroundColor Gray

Write-Host "`n2. Run the FastAPI server:" -ForegroundColor Cyan
Write-Host "   python -m uvicorn main:app --reload" -ForegroundColor Gray

Write-Host "`n3. Open API documentation:" -ForegroundColor Cyan
Write-Host "   http://localhost:8000/docs" -ForegroundColor Gray

Write-Host "`n4. Test endpoints:" -ForegroundColor Cyan
Write-Host "   GET http://localhost:8000/health" -ForegroundColor Gray
Write-Host "   GET http://localhost:8000/status" -ForegroundColor Gray

Write-Host "`n💡 Tips:" -ForegroundColor Yellow
Write-Host "- Use 'python verify_system.py' to test API connections" -ForegroundColor Gray
Write-Host "- Set 'COINBASE_SANDBOX_MODE=true' to use sandbox environment" -ForegroundColor Gray
Write-Host "- Keep .env file secure and never commit it to git" -ForegroundColor Gray

Write-Host "`n📚 Documentation:" -ForegroundColor Yellow
Write-Host "- README.md - Complete guide" -ForegroundColor Gray
Write-Host "- http://localhost:8000/docs - Interactive API docs" -ForegroundColor Gray
Write-Host "- http://localhost:8000/redoc - Alternative API docs" -ForegroundColor Gray

Write-Host "`n======================================================================`n" -ForegroundColor Cyan

# CoBM Cloud Agent - GitHub Init Script
# Run: powershell -ExecutionPolicy Bypass -File init_github.ps1

Write-Host "========================================"
Write-Host "CoBM Cloud Agent GitHub Init"
Write-Host "========================================"
Write-Host ""

# Check Git
Write-Host "[1/6] Checking Git..." -NoNewline
if (Get-Command git -ErrorAction SilentlyContinue) {
    Write-Host " OK" -ForegroundColor Green
} else {
    Write-Host " FAIL - Please install Git first" -ForegroundColor Red
    exit 1
}

# Check gh CLI
Write-Host "[2/6] Checking GitHub CLI..." -NoNewline
if (Get-Command gh -ErrorAction SilentlyContinue) {
    Write-Host " OK" -ForegroundColor Green
    $ghInstalled = $true
} else {
    Write-Host " Not installed (skip auto repo creation)" -ForegroundColor Yellow
    $ghInstalled = $false
}

# Ask GitHub username
Write-Host ""
Write-Host "[3/6] GitHub Settings" -ForegroundColor Yellow
$githubUser = Read-Host "GitHub username (press Enter to skip)"
if (-not $githubUser) {
    $githubUser = "YOUR_USERNAME"
}

# Repo name
$repoName = "cobm-agent"
Write-Host "Repository: $repoName"
$workDir = "D:\claude mini max 2.7\.claude\cloud_agent"

# Initialize Git
Write-Host ""
Write-Host "[4/6] Initializing Git repo..." -NoNewline
Set-Location $workDir
git init
Write-Host " Done" -ForegroundColor Green

# Create initial commit
Write-Host "[5/6] Creating initial commit..." -NoNewline
git add .
git commit -m "Initial: CoBM Cloud Agent

Features:
- Data Crawler
- AI Analysis
- PPT Report Generator
- Auto Email

Contact: scott365888@gmail.com | WeChat: pts9800
"
Write-Host " Done" -ForegroundColor Green

# Create GitHub repo
Write-Host ""
Write-Host "[6/6] GitHub Repository" -ForegroundColor Yellow

if ($ghInstalled) {
    Write-Host "Checking GitHub login..." -NoNewline
    $authCheck = gh auth status 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host ""
        Write-Host "Please run: gh auth login"
    } else {
        Write-Host " Logged in" -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "========================================"
Write-Host "Init Complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Connect remote:"
Write-Host "   git remote add origin https://github.com/$githubUser/$repoName.git"
Write-Host "   git branch -M main"
Write-Host "   git push -u origin main"
Write-Host ""
Write-Host "2. Add Secrets in GitHub Settings > Secrets:"
Write-Host "   - CLAUDE_API_KEY"
Write-Host "   - SMTP_AUTH_CODE"
Write-Host "   - GMAIL_USER = scott365888@gmail.com"
Write-Host ""
Write-Host "3. Enable workflow in Actions page"
Write-Host ""
Write-Host "========================================"

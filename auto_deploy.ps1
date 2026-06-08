# ============================================================
#  CareSync Auto-Deployer - One-Click GitHub + Render Deploy
#  Run this script once to deploy your app to the internet!
# ============================================================

param(
    [string]$GitHubUsername = "",
    [string]$GitHubToken = "",
    [string]$RepoName = "caresync-hospital",
    [switch]$LocalOnly
)

$ErrorActionPreference = "Continue"
$ProjectDir = Split-Path -Parent $MyInvocation.MyCommand.Path

function Write-Step { param($n, $msg) Write-Host "`n[$n] $msg" -ForegroundColor Cyan }
function Write-OK   { param($msg) Write-Host "  [OK] $msg" -ForegroundColor Green }
function Write-Warn { param($msg) Write-Host "  [!!] $msg" -ForegroundColor Yellow }
function Write-Fail { param($msg) Write-Host "  [XX] $msg" -ForegroundColor Red }
function Write-Info { param($msg) Write-Host "  --> $msg" -ForegroundColor White }

Write-Host ""
Write-Host "============================================================" -ForegroundColor Magenta
Write-Host "   CARESYNC HOSPITAL - AUTOMATED DEPLOYMENT SCRIPT         " -ForegroundColor Magenta
Write-Host "============================================================" -ForegroundColor Magenta
Write-Host ""

# -------------------------------------------------------
# STEP 0: LocalOnly mode - just run on local network
# -------------------------------------------------------
if ($LocalOnly) {
    Write-Step "0" "Starting CareSync on Local Network (LAN Mode)"
    & "$ProjectDir\.venv\Scripts\python.exe" "$ProjectDir\run_local_network.py"
    exit 0
}

# -------------------------------------------------------
# STEP 1: Check / Install Git
# -------------------------------------------------------
Write-Step "1" "Checking for Git installation..."

$gitPath = Get-Command git -ErrorAction SilentlyContinue
if ($gitPath) {
    Write-OK "Git is already installed: $(git --version)"
} else {
    Write-Warn "Git not found. Installing via winget..."
    try {
        winget install --id Git.Git -e --source winget --accept-package-agreements --accept-source-agreements
        # Refresh PATH
        $env:PATH = [System.Environment]::GetEnvironmentVariable("PATH","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("PATH","User")
        $gitPath = Get-Command git -ErrorAction SilentlyContinue
        if ($gitPath) {
            Write-OK "Git installed successfully!"
        } else {
            Write-Fail "Git installation failed. Please install manually from: https://git-scm.com/download/win"
            Write-Warn "After installing Git, restart PowerShell and run this script again."
            pause
            exit 1
        }
    } catch {
        Write-Fail "Could not auto-install Git. Please install from: https://git-scm.com/download/win"
        pause
        exit 1
    }
}

# -------------------------------------------------------
# STEP 2: Initialize Git Repository
# -------------------------------------------------------
Write-Step "2" "Setting up Git repository..."

Set-Location $ProjectDir

if (Test-Path ".git") {
    Write-OK "Git repository already initialized."
} else {
    git init
    Write-OK "Git repository initialized."
}

# Configure git if not set
$gitUser = git config user.email 2>$null
if (-not $gitUser) {
    if ($GitHubUsername) {
        git config user.email "$GitHubUsername@users.noreply.github.com"
        git config user.name $GitHubUsername
        Write-OK "Git user configured."
    } else {
        Write-Warn "Git user not configured. Enter your name and email:"
        $uname = Read-Host "  Your Name (e.g. John Doe)"
        $uemail = Read-Host "  Your Email (same as GitHub)"
        git config user.name $uname
        git config user.email $uemail
        Write-OK "Git user configured."
    }
}

# -------------------------------------------------------
# STEP 3: Stage & Commit Files
# -------------------------------------------------------
Write-Step "3" "Committing project files..."

git add .
$status = git status --porcelain
if ($status) {
    git commit -m "Deploy: CareSync Hospital Management System - Auto Deploy $(Get-Date -Format 'yyyy-MM-dd HH:mm')"
    Write-OK "Files committed."
} else {
    Write-OK "Nothing new to commit - repository is up to date."
}

# -------------------------------------------------------
# STEP 4: GitHub Setup
# -------------------------------------------------------
Write-Step "4" "Setting up GitHub repository..."

if (-not $GitHubUsername) {
    Write-Info "You need a FREE GitHub account to deploy online."
    Write-Info "Sign up at: https://github.com (takes 2 minutes)"
    Write-Host ""
    $GitHubUsername = Read-Host "  Enter your GitHub username"
}

# Check if remote already exists
$remoteExists = git remote get-url origin 2>$null
if ($remoteExists) {
    Write-OK "Remote 'origin' already set: $remoteExists"
} else {
    # Try to create GitHub repo via API
    if (-not $GitHubToken) {
        Write-Host ""
        Write-Info "To auto-create the GitHub repo, we need a Personal Access Token."
        Write-Info "Create one at: https://github.com/settings/tokens/new"
        Write-Info "  - Give it 'repo' permissions"
        Write-Info "  - Copy the token (starts with ghp_...)"
        Write-Host ""
        $GitHubToken = Read-Host "  Paste your GitHub Token (or press Enter to skip auto-create)"
    }

    if ($GitHubToken) {
        Write-Info "Creating GitHub repository '$RepoName'..."
        $headers = @{
            "Authorization" = "token $GitHubToken"
            "Accept"        = "application/vnd.github.v3+json"
            "User-Agent"    = "CareSync-AutoDeploy"
        }
        $body = @{
            name        = $RepoName
            description = "CareSync Hospital Management System - Flask Web App"
            private     = $false
        } | ConvertTo-Json

        try {
            $response = Invoke-RestMethod -Uri "https://api.github.com/user/repos" -Method POST -Headers $headers -Body $body -ContentType "application/json"
            Write-OK "GitHub repository created: $($response.html_url)"
            git remote add origin "https://$GitHubUsername`:$GitHubToken@github.com/$GitHubUsername/$RepoName.git"
        } catch {
            Write-Warn "Repository may already exist. Connecting to existing repo..."
            git remote add origin "https://$GitHubUsername`:$GitHubToken@github.com/$GitHubUsername/$RepoName.git"
        }
    } else {
        Write-Warn "Skipping auto-create. Please create repository manually:"
        Write-Info "1. Go to: https://github.com/new"
        Write-Info "2. Repository name: $RepoName"
        Write-Info "3. Leave it Public, click 'Create repository'"
        Write-Host ""
        $confirm = Read-Host "  Press Enter after creating the repo on GitHub"
        git remote add origin "https://github.com/$GitHubUsername/$RepoName.git"
    }
}

# -------------------------------------------------------
# STEP 5: Push to GitHub
# -------------------------------------------------------
Write-Step "5" "Pushing code to GitHub..."

try {
    git branch -M main
    git push -u origin main --force
    Write-OK "Code pushed to GitHub successfully!"
    Write-Info "View your repo at: https://github.com/$GitHubUsername/$RepoName"
} catch {
    Write-Fail "Push failed. This may be due to authentication."
    Write-Info "Try pushing manually:"
    Write-Info "  git push -u origin main"
    Write-Warn "If asked for password, use your GitHub token as the password."
}

# -------------------------------------------------------
# STEP 6: Render.com Deployment Instructions
# -------------------------------------------------------
Write-Step "6" "Deploying to Render.com (FREE hosting)..."

Write-Host ""
Write-Host "  ============================================" -ForegroundColor Yellow
Write-Host "   FINAL STEP - Deploy on Render.com (FREE)" -ForegroundColor Yellow
Write-Host "  ============================================" -ForegroundColor Yellow
Write-Host ""
Write-Host "  Your code is on GitHub. Now deploy it:" -ForegroundColor White
Write-Host ""
Write-Host "  1. Go to: https://render.com" -ForegroundColor Cyan
Write-Host "     (Sign up FREE - no credit card needed)" -ForegroundColor Gray
Write-Host ""
Write-Host "  2. Click 'New +' -> 'Web Service'" -ForegroundColor Cyan
Write-Host ""
Write-Host "  3. Connect GitHub -> Select '$RepoName'" -ForegroundColor Cyan
Write-Host ""
Write-Host "  4. Settings (auto-filled from render.yaml):" -ForegroundColor Cyan
Write-Host "     - Build Command: pip install -r requirements.txt" -ForegroundColor Gray
Write-Host "     - Start Command: gunicorn app:app" -ForegroundColor Gray
Write-Host ""
Write-Host "  5. Click 'Create Web Service'" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Your app will be LIVE at:" -ForegroundColor Green
Write-Host "  https://$RepoName.onrender.com" -ForegroundColor Green -BackgroundColor DarkGreen
Write-Host ""

# Open browser to Render
$openRender = Read-Host "  Open Render.com now? (y/n)"
if ($openRender -eq "y" -or $openRender -eq "Y") {
    Start-Process "https://render.com/deploy?repo=https://github.com/$GitHubUsername/$RepoName"
    Write-OK "Opened Render.com in browser!"
}

# -------------------------------------------------------
# SUMMARY
# -------------------------------------------------------
Write-Host ""
Write-Host "============================================================" -ForegroundColor Green
Write-Host "   DEPLOYMENT COMPLETE!" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green
Write-Host ""
Write-Host "  GitHub Repo : https://github.com/$GitHubUsername/$RepoName" -ForegroundColor Cyan
Write-Host "  Live URL    : https://$RepoName.onrender.com" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Login Credentials:" -ForegroundColor White
Write-Host "  Admin    -> admin / admin123" -ForegroundColor Gray
Write-Host "  Doctor   -> sarah.jenkins@hospital.com / doctor123" -ForegroundColor Gray
Write-Host "  Patient  -> john.doe@email.com / patient123" -ForegroundColor Gray
Write-Host ""
Write-Host "  To update your live site in future, just run:" -ForegroundColor Yellow
Write-Host "  git add . && git commit -m 'update' && git push" -ForegroundColor Yellow
Write-Host ""
pause

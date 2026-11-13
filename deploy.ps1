# =============================================================================
# Automated Azure Deployment Script (PowerShell)
# Tomato Price Prediction Daily ETL Pipeline & Web Dashboard
# =============================================================================

[CmdletBinding()]
param (
    [string]$ResourceGroupName = "rg-tomato-prediction-prod",
    [string]$Location = "eastus2",
    [string]$NotificationEmail = "priya@iservce.onmicrosoft.com",
    [switch]$SkipTerraformApply,
    [switch]$LocalDockerOnly
)

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# -----------------------------------------------------------------------------
# Ensure Azure CLI and Terraform are available in PATH
# -----------------------------------------------------------------------------
$extraPaths = @(
    "$ScriptDir\bin",
    "C:\Program Files\Microsoft SDKs\Azure\CLI2\wbin",
    "C:\Program Files (x86)\Microsoft SDKs\Azure\CLI2\wbin"
)

foreach ($p in $extraPaths) {
    if ((Test-Path $p) -and ($env:PATH -notlike "*$p*")) {
        $env:PATH = "$p;" + $env:PATH
    }
}

Write-Host "=================================================================" -ForegroundColor Cyan
Write-Host "   AZURE TOMATO PRICE PREDICTION - AUTOMATED DEPLOYMENT          " -ForegroundColor Yellow
Write-Host "=================================================================" -ForegroundColor Cyan

# 1. Local Docker Run Check
if ($LocalDockerOnly) {
    Write-Host "`n[*] Starting Local Full Stack using Docker Compose..." -ForegroundColor Green
    docker-compose -f "$ScriptDir/docker-compose.yml" up --build -d
    Write-Host "`n[+] Local stack running!" -ForegroundColor Green
    Write-Host "    - Web Dashboard: http://localhost:3000" -ForegroundColor Cyan
    Write-Host "    - Prediction API Docs: http://localhost:8000/docs" -ForegroundColor Cyan
    exit 0
}

# 2. Azure CLI Verification
Write-Host "`n[Step 1/6] Checking Azure CLI Authentication..." -ForegroundColor Cyan

$azCmd = Get-Command az -ErrorAction SilentlyContinue
if (-not $azCmd) {
    Write-Host "[!] Azure CLI ('az') not found in PATH." -ForegroundColor Red
    Write-Host "    Please ensure Azure CLI is installed." -ForegroundColor Yellow
    exit 1
}

$accountJson = $null
try {
    $accountJson = & az account show --output json 2>$null
} catch {
    $accountJson = $null
}

if (-not $accountJson -or $LASTEXITCODE -ne 0) {
    Write-Host "[!] Azure CLI not logged in. Initiating Azure login in your browser..." -ForegroundColor Yellow
    & az login
    $accountJson = & az account show --output json
}

$account = $accountJson | ConvertFrom-Json
Write-Host "[+] Signed into Azure Subscription: $($account.name) ($($account.id))" -ForegroundColor Green
Write-Host "    Account User: $($account.user.name)" -ForegroundColor DarkGray

# 3. Terraform Verification & Infrastructure Provisioning
if (-not $SkipTerraformApply) {
    Write-Host "`n[Step 2/6] Provisioning Azure Cloud Services with Terraform..." -ForegroundColor Cyan
    
    $tfCmd = Get-Command terraform -ErrorAction SilentlyContinue
    if (-not $tfCmd) {
        Write-Host "[!] Terraform not found in PATH." -ForegroundColor Red
        exit 1
    }

    Set-Location -Path "$ScriptDir/terraform"
    
    Write-Host "--> Running terraform init..." -ForegroundColor DarkGray
    terraform init -input=false

    Write-Host "--> Running terraform validate..." -ForegroundColor DarkGray
    terraform validate

    Write-Host "--> Running terraform apply..." -ForegroundColor DarkGray
    terraform apply -auto-approve -var="notification_email=$NotificationEmail" -var="location=$Location"
    
    # Extract Outputs
    $acrServer = terraform output -raw container_registry_login_server
    $frontendUrl = terraform output -raw frontend_web_app_url
    $apiFqdn = terraform output -raw api_container_fqdn
    $storageAcc = terraform output -raw storage_account_name
    
    Set-Location -Path $ScriptDir
    Write-Host "[+] Azure Infrastructure Provisioned Successfully!" -ForegroundColor Green
} else {
    Write-Host "`n[*] Skipping Terraform apply as requested." -ForegroundColor Yellow
    Set-Location -Path "$ScriptDir/terraform"
    $acrServer = terraform output -raw container_registry_login_server
    $frontendUrl = terraform output -raw frontend_web_app_url
    $apiFqdn = terraform output -raw api_container_fqdn
    $storageAcc = terraform output -raw storage_account_name
    Set-Location -Path $ScriptDir
}

# 4. Azure Container Registry Login & Docker Build
Write-Host "`n[Step 3/6] Building and Pushing Docker Images to ACR ($acrServer)..." -ForegroundColor Cyan
$acrName = ($acrServer -replace '\.azurecr\.io$','')
az acr login --name $acrName

$apiImage = "$acrServer/tomato-prediction-api:latest"
$frontendImage = "$acrServer/tomato-prediction-frontend:latest"

Write-Host "--> Building Backend API Container..." -ForegroundColor DarkGray
docker build -t $apiImage -f "$ScriptDir/Dockerfile" "$ScriptDir"
docker push $apiImage

Write-Host "--> Building React Frontend Container..." -ForegroundColor DarkGray
docker build -t $frontendImage -f "$ScriptDir/Dockerfile.frontend" "$ScriptDir"
docker push $frontendImage

# 5. Upload Datasets & Trained Models to Azure Blob Storage
Write-Host "`n[Step 4/6] Synchronizing Training Datasets & Best Models to Blob Storage..." -ForegroundColor Cyan
az storage blob upload-batch `
    --account-name $storageAcc `
    --destination "raw-data" `
    --source "$ScriptDir/data/raw" `
    --auth-mode login `
    --overwrite

az storage blob upload-batch `
    --account-name $storageAcc `
    --destination "models" `
    --source "$ScriptDir/models" `
    --auth-mode login `
    --overwrite

# 6. Seed Initial Predictions & Send Notification Email
Write-Host "`n[Step 5/6] Triggering Initial Prediction ETL Run & Email Dispatch..." -ForegroundColor Cyan
python "$ScriptDir/ml_pipeline/predict.py"
python -c "from api.scheduler import run_daily_prediction_pipeline; run_daily_prediction_pipeline('$NotificationEmail')"

# 7. Final Verification
Write-Host "`n=================================================================" -ForegroundColor Green
Write-Host "   DEPLOYMENT & PIPELINE AUTOMATION COMPLETE!                    " -ForegroundColor Green
Write-Host "=================================================================" -ForegroundColor Green
Write-Host "- Frontend Web Dashboard : $frontendUrl" -ForegroundColor Cyan
Write-Host "- Backend API Docs       : $apiFqdn/docs" -ForegroundColor Cyan
Write-Host "- Azure Container Registry: $acrServer" -ForegroundColor Cyan
Write-Host "- Notification Recipient : $NotificationEmail" -ForegroundColor Cyan
Write-Host "- Automated Daily Cron   : Active at 06:00 IST every day" -ForegroundColor Cyan

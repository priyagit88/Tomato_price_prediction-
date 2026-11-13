#!/usr/bin/env bash
# =============================================================================
# Automated Azure Deployment Script (Bash)
# Tomato Price Prediction Daily ETL Pipeline & Web Dashboard
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOCATION="${LOCATION:-eastus2}"
NOTIFICATION_EMAIL="${NOTIFICATION_EMAIL:-priya@iservce.onmicrosoft.com}"
RESOURCE_GROUP="${RESOURCE_GROUP:-rg-tomato-prediction-prod}"

echo "================================================================="
echo "   🍅 AZURE TOMATO PRICE PREDICTION - AUTOMATED DEPLOYMENT       "
echo "================================================================="

# 1. Azure Authentication
echo -e "\n[Step 1/6] Verifying Azure CLI Authentication..."
if ! az account show >/dev/null 2>&1; then
    echo "[!] Not signed in. Initiating az login..."
    az login
fi
AZ_USER=$(az account show --query user.name -o tsv)
AZ_SUB=$(az account show --query name -o tsv)
echo "[✓] Authenticated to Azure as ${AZ_USER} on subscription '${AZ_SUB}'."

# 2. Terraform Provisioning
echo -e "\n[Step 2/6] Provisioning Azure Infrastructure with Terraform..."
cd "${SCRIPT_DIR}/terraform"
terraform init -input=false
terraform validate
terraform apply -auto-approve \
    -var="location=${LOCATION}" \
    -var="notification_email=${NOTIFICATION_EMAIL}"

ACR_SERVER=$(terraform output -raw container_registry_login_server)
FRONTEND_URL=$(terraform output -raw frontend_web_app_url)
API_FQDN=$(terraform output -raw api_container_fqdn)
STORAGE_ACC=$(terraform output -raw storage_account_name)
cd "${SCRIPT_DIR}"

# 3. Docker Build & Push to ACR
echo -e "\n[Step 3/6] Authenticating Docker to ACR (${ACR_SERVER})..."
ACR_NAME=$(echo "${ACR_SERVER}" | cut -d'.' -f1)
az acr login --name "${ACR_NAME}"

API_IMAGE="${ACR_SERVER}/tomato-prediction-api:latest"
FRONTEND_IMAGE="${ACR_SERVER}/tomato-prediction-frontend:latest"

echo "--> Building and pushing API container..."
docker build -t "${API_IMAGE}" -f "${SCRIPT_DIR}/Dockerfile" "${SCRIPT_DIR}"
docker push "${API_IMAGE}"

echo "--> Building and pushing Frontend container..."
docker build -t "${FRONTEND_IMAGE}" -f "${SCRIPT_DIR}/Dockerfile.frontend" "${SCRIPT_DIR}"
docker push "${FRONTEND_IMAGE}"

# 4. Storage Sync
echo -e "\n[Step 4/6] Uploading datasets and models to Azure Blob Storage..."
az storage blob upload-batch \
    --account-name "${STORAGE_ACC}" \
    --destination "raw-data" \
    --source "${SCRIPT_DIR}/data/raw" \
    --auth-mode login \
    --overwrite

az storage blob upload-batch \
    --account-name "${STORAGE_ACC}" \
    --destination "models" \
    --source "${SCRIPT_DIR}/models" \
    --auth-mode login \
    --overwrite

# 5. Pipeline Run & Notification
echo -e "\n[Step 5/6] Executing initial price prediction and email notification..."
python3 "${SCRIPT_DIR}/ml_pipeline/predict.py"
python3 -c "from api.scheduler import run_daily_prediction_pipeline; run_daily_prediction_pipeline('${NOTIFICATION_EMAIL}')"

# 6. Summary
echo -e "\n================================================================="
echo "   🎉 DEPLOYMENT & PIPELINE AUTOMATION COMPLETE!                 "
echo "================================================================="
echo "• Frontend Web Dashboard : ${FRONTEND_URL}"
echo "• Backend API Docs       : ${API_FQDN}/docs"
echo "• Container Registry     : ${ACR_SERVER}"
echo "• Notification Recipient : ${NOTIFICATION_EMAIL}"
echo "• Daily Forecast Cron    : Active at 06:00 IST every day"


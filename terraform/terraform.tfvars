# =============================================================================
# Terraform Variable Values (PLACEHOLDERS - replace before applying)
# Tomato Price Prediction Pipeline - Azure Infrastructure
#
# WARNING: Never commit real credentials to version control.
#          Use environment variables or a secrets manager for sensitive values.
# =============================================================================

# General
subscription_id     = "d6e4b3f9-95f1-4234-9b66-046747c96c0d"
location            = "eastus2"
resource_group_name = "rg-tomato-prediction"
project_name        = "tomato"
environment         = "production"

# Admin
admin_email          = "priya@iservce.onmicrosoft.com"
admin_object_id      = "51af22ec-181c-49d9-907b-dee1e0fe9275"
tenant_id            = "cafd2576-1a76-444b-8308-df607f8b743d"
notification_email   = "priya@iservce.onmicrosoft.com"

# SQL Database
sql_admin_username = "tomatoadmin"
sql_admin_password = "CHANGE_ME_StrongP@ssw0rd!"
sql_database_name  = "tomatodb"
sql_sku_name       = "S0"

# Container Registry
acr_sku = "Standard"

# Container Instances
aci_cpu          = 1
aci_memory       = 2
prediction_image = "mcr.microsoft.com/hello-world"

# App Service
app_service_sku = {
  tier = "Standard"
  size = "S1"
}

# Redis Cache
redis_sku      = "Basic"
redis_family   = "C"
redis_capacity = 0

# Azure ML
aml_sku = "Basic"

# Azure DevOps
azuredevops_org_url      = "https://dev.azure.com/YOUR_ORG"
azuredevops_pat          = "CHANGE_ME_your_pat_token"
azuredevops_project_name = "tomato-price-prediction"

# Front Door
frontdoor_sku = "Standard_AzureFrontDoor"

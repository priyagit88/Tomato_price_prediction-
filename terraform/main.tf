# =============================================================================
# Main Orchestration File
# Tomato Price Prediction Pipeline - Azure Infrastructure
# =============================================================================
#
# This file creates foundational resources. Domain-specific resources are in:
#   - resource_group.tf      → Resource Group
#   - storage.tf             → Blob Storage (raw data + ML artifacts)
#   - database.tf            → Azure SQL Server + Database
#   - container_registry.tf  → Azure Container Registry
#   - key_vault.tf           → Azure Key Vault
#   - monitoring.tf          → Log Analytics + Application Insights
#   - machine_learning.tf    → Azure ML Workspace + dependencies
#   - data_factory.tf        → Azure Data Factory
#   - container_instances.tf → ACI for prediction service
#   - app_service.tf         → App Service Plan + Web App (frontend)
#   - redis.tf               → Azure Redis Cache
#   - event_grid.tf          → Azure Event Grid
#   - notifications.tf       → Logic App for email notifications
#   - frontdoor.tf           → Azure Front Door CDN
#   - devops.tf              → Azure DevOps project
# =============================================================================

# Random suffix for globally unique resource names
resource "random_string" "suffix" {
  length  = 6
  special = false
  upper   = false
}

# Data source: current Azure client configuration
data "azurerm_client_config" "current" {}

# Local values used across all files
locals {
  suffix = random_string.suffix.result
  name_prefix = var.project_name

  common_tags = merge(var.common_tags, {
    project     = "tomato-price-prediction"
    environment = var.environment
  })
}

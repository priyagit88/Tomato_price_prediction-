# =============================================================================
# 7. Azure Machine Learning Workspace
#    ML experimentation, training, and model registry
#    Includes associated storage, app insights, and key vault
# =============================================================================

# Dedicated Key Vault for ML Workspace
resource "azurerm_key_vault" "ml" {
  name                       = "${local.name_prefix}-mlkv-${local.suffix}"
  resource_group_name        = azurerm_resource_group.main.name
  location                   = azurerm_resource_group.main.location
  tenant_id                  = var.tenant_id
  sku_name                   = "standard"
  soft_delete_retention_days = 7
  purge_protection_enabled   = false
  tags                       = local.common_tags
}

# Azure Machine Learning Workspace
resource "azurerm_machine_learning_workspace" "main" {
  name                          = "${local.name_prefix}-mlws-${local.suffix}"
  resource_group_name           = azurerm_resource_group.main.name
  location                      = azurerm_resource_group.main.location
  application_insights_id       = azurerm_application_insights.ml.id
  key_vault_id                  = azurerm_key_vault.ml.id
  storage_account_id            = "/subscriptions/d6e4b3f9-95f1-4234-9b66-046747c96c0d/resourceGroups/rg-tomato-prediction/providers/Microsoft.Storage/storageAccounts/tomatomlsaegk79m"
  container_registry_id         = azurerm_container_registry.main.id
  public_network_access_enabled = true

  identity {
    type = "SystemAssigned"
  }

  tags = local.common_tags
}

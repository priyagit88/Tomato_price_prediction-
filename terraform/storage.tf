# =============================================================================
# 4. Azure Blob Storage Account
#    Stores raw CSV data, ML model artifacts, and pipeline outputs
# =============================================================================

resource "azurerm_storage_account" "main" {
  name                     = "${local.name_prefix}store${local.suffix}"
  resource_group_name      = azurerm_resource_group.main.name
  location                 = azurerm_resource_group.main.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
  min_tls_version          = "TLS1_2"

  blob_properties {
    versioning_enabled = true
  }

  tags = local.common_tags
}

# Container for raw CSV data uploads
resource "azurerm_storage_container" "raw_data" {
  name                  = "raw-data"
  storage_account_name  = azurerm_storage_account.main.name
  container_access_type = "private"
}

# Container for trained ML model artifacts
resource "azurerm_storage_container" "models" {
  name                  = "ml-models"
  storage_account_name  = azurerm_storage_account.main.name
  container_access_type = "private"
}

# Container for prediction outputs
resource "azurerm_storage_container" "predictions" {
  name                  = "predictions"
  storage_account_name  = azurerm_storage_account.main.name
  container_access_type = "private"
}

# Dedicated storage account for Azure ML workspace
resource "azurerm_storage_account" "ml" {
  name                     = "${local.name_prefix}mlsa${local.suffix}"
  resource_group_name      = azurerm_resource_group.main.name
  location                 = azurerm_resource_group.main.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
  min_tls_version          = "TLS1_2"
  tags                     = local.common_tags
}

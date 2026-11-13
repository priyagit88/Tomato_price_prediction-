# =============================================================================
# 14. Azure Event Grid
#     Event-driven triggers for pipeline automation
# =============================================================================

# System topic for Blob Storage events (e.g., new CSV upload triggers pipeline)
resource "azurerm_eventgrid_system_topic" "blob_events" {
  name                   = "${local.name_prefix}-eg-blob-${local.suffix}"
  resource_group_name    = azurerm_resource_group.main.name
  location               = azurerm_resource_group.main.location
  source_arm_resource_id = azurerm_storage_account.main.id
  topic_type             = "Microsoft.Storage.StorageAccounts"
  tags                   = local.common_tags
}

# Custom topic for prediction pipeline events
resource "azurerm_eventgrid_topic" "predictions" {
  name                = "${local.name_prefix}-eg-predict-${local.suffix}"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  tags                = local.common_tags
}

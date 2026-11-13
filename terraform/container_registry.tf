# =============================================================================
# 2. Azure Container Registry (ACR)
#    Hosts Docker images for prediction service and pipeline components
# =============================================================================

resource "azurerm_container_registry" "main" {
  name                = "${local.name_prefix}acr${local.suffix}"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  sku                 = var.acr_sku
  admin_enabled       = true
  tags                = local.common_tags
}

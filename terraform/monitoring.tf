# =============================================================================
# 11 & 12. Azure Application Insights + Log Analytics Workspace
#    Monitoring and logging for the entire pipeline
# =============================================================================

# Log Analytics Workspace (12)
resource "azurerm_log_analytics_workspace" "main" {
  name                = "${local.name_prefix}-law-${local.suffix}"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  sku                 = "PerGB2018"
  retention_in_days   = 30
  tags                = local.common_tags
}

# Application Insights (11) - linked to Log Analytics
resource "azurerm_application_insights" "main" {
  name                = "${local.name_prefix}-appins-${local.suffix}"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  workspace_id        = azurerm_log_analytics_workspace.main.id
  application_type    = "web"
  tags                = local.common_tags
}

# Dedicated Application Insights for Azure ML Workspace
resource "azurerm_application_insights" "ml" {
  name                = "${local.name_prefix}-ml-appins-${local.suffix}"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  workspace_id        = azurerm_log_analytics_workspace.main.id
  application_type    = "web"
  tags                = local.common_tags
}

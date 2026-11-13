# =============================================================================
# 9. Azure App Service Plan + App Service
#    Hosts the frontend website for the tomato price prediction dashboard
# =============================================================================

resource "azurerm_service_plan" "main" {
  name                = "${local.name_prefix}-asp-${local.suffix}"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  os_type             = "Linux"
  sku_name            = var.app_service_sku.size

  tags = local.common_tags
}

resource "azurerm_linux_web_app" "frontend" {
  name                = "${local.name_prefix}-webapp-${local.suffix}"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  service_plan_id     = azurerm_service_plan.main.id
  https_only          = true

  site_config {
    always_on = true

    application_stack {
      python_version = "3.11"
    }
  }

  app_settings = {
    "ENVIRONMENT"                         = var.environment
    "PREDICTION_SERVICE_URL"              = "http://${azurerm_container_group.prediction_service.fqdn}:8000"
    "APPINSIGHTS_INSTRUMENTATIONKEY"      = azurerm_application_insights.main.instrumentation_key
    "APPLICATIONINSIGHTS_CONNECTION_STRING" = azurerm_application_insights.main.connection_string
    "REDIS_HOST"                          = azurerm_redis_cache.main.hostname
    "REDIS_PORT"                          = tostring(azurerm_redis_cache.main.ssl_port)
    "REDIS_KEY"                           = azurerm_redis_cache.main.primary_access_key
    "SQL_SERVER"                          = azurerm_mssql_server.main.fully_qualified_domain_name
    "SQL_DATABASE"                        = azurerm_mssql_database.main.name
  }

  identity {
    type = "SystemAssigned"
  }

  tags = local.common_tags
}

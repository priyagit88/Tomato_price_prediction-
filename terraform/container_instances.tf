# =============================================================================
# 8. Azure Container Instances (ACI)
#    Runs the tomato price prediction service Docker container
# =============================================================================

resource "azurerm_container_group" "prediction_service" {
  name                = "${local.name_prefix}-aci-${local.suffix}"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  os_type             = "Linux"
  ip_address_type     = "Public"
  dns_name_label      = "${local.name_prefix}-predict-${local.suffix}"
  restart_policy      = "Always"

  image_registry_credential {
    server   = azurerm_container_registry.main.login_server
    username = azurerm_container_registry.main.admin_username
    password = azurerm_container_registry.main.admin_password
  }

  container {
    name   = "prediction-service"
    image  = var.prediction_image
    cpu    = var.aci_cpu
    memory = var.aci_memory

    ports {
      port     = 8000
      protocol = "TCP"
    }

    environment_variables = {
      "ENVIRONMENT"          = var.environment
      "REDIS_HOST"           = azurerm_redis_cache.main.hostname
      "REDIS_PORT"           = tostring(azurerm_redis_cache.main.ssl_port)
      "APPINSIGHTS_INSTRUMENTATIONKEY" = azurerm_application_insights.main.instrumentation_key
    }

    secure_environment_variables = {
      "SQL_CONNECTION_STRING"     = "Server=tcp:${azurerm_mssql_server.main.fully_qualified_domain_name},1433;Initial Catalog=${azurerm_mssql_database.main.name};User ID=${var.sql_admin_username};Password=${var.sql_admin_password};Encrypt=True;"
      "STORAGE_CONNECTION_STRING" = azurerm_storage_account.main.primary_connection_string
      "REDIS_KEY"                 = azurerm_redis_cache.main.primary_access_key
    }
  }

  tags = local.common_tags
}

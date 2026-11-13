# =============================================================================
# Azure Container Instances (ACI)
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
    image  = "${azurerm_container_registry.main.login_server}/tomato-prediction-api:latest"
    cpu    = var.aci_cpu
    memory = var.aci_memory

    ports {
      port     = 8000
      protocol = "TCP"
    }

    environment_variables = {
      "ENVIRONMENT"                           = var.environment
      "APPINSIGHTS_INSTRUMENTATIONKEY"        = azurerm_application_insights.main.instrumentation_key
      "APPLICATIONINSIGHTS_CONNECTION_STRING" = azurerm_application_insights.main.connection_string
    }

    secure_environment_variables = {
      "STORAGE_ACCOUNT_NAME" = "tomatostoreegk79m"
    }
  }

  tags = local.common_tags
}

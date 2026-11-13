# =============================================================================
# Outputs for Azure Tomato Price Prediction Infrastructure
# =============================================================================

output "resource_group_name" {
  description = "Name of the provisioned Azure Resource Group"
  value       = azurerm_resource_group.rg.name
}

output "location" {
  description = "Primary Azure region"
  value       = azurerm_resource_group.rg.location
}

output "storage_account_name" {
  description = "Storage account name for raw data, models, and scripts"
  value       = azurerm_storage_account.storage.name
}

output "storage_primary_blob_endpoint" {
  description = "Storage account primary blob endpoint"
  value       = azurerm_storage_account.storage.primary_blob_endpoint
}

output "container_registry_login_server" {
  description = "ACR login server for Docker images"
  value       = azurerm_container_registry.acr.login_server
}

output "container_registry_admin_username" {
  description = "ACR admin username"
  value       = azurerm_container_registry.acr.admin_username
}

output "key_vault_uri" {
  description = "Azure Key Vault URI"
  value       = azurerm_key_vault.kv.vault_uri
}

output "sql_server_fqdn" {
  description = "Fully qualified domain name of Azure SQL Server"
  value       = azurerm_mssql_server.sql_server.fully_qualified_domain_name
}

output "sql_database_name" {
  description = "Name of the Azure SQL Database"
  value       = azurerm_mssql_database.sql_db.name
}

output "machine_learning_workspace_name" {
  description = "Azure ML Workspace name"
  value       = azurerm_machine_learning_workspace.mlw.name
}

output "data_factory_name" {
  description = "Azure Data Factory name"
  value       = azurerm_data_factory.adf.name
}

output "frontend_web_app_url" {
  description = "Direct URL for Frontend App Service"
  value       = "https://${azurerm_linux_web_app.frontend.default_hostname}"
}

output "api_container_fqdn" {
  description = "FQDN of the Prediction API Container Group"
  value       = "http://${azurerm_container_group.api.fqdn}:8000"
}

output "front_door_endpoint" {
  description = "Azure Front Door Global CDN URL"
  value       = "https://${azurerm_cdn_frontdoor_endpoint.endpoint.host_name}"
}

output "redis_hostname" {
  description = "Azure Cache for Redis hostname"
  value       = azurerm_redis_cache.redis.hostname
}

output "application_insights_connection_string" {
  description = "App Insights connection string"
  value       = azurerm_application_insights.appinsights.connection_string
  sensitive   = true
}

output "notification_recipient" {
  description = "Target recipient email for daily forecasts"
  value       = var.notification_email
}


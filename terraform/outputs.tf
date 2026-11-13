# =============================================================================
# Terraform Outputs
# Tomato Price Prediction Pipeline - Azure Infrastructure
# =============================================================================

output "resource_group_name" {
  description = "Name of the Azure Resource Group"
  value       = azurerm_resource_group.main.name
}

output "location" {
  description = "Azure region where resources are deployed"
  value       = azurerm_resource_group.main.location
}

output "storage_account_name" {
  description = "Name of the Azure Storage Account"
  value       = "${local.name_prefix}store${local.suffix}"
}

output "storage_primary_blob_endpoint" {
  description = "Primary blob endpoint of the Storage Account"
  value       = "https://${local.name_prefix}store${local.suffix}.blob.core.windows.net"
}

output "container_registry_login_server" {
  description = "Login server URL of the Azure Container Registry"
  value       = azurerm_container_registry.main.login_server
}

output "container_registry_admin_username" {
  description = "Admin username for the Container Registry"
  value       = azurerm_container_registry.main.admin_username
  sensitive   = true
}

output "key_vault_uri" {
  description = "URI of the Azure Key Vault"
  value       = azurerm_key_vault.main.vault_uri
}

output "machine_learning_workspace_name" {
  description = "Name of the Azure ML Workspace"
  value       = azurerm_machine_learning_workspace.main.name
}

output "data_factory_name" {
  description = "Name of the Azure Data Factory"
  value       = azurerm_data_factory.main.name
}

output "api_container_fqdn" {
  description = "Public URL of the prediction API container"
  value       = "http://${azurerm_container_group.prediction_service.fqdn}:8000"
}

output "front_door_endpoint" {
  description = "Azure Front Door endpoint URL"
  value       = "https://${azurerm_cdn_frontdoor_endpoint.frontend.host_name}"
}

output "application_insights_connection_string" {
  description = "Application Insights connection string"
  value       = azurerm_application_insights.main.connection_string
  sensitive   = true
}

output "notification_recipient" {
  description = "Email address for daily price notifications"
  value       = var.notification_email
}

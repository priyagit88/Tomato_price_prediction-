# =============================================================================
# 5. Azure Key Vault
#    Centralized secrets management for the pipeline
# =============================================================================

resource "azurerm_key_vault" "main" {
  name                       = "${local.name_prefix}-kv-${local.suffix}"
  resource_group_name        = azurerm_resource_group.main.name
  location                   = azurerm_resource_group.main.location
  tenant_id                  = var.tenant_id
  sku_name                   = "standard"
  soft_delete_retention_days = 7
  purge_protection_enabled   = false
  enable_rbac_authorization  = false

  # Combined single access policy for admin + terraform (same object ID avoids conflict)
  access_policy {
    tenant_id = var.tenant_id
    object_id = var.admin_object_id

    secret_permissions = [
      "Get", "List", "Set", "Delete", "Purge", "Recover"
    ]

    key_permissions = [
      "Get", "List", "Create", "Delete", "Purge", "Recover"
    ]
  }

  tags = local.common_tags
}

# Store ACR admin password in Key Vault
resource "azurerm_key_vault_secret" "acr_password" {
  name         = "acr-admin-password"
  value        = azurerm_container_registry.main.admin_password
  key_vault_id = azurerm_key_vault.main.id
}

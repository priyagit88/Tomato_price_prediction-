# =============================================================================
# 10. Notifications - Logic App for Email Alerts
#     Sends email notifications for price alerts and pipeline status
# =============================================================================

resource "azurerm_logic_app_workflow" "email_notifications" {
  name                = "${local.name_prefix}-logic-email-${local.suffix}"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location

  tags = local.common_tags
}

# Communication Services for email delivery
resource "azurerm_communication_service" "main" {
  name                = "${local.name_prefix}-comm-${local.suffix}"
  resource_group_name = azurerm_resource_group.main.name
  data_location       = "India"
  tags                = local.common_tags
}

# Email Communication Service
resource "azurerm_email_communication_service" "main" {
  name                = "${local.name_prefix}-emailcomm-${local.suffix}"
  resource_group_name = azurerm_resource_group.main.name
  data_location       = "India"
  tags                = local.common_tags
}

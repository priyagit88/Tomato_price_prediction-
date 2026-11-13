# =============================================================================
# 16. Azure Front Door
#     CDN and global load balancing — points to Container Group (API + frontend)
# =============================================================================

resource "azurerm_cdn_frontdoor_profile" "main" {
  name                = "${local.name_prefix}-fd-${local.suffix}"
  resource_group_name = azurerm_resource_group.main.name
  sku_name            = var.frontdoor_sku
  tags                = local.common_tags
}

resource "azurerm_cdn_frontdoor_endpoint" "frontend" {
  name                     = "${local.name_prefix}-fd-ep-${local.suffix}"
  cdn_frontdoor_profile_id = azurerm_cdn_frontdoor_profile.main.id
  tags                     = local.common_tags
}

resource "azurerm_cdn_frontdoor_origin_group" "frontend" {
  name                     = "frontend-origin-group"
  cdn_frontdoor_profile_id = azurerm_cdn_frontdoor_profile.main.id
  session_affinity_enabled = false

  load_balancing {
    sample_size                 = 4
    successful_samples_required = 3
  }

  health_probe {
    path                = "/api/health"
    protocol            = "Http"
    interval_in_seconds = 60
  }
}

resource "azurerm_cdn_frontdoor_origin" "webapp" {
  name                           = "webapp-origin"
  cdn_frontdoor_origin_group_id  = azurerm_cdn_frontdoor_origin_group.frontend.id
  enabled                        = true

  # Point to the Container Group (prediction API + frontend)
  host_name                      = azurerm_container_group.prediction_service.fqdn
  http_port                      = 8000
  https_port                     = 443
  origin_host_header             = azurerm_container_group.prediction_service.fqdn
  certificate_name_check_enabled = false
}

resource "azurerm_cdn_frontdoor_route" "frontend" {
  name                          = "frontend-route"
  cdn_frontdoor_endpoint_id     = azurerm_cdn_frontdoor_endpoint.frontend.id
  cdn_frontdoor_origin_group_id = azurerm_cdn_frontdoor_origin_group.frontend.id
  cdn_frontdoor_origin_ids      = [azurerm_cdn_frontdoor_origin.webapp.id]

  supported_protocols    = ["Http", "Https"]
  patterns_to_match      = ["/*"]
  forwarding_protocol    = "HttpOnly"
  https_redirect_enabled = false
  link_to_default_domain = true
}

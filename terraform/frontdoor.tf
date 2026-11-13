# =============================================================================
# 16. Azure Front Door
#     CDN and global load balancing for the frontend web app
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
    path                = "/"
    protocol            = "Https"
    interval_in_seconds = 60
  }
}

resource "azurerm_cdn_frontdoor_origin" "webapp" {
  name                          = "webapp-origin"
  cdn_frontdoor_origin_group_id = azurerm_cdn_frontdoor_origin_group.frontend.id
  enabled                       = true

  host_name          = azurerm_linux_web_app.frontend.default_hostname
  http_port          = 80
  https_port         = 443
  origin_host_header = azurerm_linux_web_app.frontend.default_hostname
  certificate_name_check_enabled = true
}

resource "azurerm_cdn_frontdoor_route" "frontend" {
  name                          = "frontend-route"
  cdn_frontdoor_endpoint_id     = azurerm_cdn_frontdoor_endpoint.frontend.id
  cdn_frontdoor_origin_group_id = azurerm_cdn_frontdoor_origin_group.frontend.id
  cdn_frontdoor_origin_ids      = [azurerm_cdn_frontdoor_origin.webapp.id]

  supported_protocols    = ["Https"]
  patterns_to_match      = ["/*"]
  forwarding_protocol    = "HttpsOnly"
  https_redirect_enabled = true
  link_to_default_domain = true
}

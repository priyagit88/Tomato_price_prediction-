# =============================================================================
# 6. Azure Data Factory
#    ETL pipeline orchestration for data ingestion and transformation
# =============================================================================

resource "azurerm_data_factory" "main" {
  name                = "${local.name_prefix}-adf-${local.suffix}"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location

  identity {
    type = "SystemAssigned"
  }

  tags = local.common_tags
}

# Linked Service: Azure Blob Storage
resource "azurerm_data_factory_linked_service_azure_blob_storage" "main" {
  name              = "ls-blob-storage"
  data_factory_id   = azurerm_data_factory.main.id
  connection_string = "DefaultEndpointsProtocol=https;AccountName=tomatostoreegk79m;EndpointSuffix=core.windows.net"
}

# Linked Service: Azure SQL Database (disabled – using local SQLite fallback)
# resource "azurerm_data_factory_linked_service_sql_server" "main" {
#   name            = "ls-sql-database"
#   data_factory_id = azurerm_data_factory.main.id
#   connection_string = join("", [
#     "Server=tcp:${azurerm_mssql_server.main.fully_qualified_domain_name},1433;",
#     "Initial Catalog=${azurerm_mssql_database.main.name};",
#     "User ID=${var.sql_admin_username};",
#     "Password=${var.sql_admin_password};",
#     "Encrypt=True;TrustServerCertificate=False;Connection Timeout=30;"
#   ])
# }

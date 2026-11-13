# =============================================================================
# Variables Configuration
# Tomato Price Prediction Pipeline - Azure Infrastructure
# =============================================================================

# -----------------------------------------------------------------------------
# General
# -----------------------------------------------------------------------------
variable "subscription_id" {
  description = "Azure subscription ID"
  type        = string
  sensitive   = true
}

variable "location" {
  description = "Azure region for all resources"
  type        = string
  default     = "centralindia"
}

variable "resource_group_name" {
  description = "Name of the Azure Resource Group"
  type        = string
  default     = "rg-tomato-prediction"
}

variable "project_name" {
  description = "Short project identifier used in resource naming"
  type        = string
  default     = "tomato"
}

variable "environment" {
  description = "Deployment environment (production, staging, dev)"
  type        = string
  default     = "production"
}

variable "common_tags" {
  description = "Tags applied to every resource"
  type        = map(string)
  default = {
    project     = "tomato-price-prediction"
    environment = "production"
    managed_by  = "terraform"
  }
}

# -----------------------------------------------------------------------------
# Admin / Notification
# -----------------------------------------------------------------------------
variable "admin_email" {
  description = "Administrator email for alerts and notifications"
  type        = string
}

variable "admin_object_id" {
  description = "Azure AD Object ID of the admin user (for Key Vault access policies)"
  type        = string
}

variable "tenant_id" {
  description = "Azure AD Tenant ID"
  type        = string
}

# -----------------------------------------------------------------------------
# SQL Database
# -----------------------------------------------------------------------------
variable "sql_admin_username" {
  description = "SQL Server administrator login"
  type        = string
  default     = "tomatoadmin"
}

variable "sql_admin_password" {
  description = "SQL Server administrator password"
  type        = string
  sensitive   = true
}

variable "sql_database_name" {
  description = "Name of the SQL database"
  type        = string
  default     = "tomatodb"
}

variable "sql_sku_name" {
  description = "SQL Database SKU (e.g. S0, S1, GP_S_Gen5_1)"
  type        = string
  default     = "S0"
}

# -----------------------------------------------------------------------------
# Container Registry
# -----------------------------------------------------------------------------
variable "acr_sku" {
  description = "SKU for Azure Container Registry (Basic, Standard, Premium)"
  type        = string
  default     = "Standard"
}

# -----------------------------------------------------------------------------
# Container Instances
# -----------------------------------------------------------------------------
variable "aci_cpu" {
  description = "CPU cores for prediction service container"
  type        = number
  default     = 1
}

variable "aci_memory" {
  description = "Memory in GB for prediction service container"
  type        = number
  default     = 2
}

variable "prediction_image" {
  description = "Docker image for the prediction service (updated after first ACR push)"
  type        = string
  default     = "mcr.microsoft.com/hello-world"
}

# -----------------------------------------------------------------------------
# App Service (Frontend)
# -----------------------------------------------------------------------------
variable "app_service_sku" {
  description = "App Service Plan SKU tier and size"
  type = object({
    tier = string
    size = string
  })
  default = {
    tier = "Standard"
    size = "S1"
  }
}

# -----------------------------------------------------------------------------
# Redis Cache
# -----------------------------------------------------------------------------
variable "redis_sku" {
  description = "Redis Cache SKU (Basic, Standard, Premium)"
  type        = string
  default     = "Basic"
}

variable "redis_family" {
  description = "Redis Cache family (C for Basic/Standard, P for Premium)"
  type        = string
  default     = "C"
}

variable "redis_capacity" {
  description = "Redis Cache capacity (0-6)"
  type        = number
  default     = 0
}

# -----------------------------------------------------------------------------
# Azure ML
# -----------------------------------------------------------------------------
variable "aml_sku" {
  description = "Azure Machine Learning Workspace SKU"
  type        = string
  default     = "Basic"
}

# -----------------------------------------------------------------------------
# Azure DevOps
# -----------------------------------------------------------------------------
variable "azuredevops_org_url" {
  description = "Azure DevOps organization URL (e.g. https://dev.azure.com/myorg)"
  type        = string
}

variable "azuredevops_pat" {
  description = "Azure DevOps personal access token"
  type        = string
  sensitive   = true
}

variable "azuredevops_project_name" {
  description = "Name of the Azure DevOps project"
  type        = string
  default     = "tomato-price-prediction"
}

# -----------------------------------------------------------------------------
# Front Door / CDN
# -----------------------------------------------------------------------------
variable "frontdoor_sku" {
  description = "Front Door SKU (Standard_AzureFrontDoor, Premium_AzureFrontDoor)"
  type        = string
  default     = "Standard_AzureFrontDoor"
}

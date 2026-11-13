# =============================================================================
# Terraform Providers Configuration
# Tomato Price Prediction Pipeline - Azure Infrastructure
# =============================================================================

terraform {
  required_version = ">= 1.5.0"

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.80"
    }
    azuread = {
      source  = "hashicorp/azuread"
      version = "~> 2.45"
    }
    azuredevops = {
      source  = "microsoft/azuredevops"
      version = "~> 0.11"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.5"
    }
  }
}

# Azure Resource Manager Provider
provider "azurerm" {
  features {
    key_vault {
      purge_soft_delete_on_destroy    = true
      recover_soft_deleted_key_vaults = true
    }
    resource_group {
      prevent_deletion_if_contains_resources = false
    }
  }

  subscription_id = var.subscription_id
}

# Azure Active Directory Provider
provider "azuread" {}

# Azure DevOps Provider
provider "azuredevops" {
  org_service_url       = var.azuredevops_org_url
  personal_access_token = var.azuredevops_pat
}

# Random provider for unique naming
provider "random" {}

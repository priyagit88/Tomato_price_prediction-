# =============================================================================
# Storage containers — accounts already exist, managed via az CLI
# We reference the account name directly (known from previous apply)
# =============================================================================

locals {
  storage_account_name    = "${local.name_prefix}store${local.suffix}"
  ml_storage_account_name = "${local.name_prefix}mlsa${local.suffix}"
}

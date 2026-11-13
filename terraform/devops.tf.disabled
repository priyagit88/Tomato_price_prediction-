# =============================================================================
# 13. Azure DevOps Project
#     CI/CD project for the tomato price prediction pipeline
# =============================================================================

resource "azuredevops_project" "main" {
  name               = var.azuredevops_project_name
  description        = "CI/CD pipelines for the Tomato Price Prediction system"
  visibility         = "private"
  version_control    = "Git"
  work_item_template = "Agile"

  features = {
    "testplans"    = "disabled"
    "artifacts"    = "enabled"
    "boards"       = "enabled"
    "repositories" = "enabled"
    "pipelines"    = "enabled"
  }
}

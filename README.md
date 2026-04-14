# Terraform Version Detector in GitHub Actions

Automatic detection of Terraform version for [hashicorp/setup-terraform](https://github.com/hashicorp/setup-terraform) action step.

Detects the version from (in order of priority):
1. `required_version` constraint in `terraform {}` blocks in `.tf` files
2. `.terraform-version` file (used by [tfenv](https://github.com/tfutils/tfenv)/[tfswitch](https://github.com/warrensbox/terraform-switcher))
3. `fallback-version` input, or latest release if not specified

Basic usage:

```yaml
steps:
- uses: actions/checkout@v5

- uses: skokado/terraform-version-detector@v1.2
  id: terraform-version
  with:
    path: path/to/dir

- uses: hashicorp/setup-terraform@v3
  with:
    terraform_version: ${{ steps.terraform-version.outputs.terraform-version }}
```

## Examples

```yaml
steps:
- uses: actions/checkout@v5

# --- app1/terraform.tf
# terraform {
#   required_version = ">= 1.10.0, < 1.11.0"
# }
- uses: skokado/terraform-version-detector@v1.2
  id: sample1
  with:
    path: app1/

- run: echo ${{ steps.sample1.outputs.terraform-version }}
# => Latest of 1.10.x 
```

Using a fallback version with detection check:

```yaml
steps:
- uses: actions/checkout@v5

- uses: skokado/terraform-version-detector@v1.2
  id: terraform-version
  with:
    path: path/to/dir
    fallback-version: "1.10.5"

- if: steps.terraform-version.outputs.version-was-detected == 'false'
  run: echo "Warning - no Terraform version pinned, using fallback"

- uses: hashicorp/setup-terraform@v3
  with:
    terraform_version: ${{ steps.terraform-version.outputs.terraform-version }}
```

For more details, see Terraform documentation on [Version Constraints](https://developer.hashicorp.com/terraform/language/expressions/version-constraints#version-constraint-syntax).

# Inputs

| Input | Description | Default |
|-------|-------------|---------|
| `path`  | Path to the directory containing Terraform configuration files. | `.` |
| `fallback-version` | Version to use when no version constraint is found. | `latest` |

# Outputs

| Output | Description |
|--------|-------------|
| `terraform-version` | The detected Terraform version based on the `required_version` constraint, `.terraform-version` file, or fallback. |
| `version-was-detected` | `true` if a version was found in the Terraform configuration, `false` if the fallback/latest was used. |

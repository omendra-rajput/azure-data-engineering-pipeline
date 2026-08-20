param(
    [string]$RepoName = "azure-data-engineering-pipeline",
    [string]$Visibility = "public"
)

$ErrorActionPreference = "Stop"

if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
    throw "GitHub CLI is not installed. Install gh or connect the GitHub plugin, then rerun this script."
}

gh auth status

git add .
git commit -m "Initial Azure data engineering pipeline project"
gh repo create $RepoName --source . --remote origin --push --$Visibility

Write-Host "Published repository: $RepoName"

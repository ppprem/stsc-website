param(
    [string]$Credentials = ".\stsc-490212-be6879d57ad0.json",
    [string]$Sitemap = ".\sitemap.xml",
    [string]$SiteRoot = "https://www.stsc.at/",
    [ValidateSet("URL_UPDATED", "URL_DELETED")]
    [string]$Type = "URL_UPDATED",
    [int]$Limit = 0,
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"

$python = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
$script = Join-Path $PSScriptRoot "google_indexing_api_submit.py"
$credentialsPath = Join-Path $PSScriptRoot $Credentials
$sitemapPath = Join-Path $PSScriptRoot $Sitemap

if (-not (Test-Path $python)) {
    throw "Python interpreter not found: $python"
}

if (-not (Test-Path $script)) {
    throw "Script not found: $script"
}

$args = @(
    $script,
    "--credentials", $credentialsPath,
    "--sitemap", $sitemapPath,
    "--site-root", $SiteRoot,
    "--type", $Type
)

if ($Limit -gt 0) {
    $args += @("--limit", $Limit)
}

if ($DryRun) {
    $args += "--dry-run"
}

& $python @args
exit $LASTEXITCODE
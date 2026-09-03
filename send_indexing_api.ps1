param(
    [string]$Credentials = ".\stsc-490212-be6879d57ad0.json",
    [string]$PropertyUrl = "https://www.stsc.at/",
    [string]$SiteRoot = "https://www.stsc.at/",
    [string]$Sitemap = ".\sitemap.xml",
    [string]$Posts = ".\posts.json",
    [string]$DbPath = ".\seo_targets.sqlite3",
    [string]$Homepage = ".\index.html",
    [int]$PriorityLimit = 0,
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"

$python = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
$script = Join-Path $PSScriptRoot "google_indexing_api_submit.py"
$credentialsPath = Join-Path $PSScriptRoot $Credentials
$sitemapPath = Join-Path $PSScriptRoot $Sitemap
$postsPath = Join-Path $PSScriptRoot $Posts
$dbPath = Join-Path $PSScriptRoot $DbPath
$homepagePath = Join-Path $PSScriptRoot $Homepage

if (-not (Test-Path $python)) {
    throw "Python interpreter not found: $python"
}

if (-not (Test-Path $script)) {
    throw "Script not found: $script"
}

$args = @(
    $script,
    "--credentials", $credentialsPath,
    "--property-url", $PropertyUrl,
    "--site-root", $SiteRoot,
    "--sitemap", $sitemapPath,
    "--posts", $postsPath,
    "--db-path", $dbPath,
    "--homepage", $homepagePath
)

if ($PriorityLimit -gt 0) {
    $args += @("--priority-limit", $PriorityLimit)
}

if ($DryRun) {
    $args += "--dry-run"
}

& $python @args
exit $LASTEXITCODE
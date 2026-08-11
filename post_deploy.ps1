param(
    [string]$SiteRoot = "https://www.stsc.at/",
    [string]$Sitemap = ".\sitemap.xml",
    [string]$Robots = ".\robots.txt",
    [switch]$ShowFiles
)

$ErrorActionPreference = "Stop"

function Get-AbsolutePath {
    param([string]$Path)

    if ([System.IO.Path]::IsPathRooted($Path)) {
        return $Path
    }

    return (Join-Path $PSScriptRoot $Path)
}

function Get-SitemapUrls {
    param([string]$Path)

    if (-not (Test-Path $Path)) {
        throw "Sitemap not found: $Path"
    }

    [xml]$xml = Get-Content -Path $Path -Raw
    $namespace = New-Object System.Xml.XmlNamespaceManager($xml.NameTable)
    $namespace.AddNamespace("sm", "http://www.sitemaps.org/schemas/sitemap/0.9")

    $urls = foreach ($node in $xml.SelectNodes("/sm:urlset/sm:url/sm:loc", $namespace)) {
        $node.InnerText.Trim()
    }

    return @($urls)
}

function Test-TextFileContains {
    param(
        [string]$Path,
        [string[]]$Needles
    )

    if (-not (Test-Path $Path)) {
        return $false
    }

    $content = Get-Content -Path $Path -Raw
    foreach ($needle in $Needles) {
        if ($content -notmatch [regex]::Escape($needle)) {
            return $false
        }
    }

    return $true
}

$sitemapPath = Get-AbsolutePath $Sitemap
$robotsPath = Get-AbsolutePath $Robots

Write-Host "Post-deploy check for $SiteRoot"
Write-Host "Sitemap: $sitemapPath"
Write-Host "Robots:  $robotsPath"

$urls = Get-SitemapUrls -Path $sitemapPath
$siteUrls = $urls | Where-Object { $_.StartsWith($SiteRoot, [System.StringComparison]::OrdinalIgnoreCase) }

Write-Host ""
Write-Host "URLs in sitemap: $($urls.Count)"
Write-Host "Matching site URLs: $($siteUrls.Count)"

if ($ShowFiles) {
    Write-Host ""
    Write-Host "URLs:"
    $siteUrls | ForEach-Object { Write-Host $_ }
}

$robotsOk = Test-TextFileContains -Path $robotsPath -Needles @("User-agent:", "Sitemap:")

Write-Host ""
Write-Host "robots.txt contains User-agent and Sitemap: $robotsOk"

if ($siteUrls.Count -eq 0) {
    Write-Host ""
    Write-Host "No matching URLs found." -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "Post-deploy check finished successfully."
exit 0
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

function Get-LocalPathFromUrl {
    param(
        [string]$Url,
        [string]$SiteRoot
    )

    $rootUri = [uri]$SiteRoot
    $urlUri = [uri]$Url

    if ($urlUri.Host -ne $rootUri.Host) {
        throw "URL is outside the configured site root: $Url"
    }

    $relativePath = [uri]::UnescapeDataString($urlUri.AbsolutePath)
    if ($relativePath -eq "/") {
        return (Join-Path $PSScriptRoot "index.html")
    }

    return (Join-Path $PSScriptRoot $relativePath.TrimStart('/'))
}

function Get-ExpectedCanonicalUrl {
    param(
        [string]$Url,
        [string]$SiteRoot
    )

    $rootUri = [uri]$SiteRoot
    $urlUri = [uri]$Url

    if ($urlUri.AbsolutePath -eq "/") {
        return ($rootUri.GetLeftPart([System.UriPartial]::Authority) + "/")
    }

    return ($rootUri.GetLeftPart([System.UriPartial]::Authority) + $urlUri.AbsolutePath)
}

function Test-PageSignals {
    param(
        [string]$Url,
        [string]$SiteRoot
    )

    $localPath = Get-LocalPathFromUrl -Url $Url -SiteRoot $SiteRoot
    if (-not (Test-Path $localPath)) {
        return [pscustomobject]@{
            Url = $Url
            LocalPath = $localPath
            Exists = $false
            CanonicalOk = $false
            NoIndex = $false
            RobotsMetaOk = $false
            Issues = @("Missing local file")
        }
    }

    $content = Get-Content -Path $localPath -Raw
    $expectedCanonical = Get-ExpectedCanonicalUrl -Url $Url -SiteRoot $SiteRoot
    $canonicalMatch = [regex]::Match($content, '<link\s+rel="canonical"\s+href="([^"]+)"\s*/?>', 'IgnoreCase')
    $robotsMatch = [regex]::Match($content, '<meta\s+name="robots"\s+content="([^"]+)"\s*/?>', 'IgnoreCase')

    $canonicalValue = if ($canonicalMatch.Success) { $canonicalMatch.Groups[1].Value } else { "" }
    $robotsValue = if ($robotsMatch.Success) { $robotsMatch.Groups[1].Value } else { "" }

    $issues = New-Object System.Collections.Generic.List[string]
    $canonicalOk = $false
    $noIndex = $false
    $robotsMetaOk = $false

    if (-not $canonicalMatch.Success) {
        $issues.Add("Missing canonical tag")
    }
    elseif ([uri]$canonicalValue -ne [uri]$expectedCanonical) {
        $issues.Add("Canonical points to a different URL: $canonicalValue")
    }
    else {
        $canonicalOk = $true
    }

    if ($content -match '(?i)noindex') {
        $issues.Add("Page contains noindex")
        $noIndex = $true
    }

    if ($robotsMatch.Success) {
        $robotsMetaOk = $robotsValue -match '(?i)index' -and $robotsValue -match '(?i)follow' -and $robotsValue -notmatch '(?i)noindex'
        if (-not $robotsMetaOk) {
            $issues.Add("robots meta is not index,follow style: $robotsValue")
        }
    }
    else {
        $issues.Add("Missing robots meta tag")
    }

    return [pscustomobject]@{
        Url = $Url
        LocalPath = $localPath
        Exists = $true
        CanonicalOk = $canonicalOk
        NoIndex = $noIndex
        RobotsMetaOk = $robotsMetaOk
        Issues = @($issues)
    }
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

$pageSignals = foreach ($url in $siteUrls) {
    Test-PageSignals -Url $url -SiteRoot $SiteRoot
}

$missingFiles = @($pageSignals | Where-Object { -not $_.Exists })
$canonicalIssues = @($pageSignals | Where-Object { $_.Exists -and -not $_.CanonicalOk })
$noIndexIssues = @($pageSignals | Where-Object { $_.Exists -and $_.NoIndex })
$robotsMetaIssues = @($pageSignals | Where-Object { $_.Exists -and -not $_.RobotsMetaOk })

$robotsOk = Test-TextFileContains -Path $robotsPath -Needles @("User-agent:", "Sitemap:")

Write-Host ""
Write-Host "robots.txt contains User-agent and Sitemap: $robotsOk"

Write-Host "Page files found: $($pageSignals.Count - $missingFiles.Count)/$($pageSignals.Count)"
Write-Host "Canonical issues: $($canonicalIssues.Count)"
Write-Host "noindex issues: $($noIndexIssues.Count)"
Write-Host "robots meta issues: $($robotsMetaIssues.Count)"

if ($ShowFiles) {
    if ($missingFiles.Count -gt 0) {
        Write-Host ""
        Write-Host "Missing files:"
        $missingFiles | ForEach-Object { Write-Host "$($_.Url) -> $($_.LocalPath)" }
    }

    if ($canonicalIssues.Count -gt 0) {
        Write-Host ""
        Write-Host "Canonical issues:"
        $canonicalIssues | ForEach-Object {
            Write-Host "$($_.Url) -> $($_.Issues -join '; ')"
        }
    }

    if ($noIndexIssues.Count -gt 0) {
        Write-Host ""
        Write-Host "noindex issues:"
        $noIndexIssues | ForEach-Object { Write-Host "$($_.Url) -> $($_.Issues -join '; ')" }
    }

    if ($robotsMetaIssues.Count -gt 0) {
        Write-Host ""
        Write-Host "robots meta issues:"
        $robotsMetaIssues | ForEach-Object { Write-Host "$($_.Url) -> $($_.Issues -join '; ')" }
    }
}

if ($siteUrls.Count -eq 0) {
    Write-Host ""
    Write-Host "No matching URLs found." -ForegroundColor Yellow
    exit 1
}

if ($missingFiles.Count -gt 0 -or $canonicalIssues.Count -gt 0 -or $noIndexIssues.Count -gt 0 -or $robotsMetaIssues.Count -gt 0 -or -not $robotsOk) {
    Write-Host ""
    Write-Host "Post-deploy check finished with warnings." -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "Post-deploy check finished successfully."
exit 0
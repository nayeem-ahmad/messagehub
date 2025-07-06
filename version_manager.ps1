# version_manager.ps1
# Version management utilities for MessageHub

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("patch", "minor", "major", "build", "get", "set")]
    [string]$Action,
    
    [string]$NewVersion = "",
    [switch]$DryRun
)

$versionFile = "version.json"

# Function to read current version
function Get-CurrentVersion {
    if (!(Test-Path $versionFile)) {
        Write-Host "Version file not found. Creating default version..." -ForegroundColor Yellow
        $defaultVersion = @{
            major = 1
            minor = 0
            patch = 0
            build = 0
            version = "1.0.0"
        }
        $defaultVersion | ConvertTo-Json -Depth 3 | Set-Content $versionFile -Encoding UTF8
        return $defaultVersion
    }
    
    try {
        $content = Get-Content $versionFile -Raw -Encoding UTF8
        return $content | ConvertFrom-Json
    }
    catch {
        Write-Host "Error reading version file: $_" -ForegroundColor Red
        exit 1
    }
}

# Function to save version
function Set-Version($versionObj) {
    try {
        $versionObj.version = "$($versionObj.major).$($versionObj.minor).$($versionObj.patch)"
        $versionObj | ConvertTo-Json -Depth 3 | Set-Content $versionFile -Encoding UTF8
        Write-Host "Version updated to: $($versionObj.version)" -ForegroundColor Green
        return $versionObj
    }
    catch {
        Write-Host "Error saving version file: $_" -ForegroundColor Red
        exit 1
    }
}

# Get current version
$currentVersion = Get-CurrentVersion

switch ($Action) {
    "get" {
        Write-Host "Current version: $($currentVersion.version)" -ForegroundColor Cyan
        Write-Host "  Major: $($currentVersion.major)" -ForegroundColor White
        Write-Host "  Minor: $($currentVersion.minor)" -ForegroundColor White
        Write-Host "  Patch: $($currentVersion.patch)" -ForegroundColor White
        Write-Host "  Build: $($currentVersion.build)" -ForegroundColor White
        return $currentVersion.version
    }
    
    "patch" {
        if ($DryRun) {
            $newPatch = $currentVersion.patch + 1
            Write-Host "Would increment patch: $($currentVersion.version) -> $($currentVersion.major).$($currentVersion.minor).$newPatch" -ForegroundColor Yellow
            return "$($currentVersion.major).$($currentVersion.minor).$newPatch"
        }
        $currentVersion.patch++
        $currentVersion.build = 0
        return (Set-Version $currentVersion).version
    }
    
    "minor" {
        if ($DryRun) {
            $newMinor = $currentVersion.minor + 1
            Write-Host "Would increment minor: $($currentVersion.version) -> $($currentVersion.major).$newMinor.0" -ForegroundColor Yellow
            return "$($currentVersion.major).$newMinor.0"
        }
        $currentVersion.minor++
        $currentVersion.patch = 0
        $currentVersion.build = 0
        return (Set-Version $currentVersion).version
    }
    
    "major" {
        if ($DryRun) {
            $newMajor = $currentVersion.major + 1
            Write-Host "Would increment major: $($currentVersion.version) -> $newMajor.0.0" -ForegroundColor Yellow
            return "$newMajor.0.0"
        }
        $currentVersion.major++
        $currentVersion.minor = 0
        $currentVersion.patch = 0
        $currentVersion.build = 0
        return (Set-Version $currentVersion).version
    }
    
    "build" {
        if ($DryRun) {
            $newBuild = $currentVersion.build + 1
            Write-Host "Would increment build: Build $($currentVersion.build) -> Build $newBuild" -ForegroundColor Yellow
            return $currentVersion.version
        }
        $currentVersion.build++
        Set-Version $currentVersion | Out-Null
        Write-Host "Build number incremented to: $($currentVersion.build)" -ForegroundColor Green
        return $currentVersion.version
    }
    
    "set" {
        if ([string]::IsNullOrEmpty($NewVersion)) {
            Write-Host "Error: NewVersion parameter is required for 'set' action" -ForegroundColor Red
            Write-Host "Usage: .\version_manager.ps1 -Action set -NewVersion '2.1.0'" -ForegroundColor Yellow
            exit 1
        }
        
        if ($NewVersion -notmatch '^\d+\.\d+\.\d+$') {
            Write-Host "Error: Invalid version format. Use format: major.minor.patch (e.g., '2.1.0')" -ForegroundColor Red
            exit 1
        }
        
        $parts = $NewVersion.Split('.')
        if ($DryRun) {
            Write-Host "Would set version: $($currentVersion.version) -> $NewVersion" -ForegroundColor Yellow
            return $NewVersion
        }
        
        $currentVersion.major = [int]$parts[0]
        $currentVersion.minor = [int]$parts[1]
        $currentVersion.patch = [int]$parts[2]
        $currentVersion.build = 0
        return (Set-Version $currentVersion).version
    }
}

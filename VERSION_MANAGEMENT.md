# Version Management Guide for MessageHub

This guide explains how to manage version numbers for your MessageHub installer.

## Quick Start

### Automatic Version Increment (Recommended)
```powershell
# Build with patch increment (1.0.0 -> 1.0.1)
.\deploy.ps1

# Build with minor increment (1.0.1 -> 1.1.0)
.\deploy.ps1 -IncrementVersion minor

# Build with major increment (1.1.0 -> 2.0.0)
.\deploy.ps1 -IncrementVersion major

# Build without version increment
.\deploy.ps1 -NoVersionIncrement
```

### Manual Version Setting
```powershell
# Set specific version
.\deploy.ps1 -Version "2.5.0"

# Set version and build installer only
.\deploy.ps1 -Version "2.5.0" -InstallerOnly
```

## Version Manager Tool

### Check Current Version
```powershell
.\version_manager.ps1 -Action get
```

### Increment Versions
```powershell
# Increment patch (1.0.0 -> 1.0.1)
.\version_manager.ps1 -Action patch

# Increment minor (1.0.1 -> 1.1.0)
.\version_manager.ps1 -Action minor

# Increment major (1.1.0 -> 2.0.0)
.\version_manager.ps1 -Action major

# Increment build number only
.\version_manager.ps1 -Action build
```

### Set Specific Version
```powershell
# Set to specific version
.\version_manager.ps1 -Action set -NewVersion "3.2.1"
```

### Preview Changes (Dry Run)
```powershell
# See what would happen without making changes
.\version_manager.ps1 -Action patch -DryRun
.\version_manager.ps1 -Action set -NewVersion "2.0.0" -DryRun
```

## Version File

The version information is stored in `version.json`:
```json
{
    "major": 1,
    "minor": 0,
    "patch": 5,
    "build": 12,
    "version": "1.0.5"
}
```

## Deployment Examples

### Development Builds
```powershell
# Quick patch for bug fixes
.\deploy.ps1

# New feature (minor increment)
.\deploy.ps1 -IncrementVersion minor
```

### Release Builds
```powershell
# Major release
.\deploy.ps1 -IncrementVersion major

# Release candidate
.\deploy.ps1 -Version "2.0.0-rc1"
```

### Testing Builds
```powershell
# Build without incrementing version
.\deploy.ps1 -NoVersionIncrement -BuildOnly

# Test installer creation only
.\deploy.ps1 -InstallerOnly
```

## Best Practices

1. **Use automatic increment for regular builds**: Let the script handle version numbers
2. **Patch increment (default)**: For bug fixes and small updates
3. **Minor increment**: For new features and enhancements
4. **Major increment**: For breaking changes or major releases
5. **Manual version**: For special releases or when following semantic versioning strictly

## Troubleshooting

### Reset Version
If you need to reset or fix the version:
```powershell
# Set to specific version
.\version_manager.ps1 -Action set -NewVersion "1.0.0"
```

### Version File Missing
If `version.json` is missing, it will be automatically recreated with default values (1.0.0).

### Check Before Building
Always check the current version before major releases:
```powershell
.\version_manager.ps1 -Action get
```

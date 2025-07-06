# Git Repository File Management

## Files TRACKED in Repository ✅

### Core Application
- `main.py` - Main application entry point
- `ui.py` - User interface code
- `db.py` - Database utilities
- `emailer.py` - Email functionality
- `contact_dialog.py` - Contact management UI
- `features/` - Feature modules
- `services/` - Service layer
- `requirements.txt` - Python dependencies

### Documentation
- `README.md` - Main project documentation
- `INSTALLER_GUIDE.md` - Step-by-step installer setup
- `INSTALLER_SUMMARY.md` - Quick installer reference
- `VERSION_MANAGEMENT.md` - Version management guide
- `LICENSE.txt` - Project license

### Templates and Tools
- `create_icon.py` - Icon creation script (template)
- `version_manager.ps1` - Version management utility
- `template/` - Template files for installer (safe defaults)
- `.gitignore` - Git ignore rules

## Files IGNORED (Not Tracked) ❌

### Build Output
- `build/` - PyInstaller build directory
- `dist/` - Distribution directory with executable
- `installer_output/` - Compiled installer files
- `*.spec` - PyInstaller spec files

### Generated Configuration
- `version.json` - Current version state (auto-generated)
- `build_exe.ps1` - Generated build script
- `deploy.ps1` - Generated deployment script
- `installer.iss` - Generated installer script
- `update_installer_version.ps1` - Generated version updater

### Generated Assets
- `icon.ico` - Generated application icon
- `icon.png` - Generated icon image

### Runtime Data
- `private/` - User data, settings, databases (SENSITIVE - excluded)
- `__pycache__/` - Python bytecode cache

## Template System 🔄

**Template files** (`template/` folder) are **tracked** and **included in installer**:
- ✅ Safe sample data with no sensitive information
- ✅ Provides good defaults for new installations  
- ✅ Auto-copied to `private/` folder on first run if files don't exist

**User data** (`private/` folder) is **ignored** and **excluded from installer**:
- ❌ Contains sensitive settings and credentials
- ❌ Personal contact databases and user modifications
- ❌ Not suitable for distribution

### Test Files
- `test_version_management.ps1` - Generated test script
- `verify_installer_setup.ps1` - Generated verification script

### System Files
- IDE/editor configs (`.vscode/`, `.idea/`)
- OS files (`.DS_Store`, `Thumbs.db`)
- Log files (`*.log`)

## Why This Setup?

✅ **Track**: Source code, documentation, and reusable templates
❌ **Ignore**: Generated files, build outputs, user data, and system files

This ensures:
- Clean repository with only essential files
- No sensitive user data in version control
- No build artifacts cluttering the repo
- Easy setup on new machines with template files
- Proper separation of source vs. generated content

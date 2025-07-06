# Installer Data Management Summary

## 🎯 Problem Solved

**Issue**: How to include a sample contacts database in the installer while excluding sensitive user settings?

**Solution**: Template system that separates safe defaults from sensitive user data.

## 📁 File Structure

```
MessageHub/
├── private/                    # ❌ User data (EXCLUDED from installer)
│   ├── contacts.db            # Real user contacts
│   ├── settings.json          # Sensitive credentials  
│   └── column_widths.json     # User preferences
├── template/                  # ✅ Safe templates (INCLUDED in installer)
│   ├── private/
│   │   ├── contacts_sample.db     # Sample contacts (safe)
│   │   ├── settings_template.json # Empty settings template
│   │   ├── column_widths_template.json
│   │   └── contacts_sample.csv    # Import format example
│   └── README.md
└── ...
```

## 🔄 How It Works

1. **Installation**: 
   - Installer includes `template/` folder with safe sample files
   - No sensitive user data is included

2. **First Run**:
   - App checks if `private/` files exist
   - If missing, copies templates from `template/private/` to `private/`
   - User gets working defaults without manual setup

3. **User Experience**:
   - New users see sample contacts and clean interface
   - Existing users keep their data during updates
   - No risk of exposing sensitive information

## 🛡️ Security Benefits

✅ **Safe for Distribution**:
- Sample database with fake contacts
- Template settings with no credentials
- No personal or sensitive information

❌ **Excluded from Installer**:
- Real user contact databases
- Email/SMS API credentials
- Personal settings and preferences
- User-generated content

## 🚀 Usage

### For Developers
```powershell
# Verify clean setup before building
.\verify_clean_installer.ps1

# Build installer - includes templates, excludes user data
.\deploy.ps1
```

### For Users
- Install application normally
- App automatically creates default files on first run
- Customize settings and add real contacts
- User data stays private and is preserved during updates

## 📋 Files Included in Installer

- ✅ `template/private/contacts_sample.db` - Sample contacts
- ✅ `template/private/settings_template.json` - Settings template
- ✅ `template/private/contacts_sample.csv` - CSV import example
- ❌ `private/*` - Real user data (excluded)

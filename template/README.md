# Template Files for MessageHub Installer

This folder contains template files that are included in the installer to provide default/sample data for new installations.

## Purpose

- **Safe to include in installer**: These files contain no sensitive information
- **Sample data**: Provides users with example configurations and sample contacts
- **Auto-setup**: The application automatically copies these to the user's private folder on first run

## Files Included

### `private/contacts_sample.db`
- Sample SQLite database with example contacts
- Copied to `private/contacts.db` if no existing database is found
- Gives users a starting point with sample data

### `private/settings_template.json`
- Template for application settings
- Contains empty/default values for all configuration options
- Copied to `private/settings.json` if no existing settings file is found

### `private/column_widths_template.json`
- Template for UI column width preferences
- Copied to `private/column_widths.json` if no existing file is found

### `private/contacts_sample.csv`
- Sample CSV file showing the expected format for contact imports
- Helps users understand how to format their contact data

## Security

✅ **Safe for distribution**:
- No sensitive credentials or personal data
- Only contains sample/template data
- No real email addresses or phone numbers

❌ **Not included**:
- Real user settings with credentials
- Actual user contact databases
- Personal configuration data
- Log files or user-generated content

## How It Works

1. **Installation**: Template files are copied to `{app}/template/private/`
2. **First Run**: Application checks if user files exist in `private/`
3. **Auto-Setup**: If user files don't exist, templates are copied as defaults
4. **User Data**: User modifications are saved to `private/` (excluded from version control)

This system ensures:
- Clean installations with helpful defaults
- No sensitive data in the installer
- User data is preserved during updates
- Easy setup for new users

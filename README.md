# NaCaZo MessageHub

A Python/Tkinter-based campaign manager for sending Email and SMS campaigns to your contacts. Supports SMTP, SendGrid, and Amazon SES for email, and bulksmsbd.net for SMS.

## Features
- Manage contacts and groups
- Send email campaigns via SMTP, SendGrid, or Amazon SES
- Send SMS campaigns via bulksmsbd.net
- Track email/SMS history
- User-friendly UI with settings dialog for all credentials

## Requirements
- Python 3.11+
- Windows OS (recommended)

## Setup Instructions

1. **Clone the repository**

2. **Create and activate a virtual environment**
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

3. **Install dependencies**
```powershell
pip install -r requirements.txt
```
The `requirements.txt` file lists the external libraries used by the project
(pandas, numpy, requests, boto3). Install from it to ensure all dependencies are
available.

4. **Move/copy your `private/` folder**
- The `private/` folder contains your credentials, settings, and CSV/contact data. Copy it from your backup or previous install if needed.
- This folder is ignored by git for security.

5. **Run the application**
```powershell
python main.py
```

6. **Configure settings**
- Open the app, go to Settings, and fill in your email/SMS credentials and preferences.
- Save your settings.

7. **Import contacts**
- Use the UI to import contacts from CSV (see the `private/` folder for sample files).

8. **Send campaigns**
- Select contacts and use the Email or SMS campaign features.

## Building and Deployment

### Quick Build
```powershell
# Build with automatic patch version increment
.\deploy.ps1

# Build with minor version increment (for new features)
.\deploy.ps1 -IncrementVersion minor

# Build with major version increment (for breaking changes)
.\deploy.ps1 -IncrementVersion major
```

### Version Management
```powershell
# Check current version
.\version_manager.ps1 -Action get

# Set specific version
.\deploy.ps1 -Version "2.1.0"

# Build without version increment
.\deploy.ps1 -NoVersionIncrement
```

For complete version management documentation, see [VERSION_MANAGEMENT.md](VERSION_MANAGEMENT.md).

### Build Options
- `.\deploy.ps1 -BuildOnly` - Build executable only
- `.\deploy.ps1 -InstallerOnly` - Create installer only
- `.\deploy.ps1 -Clean` - Clean previous builds first

## Notes
- All sensitive files (settings, CSVs, etc.) are stored in the `private/` folder and are not tracked by git.
- If you move to a new machine, copy the `private/` folder as well.
- For Amazon SES, make sure your sender email is verified in your AWS SES account.

## Troubleshooting
- If you see errors about missing modules, ensure your virtual environment is activated and dependencies are installed.
- For SMTP/SendGrid/SES errors, double-check your credentials and network connection.
- For SMS errors, check your API key and sender ID in the settings.

## License
Proprietary. For internal use only.

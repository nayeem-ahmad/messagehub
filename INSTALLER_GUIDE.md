# MessageHub Installer Guide

## Overview
This guide explains how to create a Windows installer for the MessageHub application that can be distributed and installed on other Windows PCs.

## Prerequisites

### 1. Python Environment
- Python 3.8 or higher
- Virtual environment with all dependencies installed
- All MessageHub source code

### 2. Required Software
- **PyInstaller**: For creating the executable
- **Inno Setup**: For creating the Windows installer
  - Download from: https://jrsoftware.org/isinfo.php
  - Install the Unicode version (recommended)

### 3. Optional Tools
- **Pillow**: For creating custom application icons
  ```bash
  pip install Pillow
  ```

## Step-by-Step Process

### Step 1: Prepare the Application

1. **Test the Application**
   ```bash
   python main.py
   ```
   Ensure everything works correctly before building.

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   pip install pyinstaller
   ```

3. **Create Application Icon (Optional)**
   ```bash
   python create_icon.py
   ```
   This creates `icon.ico` and `icon.png` files.

### Step 2: Build the Executable

#### Option A: Using the Build Script (Recommended)
```powershell
.\build_exe.ps1
```

#### Option B: Manual Build
```bash
python -m PyInstaller --onefile --windowed --name "MessageHub" --icon=icon.ico main.py
```

**Build Options Explained:**
- `--onefile`: Creates a single executable file
- `--windowed`: No console window (for GUI apps)
- `--name`: Sets the executable name
- `--icon`: Uses custom icon (optional)

### Step 3: Create the Installer

#### Option A: Complete Deployment (Recommended)
```powershell
.\deploy.ps1
```

**Deploy Script Options:**
- `.\deploy.ps1 -Clean`: Clean previous builds first
- `.\deploy.ps1 -BuildOnly`: Only build executable, skip installer
- `.\deploy.ps1 -InstallerOnly`: Only create installer (executable must exist)
- `.\deploy.ps1 -Version "1.1.0"`: Specify version number

#### Option B: Manual Installer Creation
1. Ensure Inno Setup is installed
2. Open `installer.iss` in Inno Setup Compiler
3. Click "Compile" or press F9

### Step 4: Test the Installer

1. **Test Installation**
   - Run the created installer on the development machine
   - Install to a different directory
   - Verify all features work

2. **Test on Clean Machine**
   - Test on a machine without Python installed
   - Verify the application runs independently
   - Check all email features work

## File Structure After Build

```
MessageHub/
├── dist/
│   ├── MessageHub.exe          # Main executable
│   └── private/                # Application data
├── installer_output/
│   └── MessageHub-Setup-v1.0.0.exe  # Final installer
├── build/                      # PyInstaller temp files
├── installer.iss               # Inno Setup script
├── build_exe.ps1              # Build script
├── deploy.ps1                 # Deployment script
└── icon.ico                   # Application icon
```

## Installer Features

The created installer includes:

### Installation Features
- **Custom installation directory** with sensible defaults
- **Start menu shortcuts** for easy access
- **Desktop icon** (optional, user choice)
- **Uninstaller** for clean removal
- **Registry entries** for proper Windows integration

### Included Files
- Main executable (`MessageHub.exe`)
- Application data (`private/` folder)
- Documentation (`README.md`, `LICENSE.txt`)
- Any additional documentation files

### User Experience
- **Professional installer UI** with branding
- **License agreement** display
- **Installation progress** tracking
- **Option to launch** application after install
- **Clean uninstall** process

## Distribution

### Installer Size
Typical installer sizes:
- **Small**: 15-25 MB (basic features)
- **Medium**: 25-40 MB (with all dependencies)
- **Large**: 40+ MB (with additional libraries)

### System Requirements
- **OS**: Windows 7 SP1 or higher
- **Architecture**: x64 or ARM64
- **Memory**: 100 MB free disk space
- **Network**: Required for email functionality

### Testing Checklist

Before distributing the installer:

- [ ] Installer runs on clean Windows machine
- [ ] Application launches without errors
- [ ] All main features work (email sending, contacts, history)
- [ ] Database is created and accessible
- [ ] Settings are saved and loaded correctly
- [ ] Network resilience features work
- [ ] Uninstaller removes all files cleanly
- [ ] No Python dependencies required on target machine

## Troubleshooting

### Common Build Issues

1. **Missing Dependencies**
   ```
   Error: ModuleNotFoundError: No module named 'tkinter'
   ```
   **Solution**: Add `--hidden-import=tkinter` to PyInstaller command

2. **Large Executable Size**
   ```
   Executable is 100+ MB
   ```
   **Solution**: Use `--exclude-module` for unused packages

3. **Application Won't Start**
   ```
   Error: Failed to execute script
   ```
   **Solution**: Check paths and ensure all files are included

### Common Installer Issues

1. **Inno Setup Not Found**
   ```
   Error: ISCC.exe not found
   ```
   **Solution**: Install Inno Setup or update the path in deploy script

2. **Missing Files**
   ```
   Error: Required file not found
   ```
   **Solution**: Ensure executable is built before creating installer

### Runtime Issues

1. **Database Errors**
   - Ensure `private/` folder is writable
   - Check file permissions in installation directory

2. **Network Issues**
   - Verify Windows Firewall isn't blocking the application
   - Test email functionality with different providers

## Advanced Configuration

### Custom Branding
Edit `installer.iss` to customize:
- Company name and URLs
- Application description
- Installation messages
- Custom license text

### Additional Features
- **Auto-updater**: Add version checking
- **Digital signatures**: Sign the executable and installer
- **Multiple languages**: Add language support to installer
- **Custom installation options**: Add feature selection

## Security Considerations

1. **Code Signing**: Consider signing the executable to avoid Windows warnings
2. **Antivirus**: Test with major antivirus software
3. **Digital Distribution**: Use secure download methods
4. **Version Control**: Include version information in all files

## Support

For issues during the installer creation process:
1. Check the build logs in the console output
2. Verify all prerequisites are installed
3. Test on a clean Windows virtual machine
4. Review the troubleshooting section above

The installer creates a professional, easy-to-distribute package that works on any Windows machine without requiring Python or other dependencies to be pre-installed.

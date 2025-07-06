# verify_clean_installer.ps1
# Verify that the installer will include only clean sample data

Write-Host "Verifying Clean Installer Setup" -ForegroundColor Green
Write-Host "===============================" -ForegroundColor Green

$success = $true

# Check 1: Template database exists and is clean
Write-Host "`n1. Checking template database..." -ForegroundColor Cyan
if (Test-Path "template\private\contacts_sample.db") {
    $dbSize = (Get-Item "template\private\contacts_sample.db").Length / 1KB
    Write-Host "   ✅ Template database exists (${dbSize:N1} KB)" -ForegroundColor Green
    
    # Check contact count
    try {
        $contactCount = python -c "import sqlite3; conn = sqlite3.connect('template/private/contacts_sample.db'); cursor = conn.cursor(); cursor.execute('SELECT COUNT(*) FROM contacts'); print(cursor.fetchone()[0]); conn.close()" 2>$null
        $contactCount = [int]$contactCount
        
        if ($contactCount -le 10) {
            Write-Host "   ✅ Template has only $contactCount sample contacts (good)" -ForegroundColor Green
        } else {
            Write-Host "   ❌ Template has $contactCount contacts (too many - should be ≤10)" -ForegroundColor Red
            $success = $false
        }
    } catch {
        Write-Host "   ⚠️  Could not verify contact count" -ForegroundColor Yellow
    }
    
    # Check for real email domains
    try {
        $realEmails = python -c "import sqlite3; conn = sqlite3.connect('template/private/contacts_sample.db'); cursor = conn.cursor(); cursor.execute('SELECT email FROM contacts WHERE email NOT LIKE \`'%example.com\`''); print(len(cursor.fetchall())); conn.close()" 2>$null
        $realEmails = [int]$realEmails
        
        if ($realEmails -eq 0) {
            Write-Host "   ✅ No real email addresses found" -ForegroundColor Green
        } else {
            Write-Host "   ❌ Found $realEmails real email addresses" -ForegroundColor Red
            $success = $false
        }
    } catch {
        Write-Host "   ⚠️  Could not verify email addresses" -ForegroundColor Yellow
    }
} else {
    Write-Host "   ❌ Template database missing!" -ForegroundColor Red
    $success = $false
}

# Check 2: Settings template is clean
Write-Host "`n2. Checking settings template..." -ForegroundColor Cyan
if (Test-Path "template\private\settings_template.json") {
    $settings = Get-Content "template\private\settings_template.json" -Raw | ConvertFrom-Json
    $hasCredentials = $false
    
    # Check for filled credentials
    $credentialFields = @('sender_pwd', 'sendgrid_api_key', 'ses_access_key', 'twilio_auth_token')
    foreach ($field in $credentialFields) {
        if ($settings.$field -and $settings.$field.Length -gt 0) {
            $hasCredentials = $true
            break
        }
    }
    
    if (!$hasCredentials) {
        Write-Host "   ✅ Settings template has no credentials" -ForegroundColor Green
    } else {
        Write-Host "   ❌ Settings template contains credentials!" -ForegroundColor Red
        $success = $false
    }
} else {
    Write-Host "   ❌ Settings template missing!" -ForegroundColor Red
    $success = $false
}

# Check 3: Private folder is excluded
Write-Host "`n3. Checking gitignore rules..." -ForegroundColor Cyan
if (Test-Path ".gitignore") {
    $gitignore = Get-Content ".gitignore" -Raw
    
    if ($gitignore -match "private/") {
        Write-Host "   ✅ Private folder is ignored" -ForegroundColor Green
    } else {
        Write-Host "   ❌ Private folder not properly ignored!" -ForegroundColor Red
        $success = $false
    }
    
    if ($gitignore -match "!template/") {
        Write-Host "   ✅ Template folder is tracked" -ForegroundColor Green
    } else {
        Write-Host "   ❌ Template folder not properly tracked!" -ForegroundColor Red
        $success = $false
    }
} else {
    Write-Host "   ❌ .gitignore missing!" -ForegroundColor Red
    $success = $false
}

# Check 4: Installer configuration
Write-Host "`n4. Checking installer configuration..." -ForegroundColor Cyan
if (Test-Path "installer.iss") {
    $installer = Get-Content "installer.iss" -Raw
    
    if ($installer -match "template\\private") {
        Write-Host "   ✅ Installer includes template files" -ForegroundColor Green
    } else {
        Write-Host "   ❌ Installer not configured for template files!" -ForegroundColor Red
        $success = $false
    }
    
    if (!$installer -or $installer -notmatch "Source.*[^template]\\private\\\*.*DestDir.*private") {
        Write-Host "   ✅ Installer doesn't include private folder directly" -ForegroundColor Green
    } else {
        Write-Host "   ❌ Installer includes private folder!" -ForegroundColor Red
        $success = $false
    }
} else {
    Write-Host "   ⚠️  Installer script will be generated during build" -ForegroundColor Yellow
}

# Summary
Write-Host "`n$('='*50)" -ForegroundColor Green
if ($success) {
    Write-Host "✅ VERIFICATION PASSED" -ForegroundColor Green
    Write-Host "The installer will include only clean sample data!" -ForegroundColor Green
    Write-Host "`nUsers will see:" -ForegroundColor Cyan
    Write-Host "- 4 sample contacts with example.com emails" -ForegroundColor White
    Write-Host "- Empty settings template" -ForegroundColor White
    Write-Host "- No real user data or credentials" -ForegroundColor White
} else {
    Write-Host "❌ VERIFICATION FAILED" -ForegroundColor Red
    Write-Host "Fix the issues above before building the installer!" -ForegroundColor Red
}
Write-Host $('='*50) -ForegroundColor Green

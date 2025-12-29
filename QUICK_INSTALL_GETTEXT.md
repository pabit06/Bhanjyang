# Quick Install gettext for Windows

## 🚀 Fastest Method (5 minutes)

### Step 1: Download
1. Open: https://mlocati.github.io/articles/gettext-iconv-windows.html
2. Click **"Download"** for **static** version
3. Save ZIP file

### Step 2: Extract
1. Extract ZIP to `C:\gettext`
2. You should see: `C:\gettext\bin\msgfmt.exe`

### Step 3: Add to PATH
**Option A: Using GUI (Easiest)**
1. Press `Win + R`
2. Type: `sysdm.cpl` → Enter
3. Click "Advanced" tab
4. Click "Environment Variables"
5. Under "System variables", find "Path" → Click "Edit"
6. Click "New" → Type: `C:\gettext\bin`
7. Click OK on all dialogs

**Option B: Using Command (Quick)**
```powershell
# Run PowerShell as Administrator
[Environment]::SetEnvironmentVariable("Path", $env:Path + ";C:\gettext\bin", "Machine")
```

### Step 4: Restart Terminal
- Close and reopen your terminal/IDE
- Or restart computer

### Step 5: Verify & Compile
```bash
# Check if installed
msgfmt --version

# Compile translations
python manage.py compilemessages
```

---

## ✅ Success Check

After compiling, you should see:
```
Processing language ne
```

And file should exist:
```
locale/ne/LC_MESSAGES/django.mo
```

---

## 🎉 Done!

Once compiled, your About app will use Nepali translations automatically!

---

**Need help?** See `docs/INSTALL_GETTEXT_WINDOWS.md` for detailed instructions.


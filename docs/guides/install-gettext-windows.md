# Installing gettext Tools on Windows

## Quick Installation Guide

### Option 1: Using Pre-built Binaries (Recommended)

1. **Download gettext for Windows:**
   - Visit: https://mlocati.github.io/articles/gettext-iconv-windows.html
   - Download the **static** version (not shared)
   - Extract to a folder (e.g., `C:\gettext`)

2. **Add to PATH:**
   - Open System Properties → Environment Variables
   - Edit "Path" in System variables
   - Add: `C:\gettext\bin` (or your extraction path + `\bin`)
   - Click OK on all dialogs

3. **Verify Installation:**
   ```bash
   msgfmt --version
   ```

4. **Compile Messages:**
   ```bash
   python manage.py compilemessages
   ```

---

### Option 2: Using Chocolatey (If Installed)

```bash
choco install gettext
```

Then restart terminal and run:
```bash
python manage.py compilemessages
```

---

### Option 3: Using Scoop (If Installed)

```bash
scoop install gettext
```

Then restart terminal and run:
```bash
python manage.py compilemessages
```

---

## Manual Installation Steps (Detailed)

### Step 1: Download
1. Go to: https://mlocati.github.io/articles/gettext-iconv-windows.html
2. Click "Download" for the **static** version
3. Save the ZIP file

### Step 2: Extract
1. Extract ZIP to `C:\gettext` (or any location you prefer)
2. You should have a folder structure like:
   ```
   C:\gettext\
   ├── bin\
   │   ├── msgfmt.exe
   │   ├── msgmerge.exe
   │   ├── xgettext.exe
   │   └── ...
   └── ...
   ```

### Step 3: Add to PATH
1. Press `Win + X` → System
2. Click "Advanced system settings"
3. Click "Environment Variables"
4. Under "System variables", find "Path" and click "Edit"
5. Click "New" and add: `C:\gettext\bin`
6. Click OK on all dialogs

### Step 4: Restart Terminal
- Close and reopen your terminal/command prompt
- Or restart your IDE

### Step 5: Verify
```bash
msgfmt --version
```

You should see version information.

### Step 6: Compile
```bash
python manage.py compilemessages
```

---

## Troubleshooting

### "msgfmt is not recognized"
- Make sure you added `\bin` folder to PATH (not the root folder)
- Restart terminal after adding to PATH
- Verify with: `where msgfmt`

### "Can't find msgfmt"
- Check PATH: `echo %PATH%` (should include gettext bin folder)
- Try full path: `C:\gettext\bin\msgfmt.exe --version`
- Restart computer if needed

### Alternative: Use WSL
If you have Windows Subsystem for Linux:
```bash
wsl
sudo apt-get update
sudo apt-get install gettext
python manage.py compilemessages
```

---

## After Installation

Once gettext is installed, you can compile translations:

```bash
# Compile all languages
python manage.py compilemessages

# Or compile specific language
python manage.py compilemessages -l ne
```

This will create `django.mo` files that Django uses for translations.

---

## Verification

After compiling, check:
```bash
# Should exist:
locale/ne/LC_MESSAGES/django.mo
```

If the `.mo` file exists, translations are ready to use!

---

**Note:** The `.po` file is already created with all translations. Once you compile it, the app will use Nepali translations automatically.


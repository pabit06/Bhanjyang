# Flag Images

This directory should contain flag images for currency codes used in the exchange rate widget.

## Required Flags

Download the following flag images from [flagcdn.com](https://flagcdn.com) or another source:

- `us.png` - United States (USD)
- `eu.png` - European Union (EUR)
- `gb.png` - United Kingdom (GBP)
- `au.png` - Australia (AUD)
- `ca.png` - Canada (CAD)
- `jp.png` - Japan (JPY)
- `in.png` - India (INR)
- `ae.png` - United Arab Emirates (AED)
- `sa.png` - Saudi Arabia (SAR)
- `qa.png` - Qatar (QAR)
- `sg.png` - Singapore (SGD)
- `my.png` - Malaysia (MYR)
- `th.png` - Thailand (THB)
- `np.png` - Nepal (NPR)

## Download Instructions

### Option 1: Using flagcdn.com API
```bash
# Download all required flags (w40 size = 40px width)
curl -o us.png https://flagcdn.com/w40/us.png
curl -o eu.png https://flagcdn.com/w40/eu.png
curl -o gb.png https://flagcdn.com/w40/gb.png
curl -o au.png https://flagcdn.com/w40/au.png
curl -o ca.png https://flagcdn.com/w40/ca.png
curl -o jp.png https://flagcdn.com/w40/jp.png
curl -o in.png https://flagcdn.com/w40/in.png
curl -o ae.png https://flagcdn.com/w40/ae.png
curl -o sa.png https://flagcdn.com/w40/sa.png
curl -o qa.png https://flagcdn.com/w40/qa.png
curl -o sg.png https://flagcdn.com/w40/sg.png
curl -o my.png https://flagcdn.com/w40/my.png
curl -o th.png https://flagcdn.com/w40/th.png
curl -o np.png https://flagcdn.com/w40/np.png
```

### Option 2: Using PowerShell (Windows)
```powershell
$flags = @('us', 'eu', 'gb', 'au', 'ca', 'jp', 'in', 'ae', 'sa', 'qa', 'sg', 'my', 'th', 'np')
foreach ($flag in $flags) {
    Invoke-WebRequest -Uri "https://flagcdn.com/w40/$flag.png" -OutFile "$flag.png"
}
```

### Option 3: Manual Download
Visit https://flagcdn.com and download each flag manually.

## After Downloading

Once flags are downloaded, update `apps/services/templatetags/remittance_tags.py` to use `flag_image_local` instead of `flag_image` in templates, or modify `flag_image` to check for local files first.

## Current Status

⚠️ **Flags are currently loaded from flagcdn.com as fallback until local files are added.**


# ATLAS SSD startup

Modern Windows versions do not allow a USB/SSD drive to silently start software on any computer when it is plugged in. This is a security restriction.

Use one of these safe options:

1. Run `Start_ATLAS.bat` from the SSD.
2. If PowerShell is preferred, run `Start_ATLAS.ps1`.
3. For automatic startup on a specific trusted computer, create a Windows Startup folder shortcut or scheduled task that points to `Start_ATLAS.bat`.

Requirements on the computer:

- Python 3.12 installed.
- Project dependencies installed with:

```powershell
pip install -r requirements.txt
```

After Gemini AI is connected, set the Gemini key as an environment variable on that computer, for example:

```powershell
setx GEMINI_API_KEY "your-key-here"
```

Do not store API keys directly on the SSD in plain text.

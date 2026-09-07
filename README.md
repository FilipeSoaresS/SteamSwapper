# 🎮 Steam Swapper

**Steam Swapper** is a lightweight Windows desktop application designed to help you organize and quickly switch between multiple Steam accounts.

It provides a simple dark-mode graphical interface where each account can be assigned a number, a Steam login, and a custom note. Select an account, click **Switch Account**, and Steam Swapper will restart Steam using the selected login.

> [!IMPORTANT]
> Steam Swapper does **not** store passwords, bypass Steam Guard, or modify Steam account security. Authentication remains entirely handled by the official Steam client.

> [!NOTE]
> If you use third-party accounts, make sure you have permission to access them and understand Steam's applicable rules and risks.

---

## ✨ Features

- 🌙 Dark-mode Windows interface
- 🔢 Account shortcuts from `0` to `100`
- 👤 Steam login management
- 📝 Custom notes for each account
- ➕ Add accounts
- ✏️ Edit existing accounts
- 🗑️ Remove accounts
- 🔄 Refresh the account list
- ⚡ One-click Steam account switching
- 🔎 Automatic Steam installation detection
- 💾 Local account database
- 🎨 Custom application logo and Windows icon
- 📦 Standalone Windows `.exe` support
- 🔐 No password storage
- 🛡️ Steam Guard remains fully controlled by Steam

---

## 🚀 Quick Start

### For regular users

Download the latest `SteamSwapper.exe` from the project's **Releases** section.

No Python installation is required.

Run:

```text
SteamSwapper.exe
```

Steam Swapper will automatically create its local account database when necessary.

### For developers

Clone or download the repository and install the development dependencies:

```cmd
pip install -r requirements.txt
```

Then run:

```cmd
python steam_swapper.py
```

---

# 🧭 How to Use Steam Swapper

## ➕ Adding an Account

Click:

```text
+ Add Account
```

You will be asked for three values.

### 1. Account Number

Choose a number between:

```text
0 - 100
```

For example:

```text
10
```

Each number can belong to only one account.

### 2. Steam Login

Enter the login name used to sign in to the Steam account.

For example:

```text
my_steam_login
```

> Your Steam login may be different from the public profile name displayed on Steam.

### 3. Note

Add an optional description to help identify the account.

Examples:

```text
Main account
Elden Ring
Shared games
Forza Horizon 5
```

The account will then appear in the main list:

```text
10 | my_steam_login | Elden Ring
```

---

## ✏️ Editing an Account

Select an account and click:

```text
Edit
```

You can change:

- Account number
- Steam login
- Note

Steam Swapper prevents duplicate account numbers and duplicate logins.

---

## 🗑️ Removing an Account

Select an account and click:

```text
Remove
```

Steam Swapper will ask for confirmation before removing it.

> Removing an entry only deletes it from Steam Swapper's local database. It does **not** delete or modify the actual Steam account.

---

## 🔄 Refreshing the Account List

Click:

```text
Refresh
```

Steam Swapper will reload the account information stored in:

```text
steam_contas.txt
```

This can be useful if the database was modified externally.

---

## ⚡ Switching Accounts

Select the account you want to use and click:

```text
SWITCH ACCOUNT
```

Steam Swapper will:

1. Detect your Steam installation.
2. Close the currently running Steam client.
3. Wait for Steam to shut down.
4. Close remaining Steam processes if necessary.
5. Restart Steam using the selected login.

Steam remains responsible for authentication.

If Steam requests any of the following:

- Password
- Steam Guard
- Email confirmation
- Mobile confirmation

complete the authentication directly inside Steam.

---

# 💾 Account Database

Steam Swapper automatically creates:

```text
steam_contas.txt
```

The database is stored next to the Python script or compiled executable.

Accounts use the following format:

```text
NUMBER|LOGIN|NOTE
```

Example:

```text
1|main_account|Main account
10|eldenring_account|Elden Ring
20|forza_account|Forza Horizon 5
```

Only the following information is stored:

- Account number
- Steam login
- Custom note

**Passwords are never stored.**

---

# 🔐 Security

Steam Swapper does **not**:

- Read Steam passwords
- Save Steam passwords
- Decrypt Steam credentials
- Bypass Steam Guard
- Disable Steam authentication
- Modify Steam account security

Authentication remains handled by the official Steam client.

A database entry contains only information similar to:

```text
15|my_account|Elden Ring
```

> [!WARNING]
> Do not publish your personal `steam_contas.txt` file if it contains real Steam login names.

---

# 🔎 Steam Detection

Steam Swapper first attempts to detect Steam through the Windows Registry.

If Steam cannot be found there, the application also checks common installation locations:

```text
C:\Program Files (x86)\Steam\steam.exe
```

```text
C:\Program Files\Steam\steam.exe
```

```text
C:\Steam\steam.exe
```

No user-specific Windows directory is hardcoded into Steam Swapper.

---

# 🌙 Dark Mode

Steam Swapper uses a custom dark interface designed for Windows.

The application also attempts to enable the native Windows dark title bar through the Windows DWM API.

The interface uses:

- Dark backgrounds
- Light text
- Blue selection highlights
- Orange primary action buttons

---

# 📁 Project Structure

The repository uses the following structure:

```text
Steam-Swapper/
│
├── img/
│   ├── 2.png
│   └── 2.ico
│
├── .gitignore
├── README.md
├── requirements.txt
├── SteamSwapper.spec
└── steam_swapper.py
```

PyInstaller may additionally generate:

```text
build/
dist/
```

These folders should not be committed to the repository.

---

# 🖼️ Application Assets

## `img/2.png`

Used as the main logo displayed above the **STEAM SWAPPER** title inside the application.

## `img/2.ico`

Used as the native Windows application icon for:

- Window title bar
- Executable
- Windows shortcuts
- Application icon

The `.ico` file should be a real Windows ICO file rather than a renamed PNG.

Recommended sizes include:

```text
16x16
24x24
32x32
48x48
64x64
128x128
256x256
```

---

# 🧑‍💻 Running From Source

## Requirements

Steam Swapper is designed for Windows.

You will need:

- Python
- Steam
- The dependencies listed in `requirements.txt`

Check that Python is available:

```cmd
python --version
```

Install the project dependencies:

```cmd
pip install -r requirements.txt
```

Then launch Steam Swapper:

```cmd
python steam_swapper.py
```

---

# 📦 Building the Windows Executable

## First Build

If `SteamSwapper.spec` does not exist yet, run:

```cmd
pyinstaller --clean --noconfirm --onefile --windowed --name "SteamSwapper" --icon "img\2.ico" --add-data "img\2.png;img" --add-data "img\2.ico;img" steam_swapper.py
```

PyInstaller will generate:

```text
SteamSwapper.spec
build/
dist/
```

The executable will be created at:

```text
dist\SteamSwapper.exe
```

---

## Rebuilding After Code Changes

Once `SteamSwapper.spec` exists, you normally only need:

```cmd
pyinstaller --clean --noconfirm SteamSwapper.spec
```

The new executable will be generated at:

```text
dist\SteamSwapper.exe
```

You do **not** need to reinstall PyInstaller or Pillow every time you change the source code.

---

# ⚙️ PyInstaller Resources

The `Analysis` section of `SteamSwapper.spec` should contain:

```python
datas=[
    ('img\\2.png', 'img'),
    ('img\\2.ico', 'img'),
],
```

The `EXE` section should use:

```python
icon='img\\2.ico',
```

This ensures the application logo and Windows icon are bundled with the executable.

---

# 📦 Standalone Distribution

The executable generated by PyInstaller is designed to run without requiring the user to install:

- Python
- PyInstaller
- Pillow
- Packages from `requirements.txt`

Regular users only need:

```text
SteamSwapper.exe
```

The development dependencies are only necessary when running or building the project from source.

---

# 🌐 Publishing on GitHub

The recommended repository contents are:

```text
Steam-Swapper/
│
├── img/
│   ├── 2.png
│   └── 2.ico
│
├── .gitignore
├── README.md
├── requirements.txt
├── SteamSwapper.spec
└── steam_swapper.py
```

Do **not** commit:

```text
build/
dist/
__pycache__/
.venv/
steam_contas.txt
```

A recommended `.gitignore` includes:

```gitignore
# Python
__pycache__/
*.pyc
*.pyo
*.pyd

# Virtual environments
.venv/
venv/
env/

# PyInstaller
build/
dist/
*.spec.bak

# Personal Steam Swapper data
steam_contas.txt

# IDEs
.vscode/
.idea/

# Windows
Thumbs.db
Desktop.ini

# Temporary files
*.tmp
*.log
```

---

# 📥 GitHub Releases

Regular users should preferably download Steam Swapper through the project's **GitHub Releases** page rather than building it themselves.

A release can contain:

```text
SteamSwapper-v1.0.0.exe
```

This allows users to download and run Steam Swapper without installing Python.

A future version could also provide a traditional Windows installer:

```text
SteamSwapper-Setup-v1.0.0.exe
```

---

# 🛠️ Troubleshooting

## The old version still opens

If you edited:

```text
steam_swapper.py
```

but launch:

```text
dist\SteamSwapper.exe
```

you are still running the previously compiled version.

Rebuild it:

```cmd
pyinstaller --clean --noconfirm SteamSwapper.spec
```

---

## The logo does not appear

Verify that this file exists:

```text
img\2.png
```

Also make sure the `.spec` contains:

```python
('img\\2.png', 'img')
```

---

## The Windows icon does not appear

Verify that:

```text
img\2.ico
```

exists and is a valid Windows ICO file.

Also verify that `SteamSwapper.spec` contains:

```python
icon='img\\2.ico'
```

---

## PyInstaller reports that Pillow is missing

Install the project dependencies:

```cmd
pip install -r requirements.txt
```

Or install Pillow directly:

```cmd
pip install pillow
```

Then rebuild the executable.

---

## Steam cannot be detected

Make sure Steam is installed on Windows.

Steam Swapper checks the Windows Registry and several common Steam installation directories automatically.

---

# 🧪 Development Workflow

A typical development workflow is:

```text
Edit steam_swapper.py
        ↓
python steam_swapper.py
        ↓
Test the application
        ↓
pyinstaller --clean --noconfirm SteamSwapper.spec
        ↓
dist\SteamSwapper.exe
```

During development, run the Python source directly.

Rebuild the `.exe` when you are ready to distribute a new version.

---

# ⚠️ Important Notes

- Steam Swapper is designed for Windows.
- Steam must be installed to switch accounts.
- Steam Swapper does not store passwords.
- Steam Swapper does not bypass Steam Guard.
- Steam may request authentication after switching accounts.
- Account switching behavior may depend on the current Steam client version and remembered Steam sessions.
- Never publish a personal `steam_contas.txt` containing real account information.
- Only use accounts you are authorized to access.

---

## 🎮 Steam Swapper

**Choose an account → Switch Steam → Play**

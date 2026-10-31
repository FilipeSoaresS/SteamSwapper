# Steam Swapper

Modular Python/Tkinter desktop application for organizing and switching between Steam accounts.

## Structure

```text
SteamSwapper/
├── app.py
├── SteamSwapper.spec
├── steam_swapper.json
├── avatars/
├── img/
│   ├── 2.png
│   └── 2.ico
└── app/
    ├── config.py
    ├── main.py
    ├── data/
    ├── models/
    ├── services/
    ├── ui/
    └── utils/
```

## Run from VS Code

Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Then run:

```powershell
python app.py
```

## Data

Accounts and settings are stored in `steam_swapper.json` beside the executable/script.

Avatars are stored in `avatars/` beside the executable/script.

If the old `steam_contas.txt` exists and the JSON has no accounts, the application imports it automatically and renames it to:

```text
steam_contas.txt.backup
```

## Build the Windows EXE

Make sure `img/2.ico` and `img/2.png` exist, then run:

```powershell
pyinstaller --clean --noconfirm SteamSwapper.spec
```

The executable is created at:

```text
dist/SteamSwapper.exe
```

## Important

The `.venv`, `build`, `dist`, `__pycache__`, `steam_swapper.json`, and personal avatar files should not be committed to a public repository.


## Interface updates

- Adjustable icon/grid size from 60% to 140%.
- Persistent dark/light theme switch.
- Imported accounts can automatically attempt to retrieve their Steam profile avatar.
- Theme and icon size are saved in `steam_swapper.json`.

## Troca de contas e modo Offline

A troca de contas mantém a sequência do código base funcional: o Steam é encerrado com `steam.exe -shutdown`, o aplicativo aguarda o processo terminar e então inicia a conta selecionada com `steam.exe -login <login>`.

No modo Offline, o aplicativo prepara `config\loginusers.vdf` com `WantsOfflineMode=1`, `MostRecent=1` e `SkipOfflineModeWarning=1` para a conta selecionada e inicia o Steam sem `-login`, permitindo que o próprio cliente carregue a conta salva marcada como mais recente. Antes de uma troca Online/Auto, os flags offline são limpos para não contaminar a próxima inicialização.

O arquivo `loginusers.vdf` é mantido com sua estrutura original e recebe um backup chamado `loginusers.vdf.steam_swapper_backup` antes da primeira alteração.


## Interface redesign

The current UI uses a launcher-style composition while preserving the Steam Swapper visual identity:

- Dark/light themes with the existing Steam-inspired blue/orange palette.
- Atmospheric background rings and subtle glow accents.
- Floating navigation/header inspired by modern game managers.
- Selected account presented as a large profile/hero card.
- Remaining accounts shown as visual profile cards in a responsive grid.
- List view remains available as an alternative.
- Custom confirmation, information, error, and account dialogs; no native messagebox for application actions.
- Search, sorting, avatar size, launch mode, and account management remain available.

The account switching core keeps the proven base sequence for Online/Auto: close Steam completely, then launch `steam.exe -login <login>`. Offline mode remains the separate `loginusers.vdf` preparation flow.


## Current UI

The current interface uses a highlighted account card with the Online/Offline/Auto selector inside the card. The bottom toolbar contains only view and sorting controls. Account cards use a fixed compact size, and the current account card includes a localized Restart Steam action.

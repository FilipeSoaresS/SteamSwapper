from pathlib import Path
import sys

APP_NAME = "Steam Swapper"


def application_directory() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parents[1]


def resource_directory() -> Path:
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS)
    return application_directory()


APP_DIR = application_directory()
RESOURCE_DIR = resource_directory()
IMG_DIR = RESOURCE_DIR / "img"
ICON_FILE = IMG_DIR / "2.ico"
LOGO_FILE = IMG_DIR / "2.png"
DATA_FILE = APP_DIR / "steam_swapper.json"
AVATAR_DIR = APP_DIR / "avatars"

THEMES = {
    "dark": {
        "BG": "#171a21", "BG_DARK": "#101214", "PANEL": "#1b2838",
        "PANEL_ALT": "#243447", "PANEL_HOVER": "#2a475e",
        "TEXT": "#f1f1f1", "MUTED": "#8f98a0", "BORDER": "#30465c",
        "STEAM_BLUE": "#1a9fff", "STEAM_BLUE_HOVER": "#66c0f4",
        "ORANGE": "#ff9418", "ORANGE_HOVER": "#ffad47",
        "GREEN": "#66c0a0", "RED": "#d9534f",
        "BG_GLOW": "#1a3850", "BG_GLOW_2": "#173b2f", "GLOW_DOT": "#23445a",
        "AVATAR_PLACEHOLDER": "#26394a",
        "SCROLL_TRACK": "#101820", "SCROLL_THUMB": "#26394a",
        "SCROLL_THUMB_HOVER": "#35536c",
        "CARD_BG": "#18232d", "CARD_HOVER": "#203344", "CARD_BORDER": "#2d4254",
        "HERO_BG": "#141b20", "HERO_BORDER": "#365064",
        "CONTROL_BG": "#243447", "CONTROL_HOVER": "#2a475e",
        "TITLEBAR_BG": "#151c23", "TITLEBAR_BORDER": "#263b4c",
    },
    "light": {
        "BG": "#e8edf3", "BG_DARK": "#d7dee7", "PANEL": "#f4f6f9",
        "PANEL_ALT": "#ffffff", "PANEL_HOVER": "#e4ebf3",
        "TEXT": "#17202a", "MUTED": "#687585", "BORDER": "#c5d0dc",
        "STEAM_BLUE": "#1a75c8", "STEAM_BLUE_HOVER": "#238be6",
        "ORANGE": "#d97800", "ORANGE_HOVER": "#ed8b00",
        "GREEN": "#238a68", "RED": "#c53f3a",
        "BG_GLOW": "#cbd9e7", "BG_GLOW_2": "#d0ddd5", "GLOW_DOT": "#b9cadb",
        "AVATAR_PLACEHOLDER": "#c9d5e1",
        "SCROLL_TRACK": "#dce3eb", "SCROLL_THUMB": "#aebccc",
        "SCROLL_THUMB_HOVER": "#8fa2b5",
        "CARD_BG": "#f4f6f9", "CARD_HOVER": "#e4ebf3", "CARD_BORDER": "#c5d0dc",
        "HERO_BG": "#f4f6f9", "HERO_BORDER": "#c5d0dc",
        "CONTROL_BG": "#ffffff", "CONTROL_HOVER": "#e4ebf3",
        "TITLEBAR_BG": "#c5d0dc", "TITLEBAR_BORDER": "#aebdcb",
    },
}

# Backwards-compatible names used by older modules.
def theme(name="dark"):
    return THEMES.get(name, THEMES["dark"])

def get_theme(name):
    return theme(name)

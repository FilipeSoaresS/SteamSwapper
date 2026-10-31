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
ART_FILE = IMG_DIR / "steam_swapper_art.png"
DATA_FILE = APP_DIR / "steam_swapper.json"
AVATAR_DIR = APP_DIR / "avatars"

THEMES = {
    "dark": {
        "BG": "#050B13", "BG_DARK": "#050B13", "PANEL": "#0B1623",
        "PANEL_ALT": "#101E2D", "PANEL_HOVER": "#17283C",
        "TEXT": "#F1F6FF", "MUTED": "#9BB4D2", "BORDER": "#29445E",
        "STEAM_BLUE": "#009DFF", "STEAM_BLUE_HOVER": "#00B8FF",
        "ORANGE": "#ff9418", "ORANGE_HOVER": "#ffad47",
        "GREEN": "#35DB96", "RED": "#d9534f",
        "BG_GLOW": "#1a3850", "BG_GLOW_2": "#173b2f", "GLOW_DOT": "#23445a",
        "AVATAR_PLACEHOLDER": "#17283C",
        "SCROLL_TRACK": "#07111B", "SCROLL_THUMB": "#29445E",
        "SCROLL_THUMB_HOVER": "#426788",
        "CARD_BG": "#101E2D", "CARD_HOVER": "#14263A", "CARD_BORDER": "#203A53",
        "HERO_BG": "#0B1623", "HERO_BORDER": "#29445E",
        "CONTROL_BG": "#0B1623", "CONTROL_HOVER": "#17283C",
        "TITLEBAR_BG": "#0B1623", "TITLEBAR_BORDER": "#1C344B",
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

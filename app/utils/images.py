import re
import shutil
import urllib.request
from pathlib import Path
from urllib.parse import quote

from app.config import AVATAR_DIR


def copy_avatar(source):
    source = Path(source)
    AVATAR_DIR.mkdir(parents=True, exist_ok=True)
    destination = AVATAR_DIR / f"avatar_{source.stem}_{abs(hash(str(source))) & 0xFFFFFFFF}{source.suffix.lower()}"
    shutil.copy2(source, destination)
    return str(destination)


def _download(url, timeout=8):
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 SteamSwapper/2.0"},
    )
    with urllib.request.urlopen(req, timeout=timeout) as response:
        return response.read(), response.headers.get("Content-Type", "")


def _steam_avatar_url(identifier):
    identifier = str(identifier or "").strip()
    if not identifier:
        return None
    if identifier.isdigit() and len(identifier) >= 15:
        urls = [
            f"https://steamcommunity.com/profiles/{identifier}/?xml=1",
            f"https://steamcommunity.com/profiles/{identifier}/",
        ]
    else:
        encoded = quote(identifier)
        urls = [
            f"https://steamcommunity.com/id/{encoded}/?xml=1",
            f"https://steamcommunity.com/id/{encoded}/",
        ]
    for url in urls:
        try:
            html = _download(url, timeout=6)[0].decode("utf-8", errors="ignore")
            patterns = [
                r"<avatarFull>\s*<!\[CDATA\[(.*?)\]\]>\s*</avatarFull>",
                r"<avatarFull>(.*?)</avatarFull>",
                r'property=[\"\']og:image[\"\'][^>]+content=[\"\']([^\"\']+)[\"\']',
                r'content=[\"\']([^\"\']+)[\"\'][^>]+property=[\"\']og:image[\"\']',
                r'"avatarfull"\s*:\s*"([^"]+)"',
                r'"avatarFull"\s*:\s*"([^"]+)"',
            ]
            for pattern in patterns:
                match = re.search(pattern, html, re.IGNORECASE | re.S)
                if match:
                    value = match.group(1).strip().replace("\\/", "/")
                    if value.startswith("http"):
                        return value
        except Exception:
            pass
    return None


def _search_profile_avatar(login):
    if not login:
        return None
    try:
        url = "https://steamcommunity.com/actions/Search?K=" + quote(login)
        html = _download(url, timeout=7)[0].decode("utf-8", errors="ignore")
        patterns = [
            r'href=[\"\'](?:https?://steamcommunity\.com)?/(profiles/[0-9]{15,}|id/[A-Za-z0-9_-]+)[\"\']',
            r'https?://steamcommunity\.com/(profiles/[0-9]{15,}|id/[A-Za-z0-9_-]+)',
        ]
        for pattern in patterns:
            match = re.search(pattern, html, re.IGNORECASE)
            if match:
                profile = match.group(1)
                return _steam_avatar_url(profile.split("/", 1)[1])
    except Exception:
        pass
    return None


def _read_loginusers(steam_exe):
    if not steam_exe:
        return []
    vdf = Path(steam_exe).resolve().parent / "config" / "loginusers.vdf"
    if not vdf.is_file():
        return []
    try:
        text = vdf.read_text(encoding="utf-8-sig", errors="replace")
    except OSError:
        return []
    accounts = []
    for match in re.finditer(r'"(\d{15,})"\s*\{(.*?)\n\s*\}', text, re.S):
        block = match.group(2)
        def get(key):
            m = re.search(rf'"{re.escape(key)}"\s+"([^\"]*)"', block, re.I)
            return m.group(1).strip() if m else ""
        accounts.append({"steam_id": match.group(1), "login": get("AccountName"), "name": get("PersonaName")})
    return accounts


def _local_avatar_candidates(steam_exe, steam_id):
    if not steam_exe or not steam_id:
        return []
    cache = Path(steam_exe).resolve().parent / "config" / "avatarcache"
    if not cache.is_dir():
        return []
    candidates = []
    names = [
        f"{steam_id}.png", f"{steam_id}.jpg", f"{steam_id}.jpeg",
        f"{steam_id}_full.png", f"{steam_id}_full.jpg", f"{steam_id}_full.jpeg",
        f"avatarcache_{steam_id}.png", f"avatarcache{steam_id}.png",
    ]
    for name in names:
        path = cache / name
        if path.is_file():
            candidates.append(path)
    return candidates


def _save_avatar_data(data, account, suffix=".jpg"):
    if not data:
        return ""
    AVATAR_DIR.mkdir(parents=True, exist_ok=True)
    safe = re.sub(r"[^a-zA-Z0-9_-]+", "_", account.steam_id or account.login or account.id)
    destination = AVATAR_DIR / f"steam_{safe}{suffix}"
    try:
        destination.write_bytes(data)
        return str(destination)
    except OSError:
        return ""


def _copy_local_avatar(path, account):
    try:
        AVATAR_DIR.mkdir(parents=True, exist_ok=True)
        suffix = path.suffix.lower() or ".png"
        safe = re.sub(r"[^a-zA-Z0-9_-]+", "_", account.steam_id or account.login or account.id)
        destination = AVATAR_DIR / f"steam_{safe}{suffix}"
        shutil.copy2(path, destination)
        return str(destination)
    except OSError:
        return ""


def fetch_profile_avatar(account, steam_exe=None):
    if account.avatar and Path(account.avatar).is_file():
        return account.avatar

    saved = _read_loginusers(steam_exe)
    login_norm = (account.login or "").strip().lower()
    for item in saved:
        if login_norm and item["login"].lower() == login_norm:
            if not account.steam_id:
                account.steam_id = item["steam_id"]
            if item["name"] and (not account.name or account.name == account.login):
                account.name = item["name"]
            break

    steam_id = str(account.steam_id or "").strip()
    for candidate in _local_avatar_candidates(steam_exe, steam_id):
        path = _copy_local_avatar(candidate, account)
        if path:
            return path

    if steam_id:
        for url in (
            f"https://steamloopback.host/avatarcache/{steam_id}.png",
            f"http://steamloopback.host/avatarcache/{steam_id}.png",
        ):
            try:
                data, content_type = _download(url, timeout=4)
                if data and len(data) > 32:
                    suffix = ".png" if "png" in content_type.lower() or url.endswith(".png") else ".jpg"
                    path = _save_avatar_data(data, account, suffix)
                    if path:
                        return path
            except Exception:
                pass

    avatar_url = _steam_avatar_url(steam_id)
    if not avatar_url and account.login:
        avatar_url = _steam_avatar_url(account.login)
    if not avatar_url and account.login:
        avatar_url = _search_profile_avatar(account.login)
    if not avatar_url:
        return ""

    try:
        data, content_type = _download(avatar_url, timeout=8)
        if not data:
            return ""
        suffix = ".png" if "png" in content_type.lower() else ".jpg"
        return _save_avatar_data(data, account, suffix)
    except Exception:
        return ""

import json
import shutil
from pathlib import Path
from datetime import datetime

from app.config import DATA_FILE, APP_DIR
from app.models.account import Account

LEGACY_FILE = APP_DIR / "steam_contas.txt"


class AccountStore:
    def __init__(self, path=DATA_FILE):
        self.path = Path(path)
        self.ensure_exists()
        self.migrate_legacy()

    def default_data(self):
        return {
            "accounts": [],
            "settings": {
                "view": "grid",
                "sort": "name_asc",
                "launch_mode": "online",
                "theme": "dark",
                "language": "pt-BR",
                "icon_size": 60,
            },
        }

    def ensure_exists(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self.write(self.default_data())

    def read(self):
        try:
            with self.path.open("r", encoding="utf-8") as f:
                data = json.load(f)
        except (OSError, json.JSONDecodeError) as exc:
            raise RuntimeError(f"Could not read:\n\n{self.path}\n\n{exc}") from exc

        if not isinstance(data, dict):
            data = self.default_data()

        data.setdefault("accounts", [])
        data.setdefault("settings", {})
        data["settings"].setdefault("view", "list")
        data["settings"].setdefault("sort", "name_asc")
        data["settings"].setdefault("launch_mode", "online")
        data["settings"].setdefault("theme", "dark")
        data["settings"].setdefault("language", "pt-BR")
        data["settings"].setdefault("icon_size", 60)
        return data

    def write(self, data):
        temp = self.path.with_suffix(".tmp")
        try:
            with temp.open("w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            temp.replace(self.path)
        except OSError as exc:
            if temp.exists():
                try:
                    temp.unlink()
                except OSError:
                    pass
            raise RuntimeError(f"Could not save:\n\n{self.path}\n\n{exc}") from exc

    def accounts(self):
        return [Account.from_dict(x) for x in self.read()["accounts"]]

    def settings(self):
        return self.read()["settings"]

    def save_accounts(self, accounts):
        data = self.read()
        data["accounts"] = [a.to_dict() for a in accounts]
        self.write(data)

    def save_settings(self, **settings):
        data = self.read()
        data["settings"].update(settings)
        self.write(data)

    def next_id(self, accounts):
        used = {a.id for a in accounts}
        i = 1
        while f"account_{i}" in used:
            i += 1
        return f"account_{i}"

    def add(self, name, login, steam_id="", note="No note", avatar=""):
        accounts = self.accounts()

        if any(a.login.lower() == login.lower() for a in accounts):
            raise ValueError(f'The account "{login}" is already registered.')

        account = Account(
            id=self.next_id(accounts),
            name=name.strip(),
            login=login.strip(),
            steam_id=steam_id.strip(),
            note=note.strip() or "No note",
            avatar=avatar,
        )
        accounts.append(account)
        self.save_accounts(accounts)
        return account

    def update(self, account_id, name, login, steam_id="", note="No note", avatar=""):
        accounts = self.accounts()
        target = next((a for a in accounts if a.id == account_id), None)

        if target is None:
            raise ValueError("The selected account was not found.")

        if any(a.id != account_id and a.login.lower() == login.lower() for a in accounts):
            raise ValueError(f'The account "{login}" is already registered.')

        target.name = name.strip()
        target.login = login.strip()
        target.steam_id = steam_id.strip()
        target.note = note.strip() or "No note"
        target.avatar = avatar
        self.save_accounts(accounts)

    def remove(self, account_id):
        accounts = self.accounts()
        target = next((a for a in accounts if a.id == account_id), None)

        if target is None:
            raise ValueError("The selected account was not found.")

        self.save_accounts([a for a in accounts if a.id != account_id])
        return target

    def migrate_legacy(self):
        if not LEGACY_FILE.exists():
            return

        try:
            if self.accounts():
                return
            text = LEGACY_FILE.read_text(encoding="utf-8-sig")
        except (OSError, UnicodeDecodeError):
            try:
                text = LEGACY_FILE.read_text(encoding="cp1252")
            except OSError:
                return

        accounts = []
        for line in text.splitlines():
            parts = line.strip().split("|", 2)
            if len(parts) < 2:
                continue

            try:
                int(parts[0].strip())
            except ValueError:
                continue

            login = parts[1].strip()
            if not login:
                continue

            note = parts[2].strip() if len(parts) > 2 else "No note"
            accounts.append(Account(
                id=f"account_{len(accounts) + 1}",
                name=login,
                login=login,
                note=note or "No note",
            ))

        if accounts:
            self.save_accounts(accounts)
            try:
                shutil.move(LEGACY_FILE, LEGACY_FILE.with_suffix(".txt.backup"))
            except OSError:
                pass

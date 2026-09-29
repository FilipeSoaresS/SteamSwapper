from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class Account:
    id: str
    name: str
    login: str
    steam_id: str = ""
    note: str = "No note"
    avatar: str = ""
    added_at: str = ""

    def __post_init__(self):
        if not self.added_at:
            self.added_at = datetime.now().isoformat(timespec="seconds")

    def to_dict(self):
        return asdict(self)

    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data.get("id", ""),
            name=data.get("name", data.get("login", "")),
            login=data.get("login", ""),
            steam_id=data.get("steam_id", ""),
            note=data.get("note", "No note"),
            avatar=data.get("avatar", ""),
            added_at=data.get("added_at", ""),
        )

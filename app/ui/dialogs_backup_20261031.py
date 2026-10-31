import tkinter as tk
from tkinter import filedialog
from pathlib import Path

from app.config import get_theme
from app.ui.widgets import show_error, RoundedCard, PillButton
from app.utils.images import copy_avatar, load_photo
from app.utils.windows import set_title_bar_theme


class ModalBase(tk.Toplevel):
    def __init__(self, parent, title, width=520, height=420):
        super().__init__(parent)
        self.steam_theme = getattr(parent, "steam_theme", "dark")
        self.t = get_theme(self.steam_theme)
        self.title(title)
        self.configure(bg=self.t["BG"])
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        try:
            from app.config import ICON_FILE
            if ICON_FILE.exists():
                self.iconbitmap(default=str(ICON_FILE))
        except Exception:
            pass
        set_title_bar_theme(self, self.steam_theme == "dark")
        self.geometry(f"{width}x{height}")
        self.result = None
        self.bind("<Escape>", lambda e: self.cancel())
        self.after(50, lambda: self._center(parent))

    def _center(self, parent):
        try:
            parent.update_idletasks()
            x = parent.winfo_rootx() + (parent.winfo_width() - self.winfo_width()) // 2
            y = parent.winfo_rooty() + (parent.winfo_height() - self.winfo_height()) // 2
            self.geometry(f"+{max(0, x)}+{max(0, y)}")
        except tk.TclError:
            pass

    def cancel(self):
        self.result = None
        self.destroy()


class SwitchConfirmDialog(ModalBase):
    def __init__(self, parent, account, mode):
        self.account = account
        self.mode = mode
        super().__init__(parent, "Switch Steam account", width=560, height=430)
        self.result = False
        self.build()

    def build(self):
        t = self.t
        outer = tk.Frame(self, bg=t["BG"], padx=28, pady=24)
        outer.pack(fill="both", expand=True)

        top = tk.Frame(outer, bg=t["BG"])
        top.pack(fill="x")
        tk.Label(top, text="SWITCH STEAM ACCOUNT", bg=t["BG"], fg=t["TEXT"],
                 font=("Segoe UI", 16, "bold")).pack(side="left")
        tk.Label(top, text="CONFIRM ACTION", bg=t["BG"], fg=t["STEAM_BLUE_HOVER"],
                 font=("Segoe UI", 7, "bold")).pack(side="right", pady=5)

        profile = tk.Frame(outer, bg=t["PANEL"], highlightthickness=1, highlightbackground=t["BORDER"], height=120)
        profile.pack(fill="x", pady=(22, 16))
        profile.pack_propagate(False)
        image = load_photo(self.account.avatar, 78)
        if image:
            self.avatar_image = image
            tk.Label(profile, image=image, bg=t["PANEL"], bd=0).pack(side="left", padx=(18, 15), pady=18)
        info = tk.Frame(profile, bg=t["PANEL"])
        info.pack(side="left", fill="both", expand=True, pady=18)
        tk.Label(info, text=self.account.name, bg=t["PANEL"], fg=t["TEXT"],
                 font=("Segoe UI", 13, "bold")).pack(anchor="w")
        tk.Label(info, text=self.account.login, bg=t["PANEL"], fg=t["STEAM_BLUE_HOVER"],
                 font=("Segoe UI", 9)).pack(anchor="w", pady=(3, 0))
        tk.Label(info, text=self.account.note, bg=t["PANEL"], fg=t["MUTED"],
                 font=("Segoe UI", 8)).pack(anchor="w", pady=(4, 0))

        details = tk.Frame(outer, bg=t["BG"])
        details.pack(fill="x")
        self.detail_row(details, "LAUNCH MODE", self.mode.upper())
        self.detail_row(details, "ACTION", "RESTART STEAM")
        tk.Label(outer, text="Steam will be closed and restarted with the selected account.",
                 bg=t["BG"], fg=t["MUTED"], font=("Segoe UI", 8)).pack(anchor="w", pady=(15, 0))

        buttons = tk.Frame(outer, bg=t["BG"])
        buttons.pack(side="bottom", fill="x")
        PillButton(buttons, "CANCEL", self.cancel, primary=False, width=104).pack(side="right", padx=(8, 0))
        PillButton(buttons, "SWITCH", self.confirm, primary=True, width=104).pack(side="right")
        self.bind("<Return>", lambda e: self.confirm())

    def detail_row(self, parent, label, value):
        t = self.t
        row = tk.Frame(parent, bg=t["BG"])
        row.pack(fill="x", pady=2)
        tk.Label(row, text=label, bg=t["BG"], fg=t["MUTED"], width=15, anchor="w",
                 font=("Segoe UI", 7, "bold")).pack(side="left")
        tk.Label(row, text=value, bg=t["BG"], fg=t["TEXT"], anchor="w",
                 font=("Segoe UI", 8, "bold")).pack(side="left")

    def confirm(self):
        self.result = True
        self.destroy()


class AccountDialog(ModalBase):
    def __init__(self, parent, existing=None):
        self.existing = existing
        self.avatar = existing.avatar if existing else ""
        super().__init__(parent, "Edit Steam Account" if existing else "Add Steam Account", width=540, height=590)
        self.build()

    def build(self):
        t = self.t
        frame = tk.Frame(self, bg=t["BG"], padx=28, pady=25)
        frame.pack(fill="both", expand=True)
        tk.Label(frame, text="EDIT ACCOUNT" if self.existing else "ADD STEAM ACCOUNT", bg=t["BG"], fg=t["TEXT"],
                 font=("Segoe UI", 17, "bold")).pack(anchor="w")
        tk.Label(frame, text="Keep the profile information used by Steam Swapper.", bg=t["BG"], fg=t["MUTED"],
                 font=("Segoe UI", 8)).pack(anchor="w", pady=(3, 20))

        self.name = self.entry(frame, "DISPLAY NAME", self.existing.name if self.existing else "")
        self.login = self.entry(frame, "STEAM LOGIN", self.existing.login if self.existing else "")
        self.steam_id = self.entry(frame, "STEAM ID64 (OPTIONAL)", self.existing.steam_id if self.existing else "")
        self.note = self.entry(frame, "DESCRIPTION", self.existing.note if self.existing else "")

        avatar_row = tk.Frame(frame, bg=t["BG"])
        avatar_row.pack(fill="x", pady=(2, 20))
        PillButton(avatar_row, "CHOOSE AVATAR", self.choose_avatar, primary=False, width=138).pack(side="left")
        self.avatar_text = tk.Label(avatar_row, text=Path(self.avatar).name if self.avatar else "Automatic Steam avatar",
                                    bg=t["BG"], fg=t["MUTED"], font=("Segoe UI", 8))
        self.avatar_text.pack(side="left", padx=10)

        buttons = tk.Frame(frame, bg=t["BG"])
        buttons.pack(side="bottom", fill="x")
        PillButton(buttons, "CANCEL", self.cancel, primary=False, width=104).pack(side="right", padx=(8, 0))
        PillButton(buttons, "SAVE ACCOUNT", self.save, primary=True, width=132).pack(side="right")

    def entry(self, parent, label, value):
        t = self.t
        tk.Label(parent, text=label, bg=t["BG"], fg=t["MUTED"], font=("Segoe UI", 7, "bold")).pack(anchor="w", pady=(0, 5))
        var = tk.StringVar(value=value)
        tk.Entry(parent, textvariable=var, bg=t["PANEL"], fg=t["TEXT"], insertbackground=t["TEXT"],
                 relief="flat", bd=0, highlightthickness=1, highlightbackground=t["BORDER"],
                 highlightcolor=t["STEAM_BLUE"], font=("Segoe UI", 10)).pack(fill="x", ipady=8, pady=(0, 13))
        return var

    def choose_avatar(self):
        path = filedialog.askopenfilename(parent=self, title="Choose avatar",
                                          filetypes=[("Image files", "*.png;*.gif;*.jpg;*.jpeg;*.webp"), ("All files", "*.*")])
        if not path:
            return
        try:
            self.avatar = copy_avatar(path)
            self.avatar_text.configure(text=Path(self.avatar).name)
        except OSError as exc:
            show_error(self, "Avatar error", f"Could not copy avatar:\n\n{exc}")

    def save(self):
        name = self.name.get().strip()
        login = self.login.get().strip()
        if not name:
            show_error(self, "Missing display name", "Enter a display name.")
            return
        if not login:
            show_error(self, "Missing Steam login", "Enter the Steam login.")
            return
        self.result = {
            "name": name,
            "login": login,
            "steam_id": self.steam_id.get().strip(),
            "note": self.note.get().strip() or "No note",
            "avatar": self.avatar,
        }
        self.destroy()

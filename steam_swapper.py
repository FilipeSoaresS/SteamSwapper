from __future__ import annotations

import ctypes
import os
import re
import subprocess
import sys
import time
from pathlib import Path

import tkinter as tk
from tkinter import messagebox, ttk


# ============================================================
# APPLICATION
# ============================================================

APP_NAME = "Steam Swapper"
DATA_FILENAME = "steam_contas.txt"


# ============================================================
# PATHS
# ============================================================

def application_directory() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent

    return Path(__file__).resolve().parent


def resource_directory() -> Path:
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS)

    return Path(__file__).resolve().parent


APP_DIR = application_directory()
RESOURCE_DIR = resource_directory()

DATA_FILE = APP_DIR / DATA_FILENAME

IMG_DIR = RESOURCE_DIR / "img"

# Logo shown inside the application
LOGO_FILE = IMG_DIR / "2.png"

# Windows title bar / EXE icon
ICON_FILE = IMG_DIR / "2.ico"


# ============================================================
# COLORS
# ============================================================

BG = "#0b0d10"

PANEL = "#12171d"
PANEL_ALT = "#1a2027"

TEXT = "#f4f4f4"
MUTED = "#8b949e"

BLUE_DARK = "#0875ff"

ORANGE = "#ff9418"
ORANGE_HOVER = "#ffad47"

BORDER = "#242a31"

# Custom scrollbar
SCROLL_TRACK = "#090b0e"
SCROLL_THUMB = "#252b32"
SCROLL_THUMB_HOVER = "#353d46"


# ============================================================
# WINDOWS DARK TITLE BAR
# ============================================================

def enable_dark_title_bar(window):

    if os.name != "nt":
        return

    try:
        window.update_idletasks()

        hwnd = ctypes.windll.user32.GetParent(
            window.winfo_id()
        )

        enabled = ctypes.c_int(1)

        for attribute in (20, 19):

            try:
                result = ctypes.windll.dwmapi.DwmSetWindowAttribute(
                    hwnd,
                    attribute,
                    ctypes.byref(enabled),
                    ctypes.sizeof(enabled),
                )

                if result == 0:
                    break

            except Exception:
                pass

    except Exception:
        pass


# ============================================================
# CUSTOM DARK ROUNDED SCROLLBAR
# ============================================================

class RoundedScrollbar(tk.Canvas):

    def __init__(
        self,
        parent,
        command=None,
        width=14,
        bg=SCROLL_TRACK,
        thumb_color=SCROLL_THUMB,
        hover_color=SCROLL_THUMB_HOVER,
        **kwargs,
    ):

        super().__init__(
            parent,
            width=width,
            bg=bg,
            highlightthickness=0,
            bd=0,
            relief="flat",
            **kwargs,
        )

        self.command = command

        self.thumb_color = thumb_color
        self.hover_color = hover_color

        self.first = 0.0
        self.last = 1.0

        self.dragging = False
        self.drag_offset = 0

        self.thumb_id = None

        self.bind(
            "<Configure>",
            self._redraw
        )

        self.bind(
            "<Button-1>",
            self._mouse_down
        )

        self.bind(
            "<B1-Motion>",
            self._mouse_drag
        )

        self.bind(
            "<ButtonRelease-1>",
            self._mouse_up
        )

        self.bind(
            "<Enter>",
            self._hover_on
        )

        self.bind(
            "<Leave>",
            self._hover_off
        )


    # --------------------------------------------------------
    # TREEVIEW CALLBACK
    # --------------------------------------------------------

    def set(self, first, last):

        self.first = float(first)
        self.last = float(last)

        self._redraw()


    # --------------------------------------------------------
    # DRAW ROUNDED RECTANGLE
    # --------------------------------------------------------

    def _rounded_rectangle(
        self,
        x1,
        y1,
        x2,
        y2,
        radius,
        **kwargs,
    ):

        radius = min(
            radius,
            (x2 - x1) / 2,
            (y2 - y1) / 2,
        )

        points = [
            x1 + radius, y1,
            x2 - radius, y1,

            x2, y1,
            x2, y1 + radius,

            x2, y2 - radius,
            x2, y2,

            x2 - radius, y2,
            x1 + radius, y2,

            x1, y2,
            x1, y2 - radius,

            x1, y1 + radius,
            x1, y1,
        ]

        return self.create_polygon(
            points,
            smooth=True,
            splinesteps=36,
            **kwargs,
        )


    # --------------------------------------------------------
    # REDRAW
    # --------------------------------------------------------

    def _redraw(self, event=None):

        self.delete("thumb")

        height = self.winfo_height()
        width = self.winfo_width()

        if height <= 1:
            return

        # If all content is visible, keep the scrollbar minimal
        if self.first <= 0 and self.last >= 1:
            return

        top = self.first * height
        bottom = self.last * height

        minimum_thumb = 34

        if bottom - top < minimum_thumb:
            center = (top + bottom) / 2
            top = center - minimum_thumb / 2
            bottom = center + minimum_thumb / 2

        if top < 3:
            top = 3

        if bottom > height - 3:
            bottom = height - 3

        x1 = 3
        x2 = width - 3

        self.thumb_id = self._rounded_rectangle(
            x1,
            top,
            x2,
            bottom,
            radius=(x2 - x1) / 2,
            fill=self.thumb_color,
            outline="",
            tags="thumb",
        )


    # --------------------------------------------------------
    # HIT TEST
    # --------------------------------------------------------

    def _thumb_bounds(self):

        height = self.winfo_height()

        top = self.first * height
        bottom = self.last * height

        minimum_thumb = 34

        if bottom - top < minimum_thumb:

            center = (
                top + bottom
            ) / 2

            top = (
                center
                - minimum_thumb / 2
            )

            bottom = (
                center
                + minimum_thumb / 2
            )

        top = max(3, top)

        bottom = min(
            height - 3,
            bottom
        )

        return top, bottom


    # --------------------------------------------------------
    # MOUSE DOWN
    # --------------------------------------------------------

    def _mouse_down(self, event):

        top, bottom = (
            self._thumb_bounds()
        )

        if top <= event.y <= bottom:

            self.dragging = True

            self.drag_offset = (
                event.y - top
            )

        else:

            if not self.command:
                return

            if event.y < top:

                self.command(
                    "scroll",
                    -1,
                    "pages",
                )

            else:

                self.command(
                    "scroll",
                    1,
                    "pages",
                )


    # --------------------------------------------------------
    # DRAG
    # --------------------------------------------------------

    def _mouse_drag(self, event):

        if not self.dragging:
            return

        if not self.command:
            return

        height = self.winfo_height()

        top, bottom = (
            self._thumb_bounds()
        )

        thumb_height = (
            bottom - top
        )

        usable = (
            height
            - thumb_height
            - 6
        )

        if usable <= 0:
            return

        new_top = (
            event.y
            - self.drag_offset
            - 3
        )

        fraction = (
            new_top / usable
        )

        fraction = max(
            0.0,
            min(
                1.0,
                fraction,
            ),
        )

        self.command(
            "moveto",
            fraction,
        )


    # --------------------------------------------------------
    # MOUSE UP
    # --------------------------------------------------------

    def _mouse_up(self, event):

        self.dragging = False


    # --------------------------------------------------------
    # HOVER
    # --------------------------------------------------------

    def _hover_on(self, event):

        if self.thumb_id:

            self.itemconfigure(
                "thumb",
                fill=self.hover_color,
            )


    def _hover_off(self, event):

        if self.thumb_id:

            self.itemconfigure(
                "thumb",
                fill=self.thumb_color,
            )


# ============================================================
# STEAM DETECTION
# ============================================================

def find_steam_executable() -> Path | None:

    if os.name != "nt":
        return None

    try:
        import winreg

        registry_locations = [

            (
                winreg.HKEY_CURRENT_USER,
                r"Software\Valve\Steam",
                "SteamExe",
            ),

            (
                winreg.HKEY_CURRENT_USER,
                r"Software\Valve\Steam",
                "SteamPath",
            ),

            (
                winreg.HKEY_LOCAL_MACHINE,
                r"SOFTWARE\WOW6432Node\Valve\Steam",
                "InstallPath",
            ),

            (
                winreg.HKEY_LOCAL_MACHINE,
                r"SOFTWARE\Valve\Steam",
                "InstallPath",
            ),
        ]

        for hive, key_path, value_name in registry_locations:

            try:

                with winreg.OpenKey(
                    hive,
                    key_path,
                ) as key:

                    value, _ = winreg.QueryValueEx(
                        key,
                        value_name,
                    )

                    candidate = Path(
                        str(value).replace(
                            "/",
                            "\\",
                        )
                    )

                    if candidate.is_dir():

                        candidate = (
                            candidate
                            / "steam.exe"
                        )

                    if candidate.is_file():

                        return candidate

            except (
                FileNotFoundError,
                OSError,
            ):

                pass

    except Exception:

        pass


    candidates = [

        Path(
            os.environ.get(
                "ProgramFiles(x86)",
                r"C:\Program Files (x86)",
            )
        )
        / "Steam"
        / "steam.exe",

        Path(
            os.environ.get(
                "ProgramFiles",
                r"C:\Program Files",
            )
        )
        / "Steam"
        / "steam.exe",

        Path(
            r"C:\Steam\steam.exe"
        ),
    ]


    for candidate in candidates:

        if candidate.is_file():

            return candidate


    return None


# ============================================================
# VALIDATION
# ============================================================

def validate_login(
    login: str,
) -> tuple[bool, str]:

    login = login.strip()


    if not login:

        return (
            False,
            "Steam login cannot be empty.",
        )


    if "|" in login:

        return (
            False,
            'The "|" character cannot be used in the login.',
        )


    if "\n" in login or "\r" in login:

        return (
            False,
            "The Steam login contains invalid characters.",
        )


    return True, ""


def validate_note(
    note: str,
) -> tuple[bool, str]:

    if "|" in note:

        return (
            False,
            'The "|" character cannot be used in the note.',
        )


    if "\n" in note or "\r" in note:

        return (
            False,
            "The note contains invalid characters.",
        )


    return True, ""


# ============================================================
# DATABASE
# ============================================================

class AccountStore:

    def __init__(
        self,
        path: Path,
    ):

        self.path = path

        self.ensure_exists()


    # --------------------------------------------------------
    # CREATE
    # --------------------------------------------------------

    def ensure_exists(self):

        try:

            self.path.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

            self.path.touch(
                exist_ok=True,
            )

        except OSError as exc:

            raise RuntimeError(
                f"Could not create the database:\n\n"
                f"{self.path}\n\n"
                f"{exc}"
            ) from exc


    # --------------------------------------------------------
    # LOAD
    # --------------------------------------------------------

    def load(self) -> list[dict]:

        accounts = []


        try:

            try:

                text = self.path.read_text(
                    encoding="utf-8-sig"
                )

            except UnicodeDecodeError:

                text = self.path.read_text(
                    encoding="cp1252"
                )

        except OSError as exc:

            raise RuntimeError(
                f"Could not read:\n\n"
                f"{self.path}\n\n"
                f"{exc}"
            ) from exc


        for line in text.splitlines():

            line = line.strip()


            if not line:

                continue


            parts = line.split(
                "|",
                2,
            )


            if len(parts) < 2:

                continue


            number_text = (
                parts[0].strip()
            )

            login = (
                parts[1].strip()
            )


            note = (

                parts[2].strip()

                if len(parts) >= 3

                else "No note"
            )


            try:

                number = int(
                    number_text
                )

            except ValueError:

                continue


            if (
                number < 0
                or number > 100
            ):

                continue


            if not login:

                continue


            accounts.append(
                {
                    "number": number,
                    "login": login,
                    "note": (
                        note
                        or "No note"
                    ),
                }
            )


        unique = {}


        for account in accounts:

            unique[
                account["number"]
            ] = account


        accounts = list(
            unique.values()
        )


        accounts.sort(
            key=lambda account:
            account["number"]
        )


        return accounts


    # --------------------------------------------------------
    # SAVE
    # --------------------------------------------------------

    def save(
        self,
        accounts: list[dict],
    ):

        accounts = sorted(
            accounts,
            key=lambda account:
            account["number"],
        )


        lines = []


        for account in accounts:

            number = int(
                account["number"]
            )

            login = (
                account["login"]
                .strip()
            )

            note = (
                account["note"]
                .strip()
                or "No note"
            )


            lines.append(
                f"{number}|{login}|{note}"
            )


        content = "\n".join(
            lines
        )


        if content:

            content += "\n"


        temp_file = (
            self.path.with_suffix(
                ".tmp"
            )
        )


        try:

            temp_file.write_text(
                content,
                encoding="utf-8",
            )

            temp_file.replace(
                self.path
            )

        except OSError as exc:

            try:

                if temp_file.exists():

                    temp_file.unlink()

            except OSError:

                pass


            raise RuntimeError(
                f"Could not save:\n\n"
                f"{self.path}\n\n"
                f"{exc}"
            ) from exc


    # --------------------------------------------------------
    # ADD
    # --------------------------------------------------------

    def add(
        self,
        number: int,
        login: str,
        note: str,
    ):

        accounts = self.load()


        for account in accounts:

            if (
                account["number"]
                == number
            ):

                raise ValueError(
                    f"Number {number} is already being used."
                )


            if (
                account["login"].lower()
                == login.lower()
            ):

                raise ValueError(
                    f'The account "{login}" is already registered.'
                )


        accounts.append(
            {
                "number": number,
                "login": login.strip(),
                "note": (
                    note.strip()
                    or "No note"
                ),
            }
        )


        self.save(
            accounts
        )


    # --------------------------------------------------------
    # REMOVE
    # --------------------------------------------------------

    def remove(
        self,
        number: int,
    ):

        accounts = self.load()


        filtered = [

            account

            for account in accounts

            if account["number"]
            != number
        ]


        if (
            len(filtered)
            == len(accounts)
        ):

            raise ValueError(
                f"Account number {number} was not found."
            )


        self.save(
            filtered
        )


    # --------------------------------------------------------
    # UPDATE
    # --------------------------------------------------------

    def update(
        self,
        old_number: int,
        new_number: int,
        login: str,
        note: str,
    ):

        accounts = self.load()

        target = None


        for account in accounts:

            if (
                account["number"]
                == old_number
            ):

                target = account

                break


        if target is None:

            raise ValueError(
                f"Account number {old_number} was not found."
            )


        for account in accounts:

            if (
                account["number"]
                == new_number
                and
                old_number
                != new_number
            ):

                raise ValueError(
                    f"Number {new_number} is already being used."
                )


            if (
                account["number"]
                != old_number
                and
                account["login"].lower()
                == login.lower()
            ):

                raise ValueError(
                    f'The account "{login}" is already registered.'
                )


        target["number"] = (
            new_number
        )

        target["login"] = (
            login.strip()
        )

        target["note"] = (
            note.strip()
            or "No note"
        )


        self.save(
            accounts
        )


# ============================================================
# STEAM PROCESS
# ============================================================

def steam_process_running() -> bool:

    if os.name != "nt":

        return False


    try:

        result = subprocess.run(
            [
                "tasklist",
                "/FI",
                "IMAGENAME eq steam.exe",
            ],
            capture_output=True,
            text=True,
            creationflags=(
                subprocess.CREATE_NO_WINDOW
            ),
            check=False,
        )


        return (
            "steam.exe"
            in result.stdout.lower()
        )


    except OSError:

        return False


# ============================================================
# CLOSE STEAM
# ============================================================

def close_steam(
    steam_exe: Path,
) -> bool:

    if os.name != "nt":

        return False


    no_window = (
        subprocess.CREATE_NO_WINDOW
    )


    # --------------------------------------------------------
    # Graceful shutdown
    # --------------------------------------------------------

    try:

        subprocess.Popen(
            [
                str(steam_exe),
                "-shutdown",
            ],
            stdout=(
                subprocess.DEVNULL
            ),
            stderr=(
                subprocess.DEVNULL
            ),
            creationflags=no_window,
        )

    except OSError:

        pass


    # --------------------------------------------------------
    # Wait
    # --------------------------------------------------------

    for _ in range(16):

        if not steam_process_running():

            return True

        time.sleep(
            0.5
        )


    # --------------------------------------------------------
    # Force close
    # --------------------------------------------------------

    processes = [
        "steam.exe",
        "steamwebhelper.exe",
        "gameoverlayui.exe",
    ]


    for process in processes:

        try:

            subprocess.run(
                [
                    "taskkill",
                    "/F",
                    "/IM",
                    process,
                ],
                stdout=(
                    subprocess.DEVNULL
                ),
                stderr=(
                    subprocess.DEVNULL
                ),
                creationflags=no_window,
                check=False,
            )

        except OSError:

            pass


    time.sleep(
        1.5
    )


    return (
        not steam_process_running()
    )


# ============================================================
# START STEAM
# ============================================================

def launch_steam(
    steam_exe: Path,
    login: str,
):

    subprocess.Popen(
        [
            str(steam_exe),
            "-login",
            login,
        ],
        cwd=str(
            steam_exe.parent
        ),
        stdout=(
            subprocess.DEVNULL
        ),
        stderr=(
            subprocess.DEVNULL
        ),
    )


# ============================================================
# ACCOUNT DIALOG
# ============================================================

class AccountDialog(
    tk.Toplevel
):

    def __init__(
        self,
        parent,
        title,
        existing=None,
    ):

        super().__init__(
            parent
        )


        self.title(
            title
        )


        self.configure(
            bg=BG
        )


        self.resizable(
            False,
            False,
        )


        self.result = None


        self.transient(
            parent
        )


        self.grab_set()


        # ----------------------------------------------------
        # ICON
        # ----------------------------------------------------

        try:

            if ICON_FILE.exists():

                self.iconbitmap(
                    default=str(
                        ICON_FILE
                    )
                )

        except Exception:

            pass


        # ----------------------------------------------------
        # DARK TITLE BAR
        # ----------------------------------------------------

        enable_dark_title_bar(
            self
        )


        frame = tk.Frame(
            self,
            bg=BG,
            padx=25,
            pady=25,
        )


        frame.pack(
            fill="both",
            expand=True,
        )


        # ----------------------------------------------------
        # NUMBER
        # ----------------------------------------------------

        tk.Label(
            frame,
            text=(
                "Account number (0 - 100)"
            ),
            bg=BG,
            fg=TEXT,
            font=(
                "Segoe UI",
                10,
                "bold",
            ),
        ).pack(
            anchor="w",
            pady=(0, 5),
        )


        self.number_var = (
            tk.StringVar(
                value=(
                    str(
                        existing[
                            "number"
                        ]
                    )
                    if existing
                    else ""
                )
            )
        )


        self.number_entry = (
            tk.Entry(
                frame,
                textvariable=(
                    self.number_var
                ),
                bg=PANEL,
                fg=TEXT,
                insertbackground=TEXT,
                selectbackground=BLUE_DARK,
                selectforeground="#ffffff",
                relief="flat",
                bd=0,
                highlightthickness=0,
                font=(
                    "Segoe UI",
                    11,
                ),
            )
        )


        self.number_entry.pack(
            fill="x",
            ipady=7,
            pady=(0, 15),
        )


        # ----------------------------------------------------
        # LOGIN
        # ----------------------------------------------------

        tk.Label(
            frame,
            text="Steam Login",
            bg=BG,
            fg=TEXT,
            font=(
                "Segoe UI",
                10,
                "bold",
            ),
        ).pack(
            anchor="w",
            pady=(0, 5),
        )


        self.login_var = (
            tk.StringVar(
                value=(
                    existing[
                        "login"
                    ]
                    if existing
                    else ""
                )
            )
        )


        self.login_entry = (
            tk.Entry(
                frame,
                textvariable=(
                    self.login_var
                ),
                bg=PANEL,
                fg=TEXT,
                insertbackground=TEXT,
                selectbackground=BLUE_DARK,
                selectforeground="#ffffff",
                relief="flat",
                bd=0,
                highlightthickness=0,
                font=(
                    "Segoe UI",
                    11,
                ),
            )
        )


        self.login_entry.pack(
            fill="x",
            ipady=7,
            pady=(0, 15),
        )


        # ----------------------------------------------------
        # NOTE
        # ----------------------------------------------------

        tk.Label(
            frame,
            text="Note",
            bg=BG,
            fg=TEXT,
            font=(
                "Segoe UI",
                10,
                "bold",
            ),
        ).pack(
            anchor="w",
            pady=(0, 5),
        )


        self.note_var = (
            tk.StringVar(
                value=(
                    existing[
                        "note"
                    ]
                    if existing
                    else ""
                )
            )
        )


        self.note_entry = (
            tk.Entry(
                frame,
                textvariable=(
                    self.note_var
                ),
                bg=PANEL,
                fg=TEXT,
                insertbackground=TEXT,
                selectbackground=BLUE_DARK,
                selectforeground="#ffffff",
                relief="flat",
                bd=0,
                highlightthickness=0,
                font=(
                    "Segoe UI",
                    11,
                ),
            )
        )


        self.note_entry.pack(
            fill="x",
            ipady=7,
            pady=(0, 20),
        )


        # ----------------------------------------------------
        # BUTTONS
        # ----------------------------------------------------

        buttons = tk.Frame(
            frame,
            bg=BG,
        )


        buttons.pack(
            fill="x"
        )


        cancel = tk.Button(
            buttons,
            text="Cancel",
            command=self.destroy,
            bg=PANEL_ALT,
            fg=TEXT,
            activebackground=BORDER,
            activeforeground=TEXT,
            relief="flat",
            bd=0,
            highlightthickness=0,
            cursor="hand2",
            padx=18,
            pady=8,
        )


        cancel.pack(
            side="right",
            padx=(8, 0),
        )


        save = tk.Button(
            buttons,
            text="Save",
            command=(
                self.save_account
            ),
            bg=ORANGE,
            fg="#000000",
            activebackground=(
                ORANGE_HOVER
            ),
            activeforeground=(
                "#000000"
            ),
            relief="flat",
            bd=0,
            highlightthickness=0,
            cursor="hand2",
            padx=22,
            pady=8,
            font=(
                "Segoe UI",
                9,
                "bold",
            ),
        )


        save.pack(
            side="right"
        )


        self.bind(
            "<Return>",
            lambda event:
            self.save_account(),
        )


        self.bind(
            "<Escape>",
            lambda event:
            self.destroy(),
        )


        if existing:

            self.login_entry.focus_set()

        else:

            self.number_entry.focus_set()


        self.after(
            100,
            lambda:
            enable_dark_title_bar(
                self
            ),
        )


    # --------------------------------------------------------
    # SAVE
    # --------------------------------------------------------

    def save_account(
        self,
    ):

        number_text = (
            self.number_var
            .get()
            .strip()
        )


        login = (
            self.login_var
            .get()
            .strip()
        )


        note = (
            self.note_var
            .get()
            .strip()
            or "No note"
        )


        if not re.fullmatch(
            r"\d{1,3}",
            number_text,
        ):

            messagebox.showerror(
                APP_NAME,
                "Enter a number between 0 and 100.",
                parent=self,
            )

            return


        number = int(
            number_text
        )


        if (
            number < 0
            or number > 100
        ):

            messagebox.showerror(
                APP_NAME,
                "Account number must be between 0 and 100.",
                parent=self,
            )

            return


        ok, error = (
            validate_login(
                login
            )
        )


        if not ok:

            messagebox.showerror(
                APP_NAME,
                error,
                parent=self,
            )

            return


        ok, error = (
            validate_note(
                note
            )
        )


        if not ok:

            messagebox.showerror(
                APP_NAME,
                error,
                parent=self,
            )

            return


        self.result = (
            number,
            login,
            note,
        )


        self.destroy()


# ============================================================
# MAIN APP
# ============================================================

class SteamSwapperApp:

    def __init__(
        self,
        root,
    ):

        self.root = root


        # ----------------------------------------------------
        # WINDOW
        # ----------------------------------------------------

        self.root.title(
            APP_NAME
        )


        self.root.geometry(
            "900x650"
        )


        self.root.minsize(
            760,
            560,
        )


        self.root.configure(
            bg=BG
        )


        # ----------------------------------------------------
        # ICON
        # ----------------------------------------------------

        self.apply_window_icon()


        # ----------------------------------------------------
        # DARK TITLE BAR
        # ----------------------------------------------------

        enable_dark_title_bar(
            self.root
        )


        # ----------------------------------------------------
        # DATABASE
        # ----------------------------------------------------

        self.store = (
            AccountStore(
                DATA_FILE
            )
        )


        # ----------------------------------------------------
        # STEAM
        # ----------------------------------------------------

        self.steam_exe = (
            find_steam_executable()
        )


        # ----------------------------------------------------
        # LOGO
        # ----------------------------------------------------

        self.logo_image = None


        # ----------------------------------------------------
        # UI
        # ----------------------------------------------------

        self.configure_styles()

        self.build_ui()

        self.refresh()


        self.root.after(
            100,
            lambda:
            enable_dark_title_bar(
                self.root
            ),
        )


        if self.steam_exe is None:

            self.root.after(
                300,
                self.warn_steam_missing,
            )


    # ========================================================
    # WINDOW ICON
    # ========================================================

    def apply_window_icon(
        self,
    ):

        try:

            if ICON_FILE.exists():

                self.root.iconbitmap(
                    default=str(
                        ICON_FILE
                    )
                )

        except Exception as exc:

            print(
                f"Could not load window icon: {exc}"
            )


    # ========================================================
    # LOAD LOGO
    # ========================================================

    def load_logo(
        self,
    ):

        if not LOGO_FILE.exists():

            return None


        try:

            image = (
                tk.PhotoImage(
                    file=str(
                        LOGO_FILE
                    )
                )
            )


            max_size = 145


            width = (
                image.width()
            )

            height = (
                image.height()
            )


            biggest = max(
                width,
                height,
            )


            if biggest > max_size:

                factor = (
                    biggest
                    + max_size
                    - 1
                ) // max_size


                image = (
                    image.subsample(
                        factor,
                        factor,
                    )
                )


            return image


        except tk.TclError:

            return None


    # ========================================================
    # STYLES
    # ========================================================

    def configure_styles(
        self,
    ):

        style = ttk.Style()


        style.theme_use(
            "clam"
        )


        # ----------------------------------------------------
        # IMPORTANT:
        #
        # borderwidth=0
        # relief=flat
        #
        # removes the bright/white Treeview border.
        # ----------------------------------------------------

        style.configure(
            "Dark.Treeview",
            background=PANEL,
            fieldbackground=PANEL,
            foreground=TEXT,

            borderwidth=0,
            relief="flat",

            rowheight=36,

            font=(
                "Segoe UI",
                10,
            ),
        )


        style.map(
            "Dark.Treeview",
            background=[
                (
                    "selected",
                    BLUE_DARK,
                )
            ],
            foreground=[
                (
                    "selected",
                    "#ffffff",
                )
            ],
        )


        # ----------------------------------------------------
        # HEADER
        # ----------------------------------------------------

        style.configure(
            "Dark.Treeview.Heading",
            background=PANEL_ALT,
            foreground=TEXT,

            borderwidth=0,
            relief="flat",

            padding=10,

            font=(
                "Segoe UI",
                9,
                "bold",
            ),
        )


        style.map(
            "Dark.Treeview.Heading",
            background=[
                (
                    "active",
                    PANEL_ALT,
                )
            ],
        )


        # ----------------------------------------------------
        # Remove Treeview layout border
        # ----------------------------------------------------

        try:

            style.layout(
                "Dark.Treeview",
                [
                    (
                        "Treeview.treearea",
                        {
                            "sticky": "nswe"
                        },
                    )
                ],
            )

        except tk.TclError:

            pass


    # ========================================================
    # BUILD UI
    # ========================================================

    def build_ui(
        self,
    ):

        outer = tk.Frame(
            self.root,
            bg=BG,
            padx=25,
            pady=20,

            bd=0,
            highlightthickness=0,
        )


        outer.pack(
            fill="both",
            expand=True,
        )


        # ----------------------------------------------------
        # LOGO
        # ----------------------------------------------------

        self.logo_image = (
            self.load_logo()
        )


        if self.logo_image:

            logo = tk.Label(
                outer,
                image=(
                    self.logo_image
                ),
                bg=BG,

                bd=0,
                highlightthickness=0,
            )


            logo.pack(
                pady=(0, 6)
            )


        # ----------------------------------------------------
        # TITLE
        # ----------------------------------------------------

        title = tk.Label(
            outer,
            text="STEAM SWAPPER",
            bg=BG,
            fg=TEXT,

            bd=0,
            highlightthickness=0,

            font=(
                "Segoe UI",
                22,
                "bold",
            ),
        )


        title.pack()


        subtitle = tk.Label(
            outer,
            text=(
                "Choose an account "
                "and switch instantly."
            ),
            bg=BG,
            fg=MUTED,

            bd=0,
            highlightthickness=0,

            font=(
                "Segoe UI",
                10,
            ),
        )


        subtitle.pack(
            pady=(3, 18)
        )


        # ----------------------------------------------------
        # TABLE
        #
        # IMPORTANT:
        # No highlight border.
        # No white outline.
        # ----------------------------------------------------

        table_container = (
            tk.Frame(
                outer,
                bg=PANEL,

                bd=0,
                highlightthickness=0,
                relief="flat",
            )
        )


        table_container.pack(
            fill="both",
            expand=True,
        )


        # Grid is easier here because we have our own scrollbar
        table_container.grid_rowconfigure(
            0,
            weight=1,
        )


        table_container.grid_columnconfigure(
            0,
            weight=1,
        )


        columns = (
            "number",
            "login",
            "note",
        )


        self.tree = (
            ttk.Treeview(
                table_container,
                columns=columns,

                show="headings",

                selectmode="browse",

                style=(
                    "Dark.Treeview"
                ),
            )
        )


        # ----------------------------------------------------
        # HEADINGS
        # ----------------------------------------------------

        self.tree.heading(
            "number",
            text="#",
        )


        self.tree.heading(
            "login",
            text="STEAM LOGIN",
        )


        self.tree.heading(
            "note",
            text="NOTE",
        )


        # ----------------------------------------------------
        # COLUMNS
        # ----------------------------------------------------

        self.tree.column(
            "number",
            width=75,
            minwidth=60,
            stretch=False,
            anchor="center",
        )


        self.tree.column(
            "login",
            width=280,
            minwidth=180,
            anchor="w",
        )


        self.tree.column(
            "note",
            width=420,
            minwidth=200,
            anchor="w",
        )


        # ----------------------------------------------------
        # CUSTOM BLACK ROUNDED SCROLLBAR
        # ----------------------------------------------------

        self.scrollbar = RoundedScrollbar(
            table_container,
            command=self.tree.yview,
            width=14,
        )


        self.tree.configure(
            yscrollcommand=(
                self.scrollbar.set
            )
        )


        self.tree.grid(
            row=0,
            column=0,

            sticky="nsew",
        )


        self.scrollbar.grid(
            row=0,
            column=1,

            sticky="ns",

            padx=(4, 0),
        )


        # ----------------------------------------------------
        # MOUSE WHEEL
        # ----------------------------------------------------

        self.tree.bind(
            "<MouseWheel>",
            self._mousewheel,
        )


        # ----------------------------------------------------
        # EVENTS
        # ----------------------------------------------------

        self.tree.bind(
            "<Double-1>",
            lambda event:
            self.switch_selected(),
        )


        self.tree.bind(
            "<Return>",
            lambda event:
            self.switch_selected(),
        )


        self.tree.bind(
            "<Delete>",
            lambda event:
            self.remove_selected(),
        )


        # ----------------------------------------------------
        # BUTTONS
        # ----------------------------------------------------

        buttons = tk.Frame(
            outer,
            bg=BG,

            bd=0,
            highlightthickness=0,
        )


        buttons.pack(
            fill="x",
            pady=(16, 0),
        )


        self.create_button(
            buttons,
            "+ Add Account",
            self.add_account,
        ).pack(
            side="left",
            padx=(0, 8),
        )


        self.create_button(
            buttons,
            "Edit",
            self.edit_selected,
        ).pack(
            side="left",
            padx=(0, 8),
        )


        self.create_button(
            buttons,
            "Remove",
            self.remove_selected,
        ).pack(
            side="left",
            padx=(0, 8),
        )


        self.create_button(
            buttons,
            "Refresh",
            self.refresh,
        ).pack(
            side="left"
        )


        self.switch_button = (
            tk.Button(
                buttons,

                text=(
                    "SWITCH ACCOUNT"
                ),

                command=(
                    self.switch_selected
                ),

                bg=ORANGE,
                fg="#000000",

                activebackground=(
                    ORANGE_HOVER
                ),

                activeforeground=(
                    "#000000"
                ),

                relief="flat",

                bd=0,
                highlightthickness=0,

                cursor="hand2",

                padx=24,
                pady=9,

                font=(
                    "Segoe UI",
                    9,
                    "bold",
                ),
            )
        )


        self.switch_button.pack(
            side="right"
        )


        # ----------------------------------------------------
        # STATUS
        # ----------------------------------------------------

        self.status_var = (
            tk.StringVar()
        )


        status = tk.Label(
            outer,

            textvariable=(
                self.status_var
            ),

            bg=BG,
            fg=MUTED,

            anchor="w",

            bd=0,
            highlightthickness=0,

            font=(
                "Segoe UI",
                9,
            ),
        )


        status.pack(
            fill="x",
            pady=(12, 0),
        )


    # ========================================================
    # MOUSE WHEEL
    # ========================================================

    def _mousewheel(
        self,
        event,
    ):

        self.tree.yview_scroll(
            int(
                -1
                * (
                    event.delta / 120
                )
            ),
            "units",
        )


        return "break"


    # ========================================================
    # BUTTON
    # ========================================================

    def create_button(
        self,
        parent,
        text,
        command,
    ):

        return tk.Button(
            parent,

            text=text,

            command=command,

            bg=PANEL_ALT,
            fg=TEXT,

            activebackground=BORDER,
            activeforeground=TEXT,

            relief="flat",

            bd=0,
            highlightthickness=0,

            cursor="hand2",

            padx=15,
            pady=8,

            font=(
                "Segoe UI",
                9,
            ),
        )


    # ========================================================
    # WARNING
    # ========================================================

    def warn_steam_missing(
        self,
    ):

        messagebox.showwarning(
            APP_NAME,

            (
                "Steam could not be "
                "detected automatically.\n\n"

                "Account management will "
                "continue working, but "

                "switching accounts requires "
                "Steam to be detected."
            ),

            parent=self.root,
        )


    # ========================================================
    # REFRESH
    # ========================================================

    def refresh(
        self,
    ):

        try:

            accounts = (
                self.store.load()
            )

        except RuntimeError as exc:

            messagebox.showerror(
                APP_NAME,
                str(exc),
                parent=self.root,
            )

            return


        for item in (
            self.tree.get_children()
        ):

            self.tree.delete(
                item
            )


        for account in accounts:

            self.tree.insert(
                "",
                "end",

                iid=str(
                    account["number"]
                ),

                values=(
                    account["number"],
                    account["login"],
                    account["note"],
                ),
            )


        if self.steam_exe:

            steam_text = (
                f"Steam: "
                f"{self.steam_exe}"
            )

        else:

            steam_text = (
                "Steam not detected"
            )


        self.status_var.set(
            f"{len(accounts)} "
            f"account(s) registered  •  "
            f"{steam_text}"
        )


    # ========================================================
    # SELECTED ACCOUNT
    # ========================================================

    def selected_account(
        self,
    ):

        selection = (
            self.tree.selection()
        )


        if not selection:

            messagebox.showinfo(
                APP_NAME,
                "Select an account first.",
                parent=self.root,
            )

            return None


        number = int(
            selection[0]
        )


        for account in (
            self.store.load()
        ):

            if (
                account["number"]
                == number
            ):

                return account


        self.refresh()

        return None


    # ========================================================
    # ADD
    # ========================================================

    def add_account(
        self,
    ):

        dialog = AccountDialog(
            self.root,
            "Add Steam Account",
        )


        self.root.wait_window(
            dialog
        )


        if dialog.result is None:

            return


        number, login, note = (
            dialog.result
        )


        try:

            self.store.add(
                number,
                login,
                note,
            )

        except (
            ValueError,
            RuntimeError,
        ) as exc:

            messagebox.showerror(
                APP_NAME,
                str(exc),
                parent=self.root,
            )

            return


        self.refresh()


        if self.tree.exists(
            str(number)
        ):

            self.tree.selection_set(
                str(number)
            )


            self.tree.focus(
                str(number)
            )


            self.tree.see(
                str(number)
            )


    # ========================================================
    # EDIT
    # ========================================================

    def edit_selected(
        self,
    ):

        account = (
            self.selected_account()
        )


        if account is None:

            return


        dialog = AccountDialog(
            self.root,
            "Edit Steam Account",
            existing=account,
        )


        self.root.wait_window(
            dialog
        )


        if dialog.result is None:

            return


        number, login, note = (
            dialog.result
        )


        try:

            self.store.update(
                account["number"],
                number,
                login,
                note,
            )

        except (
            ValueError,
            RuntimeError,
        ) as exc:

            messagebox.showerror(
                APP_NAME,
                str(exc),
                parent=self.root,
            )

            return


        self.refresh()


        if self.tree.exists(
            str(number)
        ):

            self.tree.selection_set(
                str(number)
            )


            self.tree.focus(
                str(number)
            )


    # ========================================================
    # REMOVE
    # ========================================================

    def remove_selected(
        self,
    ):

        account = (
            self.selected_account()
        )


        if account is None:

            return


        answer = (
            messagebox.askyesno(
                APP_NAME,

                (
                    "Remove this account "
                    "from Steam Swapper?\n\n"

                    f"[{account['number']}] "
                    f"{account['login']}\n"

                    f"{account['note']}\n\n"

                    "This does not remove "
                    "the actual Steam account."
                ),

                parent=self.root,
            )
        )


        if not answer:

            return


        try:

            self.store.remove(
                account["number"]
            )

        except (
            ValueError,
            RuntimeError,
        ) as exc:

            messagebox.showerror(
                APP_NAME,
                str(exc),
                parent=self.root,
            )

            return


        self.refresh()


    # ========================================================
    # SWITCH
    # ========================================================

    def switch_selected(
        self,
    ):

        account = (
            self.selected_account()
        )


        if account is None:

            return


        self.steam_exe = (
            find_steam_executable()
        )


        if self.steam_exe is None:

            messagebox.showerror(
                APP_NAME,
                "Steam could not be found.",
                parent=self.root,
            )

            return


        answer = (
            messagebox.askyesno(
                APP_NAME,

                (
                    "Switch Steam account?\n\n"

                    f"[{account['number']}] "
                    f"{account['login']}\n"

                    f"{account['note']}\n\n"

                    "Steam will be restarted."
                ),

                parent=self.root,
            )
        )


        if not answer:

            return


        self.status_var.set(
            "Closing Steam... "
            f"{account['login']}"
        )


        self.root.update_idletasks()


        try:

            close_steam(
                self.steam_exe
            )


            launch_steam(
                self.steam_exe,
                account["login"],
            )

        except OSError as exc:

            messagebox.showerror(
                APP_NAME,

                (
                    "Could not start "
                    f"Steam:\n\n{exc}"
                ),

                parent=self.root,
            )

            return


        self.status_var.set(
            f'Steam started for '
            f'"{account["login"]}". '

            "Steam may request "
            "authentication if necessary."
        )


# ============================================================
# START APPLICATION
# ============================================================

def main():

    root = tk.Tk()


    SteamSwapperApp(
        root
    )


    root.mainloop()


if __name__ == "__main__":

    main()
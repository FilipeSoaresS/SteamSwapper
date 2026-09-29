import os
import re
import shutil
import subprocess
import time
from pathlib import Path


class SteamService:
    def find_executable(self):
        if os.name != "nt":
            return None

        try:
            import winreg

            locations = [
                (winreg.HKEY_CURRENT_USER, r"Software\Valve\Steam", "SteamExe"),
                (winreg.HKEY_CURRENT_USER, r"Software\Valve\Steam", "SteamPath"),
                (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Valve\Steam", "InstallPath"),
                (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Valve\Steam", "InstallPath"),
            ]

            for hive, key_path, value_name in locations:
                try:
                    with winreg.OpenKey(hive, key_path) as key:
                        value, _ = winreg.QueryValueEx(key, value_name)
                        candidate = Path(str(value).replace("/", "\\"))
                        if candidate.is_dir():
                            candidate /= "steam.exe"
                        if candidate.is_file():
                            return candidate
                except (FileNotFoundError, OSError):
                    pass
        except Exception:
            pass

        candidates = [
            Path(os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)")) / "Steam" / "steam.exe",
            Path(os.environ.get("ProgramFiles", r"C:\Program Files")) / "Steam" / "steam.exe",
            Path(r"C:\Steam\steam.exe"),
        ]

        return next((p for p in candidates if p.is_file()), None)

    def is_running(self):
        if os.name != "nt":
            return False

        try:
            result = subprocess.run(
                ["tasklist", "/FI", "IMAGENAME eq steam.exe"],
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW,
                check=False,
            )
            return "steam.exe" in result.stdout.lower()
        except OSError:
            return False

    def close(self, steam_exe):
        if os.name != "nt":
            return False

        flags = subprocess.CREATE_NO_WINDOW

        try:
            subprocess.Popen(
                [str(steam_exe), "-shutdown"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=flags,
            )
        except OSError:
            pass

        for _ in range(16):
            if not self.is_running():
                # Give Steam's helper processes a brief moment to release
                # files/IPC handles before the next client instance starts.
                time.sleep(0.75)
                return True
            time.sleep(0.5)

        for process in ("steam.exe", "steamwebhelper.exe", "gameoverlayui.exe"):
            try:
                subprocess.run(
                    ["taskkill", "/F", "/IM", process],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    creationflags=flags,
                    check=False,
                )
            except OSError:
                pass

        time.sleep(1.5)
        return not self.is_running()

    def _loginusers_file(self, steam_exe):
        return Path(steam_exe).resolve().parent / "config" / "loginusers.vdf"

    @staticmethod
    def _vdf_get(block, key):
        match = re.search(rf'"{re.escape(key)}"\s+"([^"]*)"', block, flags=re.IGNORECASE)
        return match.group(1) if match else ""

    @staticmethod
    def _set_auto_login_user(login):
        """Tell Steam which remembered account should be selected at startup."""
        if os.name != "nt" or not login:
            return
        try:
            import winreg
            with winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"Software\Valve\Steam") as key:
                winreg.SetValueEx(key, "AutoLoginUser", 0, winreg.REG_SZ, str(login))
        except (OSError, ImportError):
            pass

    def prepare_offline_mode(self, steam_exe, login="", steam_id=""):
        """Prepare Steam's saved account data for an offline startup."""
        vdf = self._loginusers_file(steam_exe)
        if not vdf.is_file():
            raise RuntimeError(
                "Steam's saved account file was not found:\n\n"
                f"{vdf}\n\n"
                "Log into the target Steam account online at least once and "
                "allow Steam to remember the account on this computer."
            )

        try:
            text = vdf.read_text(encoding="utf-8-sig")
        except OSError as exc:
            raise RuntimeError(f"Could not read Steam's account configuration:\n\n{exc}") from exc

        lines = text.splitlines(keepends=True)
        blocks = self._find_account_blocks(lines)
        if not blocks:
            raise RuntimeError(
                "Steam's saved account configuration does not contain recognizable account entries."
            )

        login_norm = (login or "").strip().lower()
        steam_id_norm = (steam_id or "").strip()
        target_sid = None

        for sid, start_line, end_line in blocks:
            body = "".join(lines[start_line:end_line + 1])
            account_name = self._vdf_get(body, "AccountName").strip().lower()
            if steam_id_norm and sid == steam_id_norm:
                target_sid = sid
                break
            if login_norm and account_name == login_norm:
                target_sid = sid
                break

        if target_sid is None:
            raise RuntimeError(
                f'Steam does not have a saved local session for "{login or steam_id}".\n\n'
                "Log into this account in Steam online once, enable remembering the account, "
                "and then use Offline mode."
            )

        backup = vdf.with_suffix(vdf.suffix + ".steam_swapper_backup")
        if not backup.exists():
            try:
                shutil.copy2(vdf, backup)
            except OSError:
                pass

        changed = False
        for sid, start_line, end_line in reversed(blocks):
            block = lines[start_line:end_line + 1]
            before = list(block)
            is_target = sid == target_sid
            self._set_vdf_value(block, "WantsOfflineMode", "1" if is_target else "0")
            self._set_vdf_value(block, "MostRecent", "1" if is_target else "0")
            self._set_vdf_value(block, "SkipOfflineModeWarning", "1" if is_target else "0")
            if is_target:
                self._set_vdf_value(block, "RememberPassword", "1")
                self._set_vdf_value(block, "AllowAutoLogin", "1")
                self._set_vdf_value(block, "Timestamp", str(int(time.time())))
            if block != before:
                changed = True
            lines[start_line:end_line + 1] = block

        new_text = "".join(lines)
        if changed:
            self._write_offline_vdf_and_verify(vdf, new_text, target_sid)
        else:
            # Verify an already-prepared file too.
            self._write_offline_vdf_and_verify(vdf, new_text, target_sid)

        self._set_auto_login_user(login)
        return vdf

    def prepare_online_mode(self, steam_exe, login="", steam_id=""):
        """Clear saved offline flags before using the original -login startup."""
        vdf = self._loginusers_file(steam_exe)
        if not vdf.is_file():
            return

        try:
            text = vdf.read_text(encoding="utf-8-sig")
        except OSError as exc:
            raise RuntimeError(f"Could not read Steam's account configuration:\n\n{exc}") from exc

        lines = text.splitlines(keepends=True)
        blocks = self._find_account_blocks(lines)
        if not blocks:
            return

        login_norm = (login or "").strip().lower()
        steam_id_norm = (steam_id or "").strip()
        target_sid = None

        for sid, start_line, end_line in blocks:
            body = "".join(lines[start_line:end_line + 1])
            account_name = self._vdf_get(body, "AccountName").strip().lower()
            if steam_id_norm and sid == steam_id_norm:
                target_sid = sid
                break
            if login_norm and account_name == login_norm:
                target_sid = sid
                break

        changed = False
        for sid, start_line, end_line in reversed(blocks):
            block = lines[start_line:end_line + 1]
            before = list(block)
            is_target = sid == target_sid
            self._set_vdf_value(block, "WantsOfflineMode", "0")
            self._set_vdf_value(block, "SkipOfflineModeWarning", "0")
            self._set_vdf_value(block, "MostRecent", "1" if is_target else "0")
            if is_target:
                self._set_vdf_value(block, "RememberPassword", "1")
                self._set_vdf_value(block, "AllowAutoLogin", "1")
                self._set_vdf_value(block, "Timestamp", str(int(time.time())))
            if block != before:
                changed = True
            lines[start_line:end_line + 1] = block

        if changed:
            self._write_vdf(vdf, "".join(lines))
        self._set_auto_login_user(login)
        return vdf

    @staticmethod
    def _find_account_blocks(lines):
        blocks = []
        i = 0
        while i < len(lines):
            m = re.match(r'^([ \t]*)"(\d{17})"[ \t]*(?:\{)?[ \t]*$', lines[i].rstrip("\r\n"))
            if not m:
                i += 1
                continue

            sid = m.group(2)
            start_line = i
            first_line_has_brace = "{" in lines[i]
            if not first_line_has_brace:
                k = i + 1
                while k < len(lines) and not lines[k].strip():
                    k += 1
                if k >= len(lines) or lines[k].strip() != "{":
                    i += 1
                    continue
            else:
                k = i

            j = k
            depth = 0
            while j < len(lines):
                depth += lines[j].count("{") - lines[j].count("}")
                if depth == 0:
                    break
                j += 1
            if j >= len(lines):
                raise RuntimeError("Steam's loginusers.vdf appears to be incomplete or malformed.")

            blocks.append((sid, start_line, j))
            i = j + 1
        return blocks

    @staticmethod
    def _set_vdf_value(block_lines, key, value, indent="\t\t"):
        pattern = re.compile(rf'^(\s*)"{re.escape(key)}"\s+"[^"]*"\s*$', re.IGNORECASE)
        for idx, line in enumerate(block_lines):
            newline = "\n" if line.endswith("\n") else ""
            raw = line[:-1] if newline else line
            if raw.endswith("\r"):
                raw = raw[:-1]
                newline = "\r\n"
            match = pattern.match(raw)
            if match:
                block_lines[idx] = f'{match.group(1)}"{key}"\t\t"{value}"{newline}'
                return
        closing = len(block_lines) - 1
        block_lines.insert(closing, f'{indent}"{key}"\t\t"{value}"\n')

    @staticmethod
    def _write_vdf(vdf, new_text):
        temp = vdf.with_suffix(vdf.suffix + ".tmp")
        try:
            temp.write_text(new_text, encoding="utf-8")
            temp.replace(vdf)
        except OSError as exc:
            if temp.exists():
                try:
                    temp.unlink()
                except OSError:
                    pass
            raise RuntimeError(f"Could not update Steam's account configuration:\n\n{exc}") from exc

    @staticmethod
    def _write_offline_vdf_and_verify(vdf, new_text, target_sid):
        """Atomically write loginusers.vdf and verify the target flags."""
        temp = vdf.with_suffix(vdf.suffix + ".tmp")
        try:
            temp.write_text(new_text, encoding="utf-8")
            temp.replace(vdf)
        except OSError as exc:
            if temp.exists():
                try:
                    temp.unlink()
                except OSError:
                    pass
            raise RuntimeError(f"Could not update Steam's offline configuration:\n\n{exc}") from exc

        try:
            verify = vdf.read_text(encoding="utf-8-sig")
        except OSError as exc:
            raise RuntimeError(f"Could not verify Steam's offline configuration:\n\n{exc}") from exc

        target_re = re.search(
            rf'"{re.escape(target_sid)}"\s*\{{(?P<body>.*?)\n\s*\}}',
            verify,
            re.DOTALL,
        )
        if not target_re:
            raise RuntimeError("Steam's account configuration could not be verified after the update.")

        body = target_re.group("body")
        wants = SteamService._vdf_get(body, "WantsOfflineMode")
        if wants != "1":
            raise RuntimeError(
                "Steam did not accept the offline-mode configuration. "
                "The target account's WantsOfflineMode flag could not be verified."
            )
        return vdf

    def restart(self, steam_exe):
        """Restart Steam without changing the selected account."""
        flags = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
        time.sleep(0.75)
        subprocess.Popen(
            [str(steam_exe)],
            cwd=str(steam_exe.parent),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=flags,
        )

    def launch(self, steam_exe, login, mode, steam_id=""):
        """Start Steam using the same account-switch sequence as the original app.

        The original working implementation launched the selected account with:
            steam.exe -login <login>
        We keep that exact behavior for Online and Auto.  Offline is the only
        exception: Steam must be allowed to select the saved account from
        loginusers.vdf after WantsOfflineMode/MostRecent have been prepared.
        """
        flags = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0

        if mode == "offline":
            # Prepare the selected account in loginusers.vdf and explicitly
            # request Steam's offline startup path. The VDF selects the
            # account; -offlinemode tells the freshly-started client not to
            # attempt a normal online login. This is intentionally used only
            # after the Steam process has been fully closed.
            self.prepare_offline_mode(steam_exe, login=login, steam_id=steam_id)
            args = [str(steam_exe), "-offlinemode"]
        else:
            # Clear any offline flags left by a previous Offline launch before
            # using the original, known-good account switch command.
            # This is especially important when switching Offline -> Online.
            self.prepare_online_mode(steam_exe, login=login, steam_id=steam_id)

            # Keep the exact startup command from the original working base.
            args = [str(steam_exe), "-login", login]

        # The old Tkinter implementation launched Steam immediately after the
        # close sequence. Keep the same command, but allow Windows a short
        # stabilization window so Steam's helpers have fully exited.
        time.sleep(0.75)

        subprocess.Popen(
            args,
            cwd=str(steam_exe.parent),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=flags,
        )

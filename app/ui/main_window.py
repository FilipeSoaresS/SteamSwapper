from pathlib import Path
import threading

from PySide6.QtCore import Qt, QSize, QTimer, Signal, QObject, QPointF
from PySide6.QtGui import QColor, QFont, QIcon, QPainter, QPainterPath, QPen, QPixmap, QLinearGradient, QRadialGradient, QRegion
from PySide6.QtWidgets import (
    QApplication, QDialog, QFrame, QGridLayout, QHBoxLayout, QLabel, QLineEdit,
    QMainWindow, QPushButton, QScrollArea, QSizePolicy, QSlider, QVBoxLayout, QWidget,
    QComboBox, QFileDialog
)

from app.config import APP_NAME, ICON_FILE, LOGO_FILE, get_theme
from app.models.account import Account
from app.utils.images import copy_avatar, fetch_profile_avatar


LANGUAGES = {
    "pt-BR": {
        "name": "Português (Brasil)", "flag": "🇧🇷",
        "brand_sub": "LANÇADOR DE CONTAS", "section": "MINHAS CONTAS",
        "section_sub": "Selecione um perfil e inicie instantaneamente.", "search": "Pesquisar contas…",
        "add": "ADICIONAR CONTA", "current": "PERFIL ATUAL", "switch": "TROCAR", "edit": "EDITAR", "restart": "REINICIAR STEAM",
        "sort": "ORDENAR", "launch": "INICIAR", "switch_account": "TROCAR CONTA", "confirm_action": "CONFIRMAR AÇÃO", "confirm": "CONFIRMAR", "remove_action": "REMOVER", "error": "ERRO", "app_label": "STEAM SWAPPER",
        "online": "Conectado", "offline": "Desconectado", "auto": "Automático", "running": "● STEAM EM EXECUÇÃO",
        "steam_offline": "● STEAM OFFLINE", "accounts": "contas", "no_accounts": "NENHUMA CONTA",
        "empty_sub": "Adicione sua primeira conta Steam para começar.", "name_az": "Nome A-Z", "name_za": "Nome Z-A",
        "newest": "Mais recentes", "oldest": "Mais antigas", "theme_light": "☀ CLARO", "theme_dark": "☾ ESCURO",
        "dialog_add": "ADICIONAR CONTA STEAM", "dialog_edit": "EDITAR CONTA STEAM", "profile_name": "Nome do perfil",
        "steam_login": "Login Steam", "steam_id": "SteamID64 (opcional)", "note": "Observação", "cancel": "CANCELAR",
        "save": "SALVAR", "ok": "OK", "remove": "Remover conta", "remove_text": "Remover {login} do Steam Swapper?",
        "switch_title": "Trocar conta Steam", "select_first": "Selecione uma conta primeiro.",
        "steam_not_found": "O Steam não foi detectado.", "steam_restart": "O Steam será reiniciado.", "restart_title": "Reiniciar Steam", "restart_done": "Steam foi reiniciado.",
        "launch_mode": "Modo de inicialização", "error_add": "Não foi possível adicionar a conta",
        "error_edit": "Não foi possível atualizar a conta", "error_remove": "Não foi possível remover a conta",
        "error_switch": "Não foi possível trocar a conta", "switch_failed": "Troca de conta falhou",
        "steam_started": 'Steam iniciado para "{login}" • {mode}', "closing": "Fechando Steam…  {login}",
    },
    "en": {
        "name": "English", "flag": "🇺🇸", "brand_sub": "ACCOUNT LAUNCHER", "section": "MY ACCOUNTS",
        "section_sub": "Select a profile and launch it instantly.", "search": "Search accounts…", "add": "ADD ACCOUNT",
        "current": "CURRENT PROFILE", "switch": "SWITCH", "edit": "EDIT", "restart": "RESTART STEAM", "sort": "SORT",
        "launch": "LAUNCH", "switch_account": "SWITCH ACCOUNT", "confirm_action": "CONFIRM ACTION", "confirm": "CONFIRM", "remove_action": "REMOVE", "error": "ERROR", "app_label": "STEAM SWAPPER", "online": "Online", "offline": "Offline", "auto": "Automatic",
        "running": "● STEAM RUNNING", "steam_offline": "● STEAM OFFLINE", "accounts": "accounts", "no_accounts": "NO ACCOUNTS",
        "empty_sub": "Add your first Steam account to build your launcher.", "name_az": "Name A-Z", "name_za": "Name Z-A",
        "newest": "Newest first", "oldest": "Oldest first", "theme_light": "☀ LIGHT", "theme_dark": "☾ DARK",
        "dialog_add": "ADD STEAM ACCOUNT", "dialog_edit": "EDIT STEAM ACCOUNT", "profile_name": "Profile name",
        "steam_login": "Steam login", "steam_id": "SteamID64 (optional)", "note": "Note", "cancel": "CANCEL",
        "save": "SAVE", "ok": "OK", "remove": "Remove account", "remove_text": "Remove {login} from Steam Swapper?",
        "switch_title": "Switch Steam account", "select_first": "Select an account first.",
        "steam_not_found": "Steam could not be detected.", "steam_restart": "Steam will be restarted.", "restart_title": "Restart Steam", "restart_done": "Steam was restarted.",
        "launch_mode": "Launch mode", "error_add": "Could not add account", "error_edit": "Could not update account",
        "error_remove": "Could not remove account", "error_switch": "Could not switch account", "switch_failed": "Switch failed",
        "steam_started": 'Steam started for "{login}" • {mode}', "closing": "Closing Steam…  {login}",
    },
    "es": {
        "name": "Español", "flag": "🇪🇸", "brand_sub": "LANZADOR DE CUENTAS", "section": "MIS CUENTAS",
        "section_sub": "Selecciona un perfil e inícialo al instante.", "search": "Buscar cuentas…", "add": "AÑADIR CUENTA",
        "current": "PERFIL ACTUAL", "switch": "CAMBIAR", "edit": "EDITAR", "restart": "REINICIAR STEAM", "sort": "ORDENAR",
        "launch": "INICIAR", "switch_account": "CAMBIAR CUENTA", "confirm_action": "CONFIRMAR ACCIÓN", "confirm": "CONFIRMAR", "remove_action": "ELIMINAR", "error": "ERROR", "app_label": "STEAM SWAPPER", "online": "En línea", "offline": "Sin conexión", "auto": "Automático",
        "running": "● STEAM EN EJECUCIÓN", "steam_offline": "● STEAM SIN CONEXIÓN", "accounts": "cuentas", "no_accounts": "SIN CUENTAS",
        "empty_sub": "Añade tu primera cuenta de Steam para empezar.", "name_az": "Nombre A-Z", "name_za": "Nombre Z-A",
        "newest": "Más recientes", "oldest": "Más antiguas", "theme_light": "☀ CLARO", "theme_dark": "☾ OSCURO",
        "dialog_add": "AÑADIR CUENTA DE STEAM", "dialog_edit": "EDITAR CUENTA DE STEAM", "profile_name": "Nombre del perfil",
        "steam_login": "Inicio de Steam", "steam_id": "SteamID64 (opcional)", "note": "Nota", "cancel": "CANCELAR",
        "save": "GUARDAR", "ok": "OK", "remove": "Eliminar cuenta", "remove_text": "¿Eliminar {login} de Steam Swapper?",
        "switch_title": "Cambiar cuenta de Steam", "select_first": "Selecciona una cuenta primero.",
        "steam_not_found": "No se detectó Steam.", "steam_restart": "Steam se reiniciará.", "restart_title": "Reiniciar Steam", "restart_done": "Steam se reinició.", "launch_mode": "Modo de inicio",
        "error_add": "No se pudo añadir la cuenta", "error_edit": "No se pudo actualizar la cuenta",
        "error_remove": "No se pudo eliminar la cuenta", "error_switch": "No se pudo cambiar la cuenta", "switch_failed": "Cambio fallido",
        "steam_started": 'Steam iniciado para "{login}" • {mode}', "closing": "Cerrando Steam…  {login}",
    },
    "zh": {
        "name": "中文", "flag": "🇨🇳", "brand_sub": "账户启动器", "section": "我的账户",
        "section_sub": "选择一个配置文件并立即启动。", "search": "搜索账户…", "add": "添加账户", "current": "当前配置",
        "switch": "切换", "edit": "编辑", "restart": "重启 STEAM", "sort": "排序", "launch": "启动", "switch_account": "切换账户", "confirm_action": "确认操作", "confirm": "确认", "remove_action": "删除", "error": "错误", "app_label": "STEAM SWAPPER",
        "online": "在线", "offline": "离线", "auto": "自动", "running": "● STEAM 正在运行", "steam_offline": "● STEAM 离线",
        "accounts": "个账户", "no_accounts": "暂无账户", "empty_sub": "添加你的第一个 Steam 账户。", "name_az": "名称 A-Z",
        "name_za": "名称 Z-A", "newest": "最新添加", "oldest": "最早添加", "theme_light": "☀ 浅色", "theme_dark": "☾ 深色",
        "dialog_add": "添加 STEAM 账户", "dialog_edit": "编辑 STEAM 账户", "profile_name": "配置名称", "steam_login": "Steam 登录名",
        "steam_id": "SteamID64（可选）", "note": "备注", "cancel": "取消", "save": "保存", "ok": "确定", "remove": "删除账户",
        "remove_text": "确定要从 Steam Swapper 删除 {login} 吗？", "switch_title": "切换 Steam 账户", "select_first": "请先选择一个账户。",
        "steam_not_found": "未检测到 Steam。", "steam_restart": "Steam 将重新启动。", "restart_title": "重启 Steam", "restart_done": "Steam 已重新启动。", "launch_mode": "启动模式",
        "error_add": "无法添加账户", "error_edit": "无法更新账户", "error_remove": "无法删除账户", "error_switch": "无法切换账户",
        "switch_failed": "切换失败", "steam_started": 'Steam 已为“{login}”启动 • {mode}', "closing": "正在关闭 Steam…  {login}",
    },
}


def tr(lang, key, **kwargs):
    text = LANGUAGES.get(lang, LANGUAGES["en"]).get(key, LANGUAGES["en"].get(key, key))
    return text.format(**kwargs) if kwargs else text


class WorkerSignals(QObject):
    avatar_ready = Signal(str, str)


class GlowBackground(QWidget):
    """Subtle abstract topographic background; no large circular outlines."""
    def __init__(self, parent=None, theme_name="dark"):
        super().__init__(parent)
        self.theme_name = theme_name
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

    def set_theme(self, theme_name):
        self.theme_name = theme_name
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()
        t = get_theme(self.theme_name)
        p.fillRect(self.rect(), QColor(t["BG_DARK"]))

        # Very soft ambient light, kept behind the UI.
        for x, y, r, color in [
            (0.08, 0.20, 260, QColor(10, 83, 125, 30) if self.theme_name == "dark" else QColor(45, 115, 170, 20)),
            (0.84, 0.22, 300, QColor(20, 105, 145, 22) if self.theme_name == "dark" else QColor(55, 130, 180, 16)),
            (0.78, 0.82, 330, QColor(11, 75, 108, 20) if self.theme_name == "dark" else QColor(35, 105, 150, 14)),
        ]:
            center = QPointF(w * x, h * y)
            g = QRadialGradient(center, r)
            g.setColorAt(0.0, color)
            g.setColorAt(1.0, QColor(0, 0, 0, 0))
            p.setBrush(g)
            p.setPen(Qt.PenStyle.NoPen)
            p.drawEllipse(center, r, r)

        # Organic topographic contour lines.
        # They stay mostly at the edges and use many irregular nested paths.
        line_color = QColor(54, 126, 163, 42) if self.theme_name == "dark" else QColor(55, 115, 150, 30)
        accent_color = QColor(70, 156, 198, 30) if self.theme_name == "dark" else QColor(70, 135, 170, 22)
        p.setBrush(Qt.BrushStyle.NoBrush)

        def organic_contour(cx, cy, rx, ry, phase, pen_color=line_color, width=1.0):
            path = QPainterPath()
            steps = 96
            import math
            for k in range(steps + 1):
                a = (k / steps) * math.tau
                # Layered low-frequency deformation creates natural contour irregularity.
                radial = 1.0 + 0.065 * math.sin(3 * a + phase) + 0.035 * math.sin(7 * a - phase * 0.7)
                x = cx + rx * radial * math.cos(a)
                y = cy + ry * radial * math.sin(a)
                if k == 0:
                    path.moveTo(QPointF(x, y))
                else:
                    path.lineTo(QPointF(x, y))
            p.setPen(QPen(pen_color, width))
            p.drawPath(path)

        # Left terrain mass: many nested, offset contours.
        for i in range(16):
            organic_contour(
                w * 0.02, h * 0.38,
                120 + i * 30, 75 + i * 24,
                i * 0.42,
                accent_color if i in (3, 8, 13) else line_color,
                1.0,
            )

        # Right terrain mass. It is intentionally asymmetrical to avoid the previous circular feel.
        for i in range(19):
            organic_contour(
                w * 0.98, h * 0.42,
                105 + i * 31, 62 + i * 22,
                1.7 + i * 0.36,
                accent_color if i in (4, 10, 16) else line_color,
                1.0,
            )

        # Lower-right contour cluster, lighter and more open.
        for i in range(9):
            organic_contour(
                w * 0.82, h * 0.91,
                95 + i * 27, 48 + i * 17,
                2.4 + i * 0.5,
                line_color,
                1.0,
            )



class RoundButton(QPushButton):
    def __init__(self, text, primary=False, parent=None):
        super().__init__(text, parent)
        self.primary = primary
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumHeight(38)
        self.setProperty("primary", primary)


class AccountCard(QFrame):
    clicked = Signal(str)
    switch_requested = Signal(str)

    def __init__(self, account, selected=False, size=150, theme_name="dark", parent=None, list_mode=False):
        super().__init__(parent)
        self.account = account
        self.selected = selected
        self.size_px = size
        self.theme_name = theme_name
        self.list_mode = list_mode
        self.setObjectName("AccountCard")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setProperty("selected", selected)

        if self.list_mode:
            self.setFixedHeight(76)
            self.setMinimumWidth(0)
            self.setMaximumWidth(16777215)
            self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            layout = QHBoxLayout(self)
            layout.setContentsMargins(12, 8, 16, 8)
            layout.setSpacing(14)

            self.avatar = QLabel()
            self.avatar.setFixedSize(58, 58)
            self.avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.avatar.setObjectName("Avatar")
            layout.addWidget(self.avatar, 0, Qt.AlignmentFlag.AlignVCenter)

            self.name = QLabel(account.name or account.login)
            self.name.setObjectName("CardName")
            self.name.setMinimumWidth(170)
            self.name.setMaximumWidth(260)
            self.name.setWordWrap(False)
            layout.addWidget(self.name, 0, Qt.AlignmentFlag.AlignVCenter)

            self.meta = QLabel(account.login)
            self.meta.setObjectName("CardMeta")
            self.meta.setMinimumWidth(70)
            self.meta.setMaximumWidth(210)
            self.meta.setWordWrap(False)
            layout.addWidget(self.meta, 0, Qt.AlignmentFlag.AlignVCenter)

            description = account.note if account.note and account.note != "No note" else "—"
            self.note = QLabel(description)
            self.note.setObjectName("CardMeta")
            self.note.setMinimumWidth(160)
            self.note.setMaximumWidth(360)
            self.note.setWordWrap(False)
            layout.addWidget(self.note, 1, Qt.AlignmentFlag.AlignVCenter)
        else:
            self.setFixedWidth(size + 70)
            self.setMinimumHeight(size + 82)
            layout = QVBoxLayout(self)
            layout.setContentsMargins(10, 10, 10, 6)
            layout.setSpacing(5)
            layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
            self.avatar = QLabel()
            self.avatar.setFixedSize(size, size)
            self.avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.avatar.setObjectName("Avatar")
            layout.addWidget(self.avatar, 0, Qt.AlignmentFlag.AlignHCenter)
            self.name = QLabel(account.name or account.login)
            self.name.setObjectName("CardName")
            self.name.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.name.setMaximumWidth(size + 50)
            layout.addWidget(self.name)
            self.meta = QLabel(account.login if account.note == "No note" else account.note)
            self.meta.setObjectName("CardMeta")
            self.meta.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.meta.setMaximumWidth(size + 50)
            layout.addWidget(self.meta)

        self._set_avatar(account.avatar)
        self.setStyleSheet(self._style())

    def _style(self):
        t = get_theme(self.theme_name)
        radius = 18 if self.list_mode else 24
        if self.selected:
            return f"QFrame#AccountCard {{ background: {t['CARD_BG']}; border: 1px solid {t['STEAM_BLUE_HOVER']}; border-radius: {radius}px; }} QFrame#AccountCard:hover {{ background: {t['CARD_HOVER']}; border: 1px solid {t['STEAM_BLUE_HOVER']}; }}"
        return f"QFrame#AccountCard {{ background: {t['CARD_BG']}; border: 1px solid {t['CARD_BORDER']}; border-radius: {radius}px; }} QFrame#AccountCard:hover {{ background: {t['CARD_HOVER']}; border: 1px solid {t['BORDER']}; }}"

    def _set_avatar(self, path):
        if path and Path(path).is_file():
            pix = QPixmap(path)
            if not pix.isNull():
                pix = pix.scaled(self.avatar.size(), Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation)
                mask = QPixmap(self.avatar.size())
                mask.fill(Qt.GlobalColor.transparent)
                painter = QPainter(mask)
                painter.setRenderHint(QPainter.RenderHint.Antialiasing)
                path_shape = QPainterPath()
                radius = 14 if self.list_mode else 20
                path_shape.addRoundedRect(0, 0, self.avatar.width(), self.avatar.height(), radius, radius)
                painter.setClipPath(path_shape)
                painter.drawPixmap(0, 0, pix)
                painter.end()
                self.avatar.setPixmap(mask)
                return
        t = get_theme(self.theme_name)
        radius = 14 if self.list_mode else 20
        self.avatar.setText("+")
        self.avatar.setStyleSheet(f"background: {t['AVATAR_PLACEHOLDER']}; border: 1px solid {t['BORDER']}; border-radius: {radius}px; color: {t['MUTED']}; font-size: 24px;")

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.account.id)
        super().mousePressEvent(event)


class HeroAccount(QFrame):
    switch_requested = Signal(str)
    edit_requested = Signal(str)
    add_requested = Signal()
    restart_requested = Signal()
    mode_changed = Signal(str)

    def __init__(self, account, size=132, language="en", theme_name="dark", launch_mode="online", parent=None, list_mode=False):
        super().__init__(parent)
        self.account = account
        self.language = language
        self.theme_name = theme_name
        self.launch_mode = launch_mode
        self.list_mode = list_mode
        self.setObjectName("HeroCard")

        t = get_theme(self.theme_name)
        radius = 18 if self.list_mode else 28
        self.setStyleSheet(
            f"QFrame#HeroCard {{ background: {t['HERO_BG']}; border: 1px solid {t['HERO_BORDER']}; border-radius: {radius}px; }}"
        )

        if self.list_mode:
            # True horizontal list row: every important piece of information stays
            # visible in the same line, starting from the left edge.
            self.setFixedHeight(86)
            self.setMinimumWidth(0)
            self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

            root = QHBoxLayout(self)
            root.setContentsMargins(8, 8, 8, 8)
            root.setSpacing(6)

            self.badge = QLabel(tr(self.language, "current"))
            self.badge.setObjectName("HeroBadge")
            self.badge.setFixedWidth(72)
            self.badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
            root.addWidget(self.badge, 0)

            self.avatar = QLabel()
            self.avatar.setFixedSize(56, 56)
            self.avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.avatar.setObjectName("HeroAvatar")
            root.addWidget(self.avatar, 0)

            self.name = QLabel(account.name or account.login)
            self.name.setObjectName("HeroName")
            self.name.setMinimumWidth(100)
            self.name.setMaximumWidth(150)
            self.name.setWordWrap(False)
            root.addWidget(self.name, 0)

            self.login_label = QLabel(account.login)
            self.login_label.setObjectName("HeroMeta")
            self.login_label.setMinimumWidth(85)
            self.login_label.setMaximumWidth(130)
            self.login_label.setWordWrap(False)
            root.addWidget(self.login_label, 0)

            description = account.note if account.note and account.note != "No note" else "—"
            self.meta = QLabel(description)
            self.meta.setObjectName("HeroMeta")
            self.meta.setMinimumWidth(130)
            self.meta.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            self.meta.setWordWrap(False)
            root.addWidget(self.meta, 1)

            self.launch_combo = QComboBox()
            self.launch_combo.setObjectName("HeroLaunch")
            self.launch_combo.addItem(tr(self.language, "online"), "online")
            self.launch_combo.addItem(tr(self.language, "offline"), "offline")
            self.launch_combo.addItem(tr(self.language, "auto"), "auto")
            self.launch_combo.setCurrentIndex({"online": 0, "offline": 1, "auto": 2}.get(self.launch_mode, 0))
            self.launch_combo.setFixedWidth(118)
            self.launch_combo.currentIndexChanged.connect(self._mode_changed)
            root.addWidget(self.launch_combo, 0)

            switch = RoundButton(tr(self.language, "switch"), True)
            restart = RoundButton(tr(self.language, "restart"))
            edit = RoundButton(tr(self.language, "edit"))
            add = RoundButton("+")
            switch.setFixedWidth(88)
            restart.setFixedWidth(150)
            edit.setFixedWidth(76)
            add.setFixedWidth(40)
            switch.clicked.connect(lambda: self.switch_requested.emit(account.id))
            restart.clicked.connect(self.restart_requested.emit)
            edit.clicked.connect(lambda: self.edit_requested.emit(account.id))
            add.clicked.connect(self.add_requested.emit)
            root.addWidget(switch, 0)
            root.addWidget(restart, 0)
            root.addWidget(edit, 0)
            root.addWidget(add, 0)
        else:
            self.setFixedSize(400, 300)
            root = QVBoxLayout(self)
            root.setContentsMargins(20, 16, 20, 16)
            root.setSpacing(7)
            root.setAlignment(Qt.AlignmentFlag.AlignCenter)

            self.badge = QLabel(tr(self.language, "current"))
            self.badge.setObjectName("HeroBadge")
            self.badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
            root.addWidget(self.badge)

            self.avatar = QLabel()
            self.avatar.setFixedSize(size, size)
            self.avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.avatar.setObjectName("HeroAvatar")
            root.addWidget(self.avatar, 0, Qt.AlignmentFlag.AlignCenter)

            self.name = QLabel(account.name or account.login)
            self.name.setObjectName("HeroName")
            self.name.setAlignment(Qt.AlignmentFlag.AlignCenter)
            root.addWidget(self.name)

            self.meta = QLabel(f"{account.login}  •  {account.note}")
            self.meta.setObjectName("HeroMeta")
            self.meta.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.meta.setWordWrap(False)
            root.addWidget(self.meta)

            self.launch_label = QLabel(tr(self.language, "launch"))
            self.launch_label.setObjectName("HeroLaunchLabel")
            self.launch_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            root.addWidget(self.launch_label)

            self.launch_combo = QComboBox()
            self.launch_combo.setObjectName("HeroLaunch")
            self.launch_combo.addItem(tr(self.language, "online"), "online")
            self.launch_combo.addItem(tr(self.language, "offline"), "offline")
            self.launch_combo.addItem(tr(self.language, "auto"), "auto")
            self.launch_combo.setCurrentIndex({"online": 0, "offline": 1, "auto": 2}.get(self.launch_mode, 0))
            self.launch_combo.currentIndexChanged.connect(self._mode_changed)
            root.addWidget(self.launch_combo)

            buttons = QHBoxLayout()
            buttons.setSpacing(8)
            buttons.setContentsMargins(0, 0, 0, 0)
            switch = RoundButton(tr(self.language, "switch"), True)
            restart = RoundButton(tr(self.language, "restart"))
            edit = RoundButton(tr(self.language, "edit"))
            add = RoundButton("+")
            # Keep the four icon-mode actions inside the 400px hero card
            # without clipping or overlap. These widths are intentionally
            # separate from the list-mode controls above.
            switch.setFixedWidth(82)
            restart.setFixedWidth(135)
            edit.setFixedWidth(82)
            add.setFixedWidth(42)
            switch.clicked.connect(lambda: self.switch_requested.emit(account.id))
            restart.clicked.connect(self.restart_requested.emit)
            edit.clicked.connect(lambda: self.edit_requested.emit(account.id))
            add.clicked.connect(self.add_requested.emit)
            buttons.addWidget(switch)
            buttons.addWidget(restart)
            buttons.addWidget(edit)
            buttons.addWidget(add)
            root.addLayout(buttons)

        self._set_avatar(account.avatar)

    def _mode_changed(self, index):
        mode = self.launch_combo.itemData(index)
        if mode:
            self.launch_mode = mode
            self.mode_changed.emit(mode)

    def _set_avatar(self, path):
        if path and Path(path).is_file():
            pix = QPixmap(path)
            if not pix.isNull():
                pix = pix.scaled(
                    self.avatar.size(),
                    Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                    Qt.TransformationMode.SmoothTransformation,
                )
                out = QPixmap(self.avatar.size())
                out.fill(Qt.GlobalColor.transparent)
                painter = QPainter(out)
                painter.setRenderHint(QPainter.RenderHint.Antialiasing)
                radius = 14 if self.list_mode else 22
                shape = QPainterPath()
                shape.addRoundedRect(0, 0, self.avatar.width(), self.avatar.height(), radius, radius)
                painter.setClipPath(shape)
                painter.drawPixmap(0, 0, pix)
                painter.end()
                self.avatar.setPixmap(out)
                return
        t = get_theme(self.theme_name)
        radius = 14 if self.list_mode else 22
        self.avatar.setText("+")
        self.avatar.setStyleSheet(
            f"background: {t['AVATAR_PLACEHOLDER']}; border: 1px solid {t['BORDER']}; "
            f"border-radius: {radius}px; color: {t['MUTED']}; font-size: 30px;"
        )


class MainWindow(QMainWindow):
    def __init__(self, store, steam):
        super().__init__()
        self.store = store
        self.steam = steam
        self.accounts_data = []
        self.selected_id = None
        self.view_mode = store.settings().get("view", "grid")
        self.sort_mode = store.settings().get("sort", "name_asc")
        self.launch_mode = store.settings().get("launch_mode", "online")
        self.theme_name = store.settings().get("theme", "dark")
        self.language = store.settings().get("language", "pt-BR")
        if self.language not in LANGUAGES:
            self.language = "pt-BR"
        self.icon_size = 60
        self.signals = WorkerSignals()
        self.signals.avatar_ready.connect(self._avatar_ready)

        self.setWindowTitle(APP_NAME)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Window)
        self.setMinimumSize(1000, 700)
        self.resize(1280, 820)
        if ICON_FILE.exists(): self.setWindowIcon(QIcon(str(ICON_FILE)))
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self._window_corner_radius = 20
        self._drag_pos = None
        self._build()
        self.refresh()
        self._start_avatar_fetch()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_steam_status)
        self.timer.start(2500)
        self.update_steam_status()

    def _build(self):
        root = QWidget(); root.setObjectName("Root")
        self.setCentralWidget(root)
        bg = GlowBackground(root, self.theme_name); self.background = bg; bg.lower(); bg.setGeometry(root.rect()); root.resizeEvent = lambda e: (bg.setGeometry(root.rect()), QWidget.resizeEvent(root, e))

        outer = QVBoxLayout(root); outer.setContentsMargins(26, 20, 26, 22); outer.setSpacing(0)
        outer.addWidget(self._titlebar())
        outer.addSpacing(12)
        outer.addWidget(self._header())
        outer.addSpacing(14)
        outer.addWidget(self._content(), 1)
        outer.addSpacing(12)
        outer.addWidget(self._bottom())
        self._apply_style()

    def _titlebar(self):
        # Brand and native-style window controls share the same horizontal line.
        # Only the window controls sit inside the rounded container.
        bar = QFrame(); bar.setFixedHeight(64); bar.setObjectName("Titlebar")
        layout = QHBoxLayout(bar); layout.setContentsMargins(8, 0, 0, 0); layout.setSpacing(0)
        layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        brand = QHBoxLayout(); brand.setSpacing(10); brand.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        if LOGO_FILE.exists():
            logo = QLabel(); logo.setPixmap(QPixmap(str(LOGO_FILE)).scaled(58, 52, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)); brand.addWidget(logo)
        title_block = QVBoxLayout(); title_block.setSpacing(1); title_block.setContentsMargins(0, 0, 0, 0)
        title = QLabel("STEAM SWAPPER"); title.setObjectName("BrandTitle"); title_block.addWidget(title)
        self.brand_sub = QLabel(tr(self.language, "brand_sub")); self.brand_sub.setObjectName("BrandSub"); title_block.addWidget(self.brand_sub)
        brand.addLayout(title_block)
        layout.addLayout(brand)
        layout.addStretch(1)

        controls = QFrame(); controls.setObjectName("TitlebarControls"); controls.setFixedHeight(38)
        controls_layout = QHBoxLayout(controls); controls_layout.setContentsMargins(4, 3, 4, 3); controls_layout.setSpacing(0)
        controls_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        for text, slot, obj in [("—", self.showMinimized, "WinBtn"), ("□", self._toggle_max, "WinBtn"), ("×", self.close, "CloseBtn")]:
            b = QPushButton(text); b.setObjectName(obj); b.setFixedSize(42, 28); b.clicked.connect(slot); controls_layout.addWidget(b)
        layout.addWidget(controls)
        return bar

    def _header(self):
        frame = QFrame(); frame.setObjectName("Header")
        row = QHBoxLayout(frame); row.setContentsMargins(12, 4, 12, 4)
        row.addStretch(1)
        self.steam_status = QLabel(); self.steam_status.setObjectName("SteamStatus"); row.addWidget(self.steam_status)
        row.addSpacing(8)

        self.language_combo = QComboBox(); self.language_combo.setObjectName("LanguageCombo")
        for code in ("pt-BR", "en", "es", "zh"):
            self.language_combo.addItem(f'{LANGUAGES[code]["flag"]}  {LANGUAGES[code]["name"]}', code)
        self.language_combo.setCurrentIndex(["pt-BR","en","es","zh"].index(self.language))
        self.language_combo.currentIndexChanged.connect(self.change_language); self.language_combo.setMinimumWidth(150); row.addWidget(self.language_combo)

        self.theme_button = RoundButton(""); self.theme_button.clicked.connect(self.toggle_theme); row.addWidget(self.theme_button)
        return frame

    def _content(self):
        container = QWidget(); layout = QVBoxLayout(container); layout.setContentsMargins(8, 0, 8, 0); layout.setSpacing(8)
        top = QHBoxLayout();
        heading = QVBoxLayout(); self.section_title = QLabel(tr(self.language, "section")); self.section_title.setObjectName("SectionTitle"); heading.addWidget(self.section_title); self.section_sub = QLabel(tr(self.language, "section_sub")); self.section_sub.setObjectName("SectionSub"); heading.addWidget(self.section_sub)
        top.addLayout(heading); top.addStretch()
        self.search = QLineEdit(); self.search.setPlaceholderText(tr(self.language, "search")); self.search.setFixedWidth(230); self.search.textChanged.connect(self.refresh_cards); top.addWidget(self.search)
        layout.addLayout(top)

        # In icon/grid mode the selected account stays permanently visible above
        # the scrolling account area. Only the secondary accounts scroll.
        self.hero_host = QFrame(); self.hero_host.setObjectName("HeroHost")
        self.hero_host.setStyleSheet("QFrame#HeroHost { background: transparent; border: none; }")
        self.hero_host_layout = QHBoxLayout(self.hero_host)
        self.hero_host_layout.setContentsMargins(0, 0, 0, 0)
        self.hero_host_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(self.hero_host, 0)

        self.scroll = QScrollArea(); self.scroll.setWidgetResizable(True); self.scroll.setFrameShape(QFrame.Shape.NoFrame); self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff); self.scroll.setObjectName("Scroll")
        self.canvas = QWidget(); self.canvas.setObjectName("Canvas"); self.scroll.setWidget(self.canvas)
        self.canvas_layout = QVBoxLayout(self.canvas); self.canvas_layout.setContentsMargins(10, 8, 10, 10); self.canvas_layout.setSpacing(10); self.canvas_layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        layout.addWidget(self.scroll, 1)
        return container

    def _bottom(self):
        frame = QFrame(); frame.setObjectName("Bottom")
        row = QHBoxLayout(frame); row.setContentsMargins(8, 0, 8, 0); row.setSpacing(8)
        self.list_btn = RoundButton("☰"); self.grid_btn = RoundButton("▦")
        self.list_btn.setFixedWidth(48); self.grid_btn.setFixedWidth(48); self.list_btn.clicked.connect(lambda: self.set_view("list")); self.grid_btn.clicked.connect(lambda: self.set_view("grid"))
        row.addWidget(self.list_btn); row.addWidget(self.grid_btn)
        self.sort_label = QLabel(tr(self.language, "sort")); self.sort_label.setObjectName("TinyLabel"); row.addWidget(self.sort_label)
        self.sort_combo = QComboBox(); self.sort_combo.setObjectName("SortCombo"); self._populate_sort_combo(); self.sort_combo.currentIndexChanged.connect(self.change_sort); row.addWidget(self.sort_combo)
        row.addStretch()
        self.status = QLabel("0 " + tr(self.language, "accounts")); self.status.setObjectName("Status"); row.addWidget(self.status)
        self._update_view_buttons()
        return frame

    def _populate_sort_combo(self):
        if not hasattr(self, "sort_combo"): return
        self.sort_combo.blockSignals(True); self.sort_combo.clear()
        self.sort_combo.addItems([tr(self.language,"name_az"), tr(self.language,"name_za"), tr(self.language,"newest"), tr(self.language,"oldest")])
        self.sort_combo.setCurrentIndex(self._sort_index()); self.sort_combo.blockSignals(False)

    def _apply_style(self):
        t = get_theme(self.theme_name)
        bg = t["BG_DARK"]; panel = t["PANEL_ALT"]; text = t["TEXT"]; muted = t["MUTED"]; border = t["BORDER"]; blue = t["STEAM_BLUE"]; blue_hover = t["STEAM_BLUE_HOVER"]
        self.setStyleSheet(f"""
        QWidget#Root {{ background: {bg}; color: {text}; font-family: 'Segoe UI'; border: 1px solid {border}; border-radius: 18px; }}
        QFrame#Titlebar {{ background: transparent; border: none; }}
        QFrame#TitlebarControls {{ background: {t["TITLEBAR_BG"]}; border: 1px solid {t["TITLEBAR_BORDER"]}; border-radius: 14px; }}
        QPushButton#WinBtn, QPushButton#CloseBtn {{ background: transparent; color: {muted}; border: none; border-radius: 8px; font-size: 15px; }}
        QPushButton#WinBtn:hover {{ background: {t["PANEL_HOVER"]}; color: {text}; }}
        QPushButton#CloseBtn:hover {{ background: #9d3030; color: white; }}
        QFrame#Header {{ background: transparent; border: none; }}
        QLabel#BrandTitle {{ color: {text}; font-size: 20px; font-weight: 700; }}
        QLabel#BrandSub, QLabel#SectionSub, QLabel#HeroMeta, QLabel#CardMeta, QLabel#Status, QLabel#TinyLabel {{ color: {muted}; }}
        QLabel#BrandSub {{ font-size: 8px; font-weight: 700; }}
        QPushButton {{ background: {t["CONTROL_BG"]}; color: {text}; border: 1px solid {border}; border-radius: 18px; padding: 8px 16px; font-weight: 600; }}
        QPushButton:hover {{ background: {t["CONTROL_HOVER"]}; border-color: {t["STEAM_BLUE_HOVER"]}; }}
        QPushButton[primary="true"] {{ background: {blue}; color: white; border: 1px solid {blue_hover}; }}
        QPushButton[primary="true"]:hover {{ background: {blue_hover}; color: #071018; }}
        QPushButton#AddAccountButton {{ min-width: 150px; }}
        QLabel#SteamStatus {{ color: {t["GREEN"]}; font-size: 10px; font-weight: 700; }}
        QLabel#SectionTitle {{ color: {text}; font-size: 26px; font-weight: 700; }}
        QLineEdit {{ background: {t["CONTROL_BG"]}; color: {text}; border: 1px solid {border}; border-radius: 18px; padding: 10px 14px; selection-background-color: {blue}; }}
        QScrollArea#Scroll {{ background: transparent; border: none; }}
        QWidget#Canvas {{ background: transparent; }}
        QComboBox {{ background: {t["CONTROL_BG"]}; color: {text}; border: 1px solid {border}; border-radius: 16px; padding: 8px 34px 8px 12px; min-width: 95px; }}
        QComboBox:hover {{ border-color: rgba(102,192,244,90); }}
        QComboBox::drop-down {{ subcontrol-origin: border; subcontrol-position: top right; width: 26px; border: none; background: transparent; }}
        QComboBox::down-arrow {{ width: 8px; height: 8px; }}
        QComboBox#LanguageCombo {{ min-width: 145px; padding-right: 26px; }}
        QComboBox#LanguageCombo::drop-down {{ width: 26px; background: transparent; border: none; }}
        QComboBox QAbstractItemView {{ background: {panel}; color: {text}; border: 1px solid {border}; selection-background-color: {blue}; padding: 4px; }}
        QSlider::groove:horizontal {{ height: 4px; background: {t["BORDER"]}; border-radius: 2px; }}
        QSlider::handle:horizontal {{ width: 12px; margin: -5px 0; border-radius: 6px; background: {blue}; }}
        QLabel#TinyLabel {{ font-size: 8px; font-weight: 700; }}
        QLabel#Status {{ font-size: 8px; }}
        QLabel#HeroBadge {{ color: {blue_hover}; font-size: 9px; font-weight: 700; }}
        QLabel#HeroLaunchLabel {{ color: {muted}; font-size: 8px; font-weight: 700; }}
        QComboBox#HeroLaunch {{ min-width: 250px; padding: 7px 28px 7px 12px; border-radius: 16px; }}
        QLabel#HeroName {{ color: {text}; font-size: 18px; font-weight: 700; }}
        QFrame#HeroCard QLabel#HeroName {{ font-size: 18px; }}
        QLabel#CardName {{ color: {text}; font-size: 12px; font-weight: 700; }}
        QLabel#CardMeta {{ color: {muted}; font-size: 9px; }}
        QFrame#Bottom {{ background: transparent; }}
        """)
        if hasattr(self, "background"): self.background.set_theme(self.theme_name)
        if hasattr(self, "theme_button"): self.theme_button.setText(tr(self.language, "theme_light" if self.theme_name == "dark" else "theme_dark"))
        self._update_status_label()

    def _update_status_label(self):
        if hasattr(self, "status"):
            self.status.setText(f"{len(self.accounts_data)} {tr(self.language,'accounts')} • {self.launch_text()}")

    def _sort_index(self):
        return {"name_asc":0,"name_desc":1,"newest":2,"oldest":3}.get(self.sort_mode,0)

    def refresh(self):
        self.accounts_data = self.store.accounts()
        if self.accounts_data and self.selected_id not in {a.id for a in self.accounts_data}:
            self.selected_id = self.accounts_data[0].id
        if not self.accounts_data: self.selected_id = None
        self.refresh_cards()
        self._update_status_label()

    def _clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            child_layout = item.layout()
            child_widget = item.widget()
            if child_layout:
                self._clear_layout(child_layout)
                child_layout.deleteLater()
            if child_widget:
                child_widget.deleteLater()

    def refresh_cards(self):
        self._clear_layout(self.canvas_layout)
        # Normal account views stay left-aligned; the empty state is centered
        # across the available content area.
        self.canvas_layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        accounts = self._filtered_sorted()
        if not accounts:
            self.canvas_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
            empty = QLabel(f"{tr(self.language, 'no_accounts')}\n\n{tr(self.language, 'empty_sub')}")
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty.setObjectName("Empty")
            empty.setStyleSheet(f"QLabel#Empty {{ color:{get_theme(self.theme_name)['MUTED']}; font-size:14px; padding:40px; }}")
            add = RoundButton("+  " + tr(self.language, "add"), False)
            add.setMinimumWidth(210)
            add.clicked.connect(self.add_account)
            box = QVBoxLayout()
            box.setAlignment(Qt.AlignmentFlag.AlignCenter)
            box.setSpacing(14)
            box.addStretch(1)
            box.addWidget(empty, 0, Qt.AlignmentFlag.AlignCenter)
            box.addWidget(add, 0, Qt.AlignmentFlag.AlignCenter)
            box.addStretch(1)
            self.canvas_layout.addLayout(box)
            return

        selected = next((a for a in accounts if a.id == self.selected_id), accounts[0])
        self.selected_id = selected.id
        if self.view_mode == "list":
            # List mode keeps the selected profile permanently visible above the
            # scrolling rows. The row layout is kept on a single line; when the
            # window is narrower than the controls, horizontal scrolling prevents
            # widgets from colliding instead of shrinking them into each other.
            self.canvas_layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
            self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
            if hasattr(self, "hero_host"):
                self._clear_layout(self.hero_host_layout)
                self.hero_host_layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
                list_width = max(0, self.scroll.viewport().width() - 20)
                list_width = max(list_width, 940)
                hero = HeroAccount(selected, size=72, language=self.language, theme_name=self.theme_name, launch_mode=self.launch_mode, list_mode=True)
                hero.setFixedWidth(list_width)
                hero.switch_requested.connect(self.switch_by_id)
                hero.edit_requested.connect(self.edit_by_id)
                hero.add_requested.connect(self.add_account)
                hero.restart_requested.connect(self.restart_steam)
                hero.mode_changed.connect(self.change_launch_mode)
                self.hero_host_layout.addWidget(hero, 0, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
                self.hero_host.show()

            list_width = max(0, self.scroll.viewport().width() - 20)
            list_width = max(list_width, 940)
            for acc in accounts:
                if acc.id == selected.id:
                    continue
                card = AccountCard(acc, False, 58, theme_name=self.theme_name, list_mode=True)
                card.setFixedWidth(list_width)
                card.clicked.connect(self.select_account)
                self.canvas_layout.addWidget(card, 0, Qt.AlignmentFlag.AlignLeft)

            # Let the scroll area size itself to the actual number of rows.
            # Do not impose an artificial minimum height: otherwise the grid/list
            # can show a large empty overflow area when there are few accounts.
            self.canvas.setMinimumHeight(0)
            self.canvas.setMinimumWidth(max(0, list_width + 20))
            self.canvas.adjustSize()
        else:
            # Icon/grid mode: centered composition with no horizontal overflow.
            self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            self.canvas.setMinimumWidth(0)
            # Icon/grid mode: the selected account is a sticky hero above the
            # scroll area, so it remains visible while the other accounts move.
            self.canvas_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
            self.canvas.setMinimumHeight(0)
            if hasattr(self, "hero_host"):
                self._clear_layout(self.hero_host_layout)
                self.hero_host_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)
                hero = HeroAccount(selected, size=118, language=self.language, theme_name=self.theme_name, launch_mode=self.launch_mode)
                hero.switch_requested.connect(self.switch_by_id)
                hero.edit_requested.connect(self.edit_by_id)
                hero.add_requested.connect(self.add_account)
                hero.restart_requested.connect(self.restart_steam)
                hero.mode_changed.connect(self.change_launch_mode)
                self.hero_host_layout.addWidget(hero)
                self.hero_host.show()
            else:
                hero = HeroAccount(selected, size=118, language=self.language, theme_name=self.theme_name, launch_mode=self.launch_mode)
                hero.switch_requested.connect(self.switch_by_id)
                hero.edit_requested.connect(self.edit_by_id)
                hero.add_requested.connect(self.add_account)
                hero.restart_requested.connect(self.restart_steam)
                hero.mode_changed.connect(self.change_launch_mode)
                self.canvas_layout.addWidget(hero, 0, Qt.AlignmentFlag.AlignHCenter)
            others = [a for a in accounts if a.id != selected.id]
            if others:
                grid_host = QWidget()
                # Keep icon/grid mode centered across the available interface.
                viewport_width = max(760, self.scroll.viewport().width() - 20)
                cols = max(2, min(6, viewport_width // 180))
                card_width = 160
                gap = 42
                grid_width = min(viewport_width, cols * card_width + (cols - 1) * gap + 24)
                grid_host.setMinimumWidth(grid_width)
                grid_host.setMaximumWidth(grid_width)
                grid = QGridLayout(grid_host)
                grid.setHorizontalSpacing(gap)
                grid.setVerticalSpacing(18)
                grid.setContentsMargins(12, 0, 12, 0)
                for i, acc in enumerate(others):
                    card = AccountCard(acc, acc.id == self.selected_id, 90, theme_name=self.theme_name)
                    card.clicked.connect(self.select_account)
                    grid.addWidget(card, i // cols, i % cols, alignment=Qt.AlignmentFlag.AlignCenter)
                self.canvas_layout.addWidget(grid_host, 0, Qt.AlignmentFlag.AlignHCenter)
        self.canvas_layout.addStretch(1)

    def _filtered_sorted(self):
        query = self.search.text().strip().lower() if hasattr(self, 'search') else ''
        accounts = [a for a in self.accounts_data if not query or query in a.name.lower() or query in a.login.lower() or query in a.note.lower()]
        if self.sort_mode == "name_desc": accounts.sort(key=lambda a:(a.name or a.login).lower(), reverse=True)
        elif self.sort_mode == "newest": accounts.sort(key=lambda a:a.added_at or "", reverse=True)
        elif self.sort_mode == "oldest": accounts.sort(key=lambda a:a.added_at or "")
        else: accounts.sort(key=lambda a:(a.name or a.login).lower())
        return accounts

    def select_account(self, account_id): self.selected_id = account_id; self.refresh_cards()
    def switch_by_id(self, account_id): self.selected_id = account_id; self.switch_selected()

    def change_sort(self, index):
        self.sort_mode = ["name_asc","name_desc","newest","oldest"][index]; self.store.save_settings(sort=self.sort_mode); self.refresh_cards()
    def change_launch_mode(self, mode):
        self.launch_mode = mode
        self.store.save_settings(launch_mode=self.launch_mode)
        self._update_status_label()
    def launch_text(self): return tr(self.language, self.launch_mode)
    def set_view(self, mode):
        if mode not in ("list", "grid"):
            return
        self.view_mode = mode
        self.store.save_settings(view=mode)
        self._update_view_buttons()
        # List mode has a deliberately wide horizontal row so its action
        # buttons never overlap. Grid mode returns to the normal viewport.
        if hasattr(self, "scroll"):
            self.scroll.setHorizontalScrollBarPolicy(
                Qt.ScrollBarPolicy.ScrollBarAsNeeded if mode == "list" else Qt.ScrollBarPolicy.ScrollBarAlwaysOff
            )
        # Rebuild the account area immediately so switching between views
        # changes the actual layout, not only the button highlight.
        self.refresh_cards()
    def _update_view_buttons(self):
        if not hasattr(self, "list_btn"):
            return
        self.list_btn.setProperty("primary", self.view_mode == "list")
        self.grid_btn.setProperty("primary", self.view_mode == "grid")
        self.list_btn.style().unpolish(self.list_btn); self.list_btn.style().polish(self.list_btn)
        self.grid_btn.style().unpolish(self.grid_btn); self.grid_btn.style().polish(self.grid_btn)
    def toggle_view(self): self.set_view("list" if self.view_mode == "grid" else "grid")

    def toggle_theme(self):
        self.theme_name = "light" if self.theme_name == "dark" else "dark"
        self.store.save_settings(theme=self.theme_name)
        self._apply_style()
        self.refresh_cards()

    def change_language(self, index):
        code = self.language_combo.itemData(index)
        if not code or code == self.language: return
        self.language = code
        self.store.save_settings(language=self.language)
        self._retranslate_ui()

    def _retranslate_ui(self):
        self.brand_sub.setText(tr(self.language, "brand_sub"))
        self.section_title.setText(tr(self.language, "section"))
        self.section_sub.setText(tr(self.language, "section_sub"))
        self.search.setPlaceholderText(tr(self.language, "search"))
        self.sort_label.setText(tr(self.language, "sort"))
        self._populate_sort_combo()
        self._update_view_buttons()
        self._apply_style(); self.refresh_cards(); self.update_steam_status()

    def update_steam_status(self):
        running = self.steam.is_running(); self.steam_status.setText(tr(self.language, "running") if running else tr(self.language, "steam_offline")); self.steam_status.setStyleSheet(f"color: {'#66c0a0' if running else '#7f8c96'}; font-size:10px; font-weight:700;")

    def _start_avatar_fetch(self):
        exe = self.steam.find_executable()
        for account in self.accounts_data:
            if account.avatar and Path(account.avatar).is_file(): continue
            threading.Thread(target=self._fetch_avatar, args=(account, exe), daemon=True).start()

    def _fetch_avatar(self, account, exe):
        path = fetch_profile_avatar(account, exe)
        self.signals.avatar_ready.emit(account.id, path)

    def _avatar_ready(self, account_id, path):
        if not path: return
        accounts = self.store.accounts(); target = next((a for a in accounts if a.id == account_id), None)
        if target:
            target.avatar = path
            self.store.save_accounts(accounts)
            self.accounts_data = accounts
            self.refresh_cards()

    def add_account(self):
        dialog = AccountDialog(self, None, self.language)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            try: self.store.add(**dialog.payload()); self.refresh(); self._start_avatar_fetch()
            except Exception as exc: StyledMessage(self,tr(self.language,"error_add"),str(exc),error=True,language=self.language).exec()

    def edit_by_id(self, account_id):
        account = next((a for a in self.store.accounts() if a.id == account_id), None)
        if not account: return
        dialog=AccountDialog(self,account,self.language)
        if dialog.exec()==QDialog.DialogCode.Accepted:
            try: self.store.update(account.id,**dialog.payload()); self.refresh(); self._start_avatar_fetch()
            except Exception as exc: StyledMessage(self,tr(self.language,"error_edit"),str(exc),error=True,language=self.language).exec()

    def remove_selected(self):
        if not self.selected_id: return
        account=next((a for a in self.store.accounts() if a.id==self.selected_id),None)
        if not account:return
        if StyledMessage(self,tr(self.language,"remove"),tr(self.language,"remove_text",login=account.login),confirm=True,confirm_key="remove_action",language=self.language).exec()!=QDialog.DialogCode.Accepted:return
        try:self.store.remove(account.id); self.selected_id=None; self.refresh()
        except Exception as exc: StyledMessage(self,tr(self.language,"error_remove"),str(exc),error=True,language=self.language).exec()

    def restart_steam(self):
        exe = self.steam.find_executable()
        if not exe:
            StyledMessage(self, tr(self.language, "restart_title"), tr(self.language, "steam_not_found"), error=True, language=self.language).exec()
            return
        dialog = StyledMessage(
            self,
            tr(self.language, "restart_title"),
            tr(self.language, "steam_restart"),
            confirm=True,
            confirm_key="restart",
            language=self.language,
        )
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        try:
            if not self.steam.close(exe):
                raise RuntimeError("Steam could not be closed completely.")
            self.steam.restart(exe)
            self.status.setText(tr(self.language, "restart_done"))
            QTimer.singleShot(2200, self.update_steam_status)
        except (OSError, RuntimeError) as exc:
            StyledMessage(self, tr(self.language, "restart_title"), str(exc), error=True, language=self.language).exec()

    def switch_selected(self):
        if not self.selected_id:
            StyledMessage(self,tr(self.language,"switch_title"),tr(self.language,"select_first"),error=True,language=self.language).exec(); return
        account=next((a for a in self.store.accounts() if a.id==self.selected_id),None)
        if not account:return
        dialog=StyledMessage(
            self,
            tr(self.language, "switch_title"),
            confirm=True,
            language=self.language,
            confirm_key="switch",
            switch_account=account,
            switch_mode=self.launch_mode,
        )
        if dialog.exec()!=QDialog.DialogCode.Accepted:return
        exe=self.steam.find_executable()
        if not exe:
            StyledMessage(self,"Steam",tr(self.language,"steam_not_found"),error=True,language=self.language).exec(); return
        self.status.setText(tr(self.language,"closing",login=account.login)); QApplication.processEvents()
        try:
            if not self.steam.close(exe): raise RuntimeError("Steam could not be closed completely.")
            self.steam.launch(exe,account.login,self.launch_mode,account.steam_id)
            self.status.setText(tr(self.language,"steam_started",login=account.login,mode=self.launch_text()))
            QTimer.singleShot(2200,self.update_steam_status)
        except (OSError,RuntimeError) as exc:
            StyledMessage(self,tr(self.language,"error_switch"),str(exc),error=True,language=self.language).exec()
            self.status.setText(tr(self.language,"switch_failed"))

    def _update_window_shape(self):
        # The frameless window needs a real native mask so the outermost
        # corners are transparent/rounded instead of only being painted
        # rounded by the central widget. Keep the mask only in windowed mode.
        if self.isMaximized() or self.isFullScreen():
            self.clearMask()
            return

        r = self._window_corner_radius
        w, h = self.width(), self.height()
        region = QRegion(0, 0, w, h, QRegion.RegionType.Rectangle)
        ellipse_tl = QRegion(0, 0, r * 2, r * 2, QRegion.RegionType.Ellipse)
        ellipse_tr = QRegion(w - r * 2, 0, r * 2, r * 2, QRegion.RegionType.Ellipse)
        ellipse_bl = QRegion(0, h - r * 2, r * 2, r * 2, QRegion.RegionType.Ellipse)
        ellipse_br = QRegion(w - r * 2, h - r * 2, r * 2, r * 2, QRegion.RegionType.Ellipse)
        region = region.subtracted(QRegion(0, 0, r, r).subtracted(ellipse_tl))
        region = region.subtracted(QRegion(w - r, 0, r, r).subtracted(ellipse_tr))
        region = region.subtracted(QRegion(0, h - r, r, r).subtracted(ellipse_bl))
        region = region.subtracted(QRegion(w - r, h - r, r, r).subtracted(ellipse_br))
        self.setMask(region)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._update_window_shape()
        # Reflow list/grid widths after the window changes size so content never
        # remains wider than the current viewport in windowed mode.
        if hasattr(self, "_layout_resize_timer"):
            self._layout_resize_timer.stop()
        else:
            self._layout_resize_timer = QTimer(self)
            self._layout_resize_timer.setSingleShot(True)
            self._layout_resize_timer.timeout.connect(self.refresh_cards)
        self._layout_resize_timer.start(80)

    def changeEvent(self, event):
        super().changeEvent(event)
        if event.type() == event.Type.WindowStateChange:
            QTimer.singleShot(0, self._update_window_shape)

    def _toggle_max(self): self.showNormal() if self.isMaximized() else self.showMaximized()
    def mousePressEvent(self,e):
        if e.button()==Qt.MouseButton.LeftButton and e.position().y()<60:self._drag_pos=e.globalPosition().toPoint()-self.frameGeometry().topLeft(); e.accept()
    def mouseMoveEvent(self,e):
        if self._drag_pos is not None and e.buttons() & Qt.MouseButton.LeftButton:self.move(e.globalPosition().toPoint()-self._drag_pos); e.accept()
    def mouseReleaseEvent(self,e): self._drag_pos=None


class StyledDialogBase(QDialog):
    def __init__(self, parent, title, width=460, height=None):
        super().__init__(parent)
        self.dialog_title = title
        self.setWindowTitle(title)
        self.setModal(True)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setFixedWidth(width)
        if height:
            self.setFixedHeight(height)
        self._drag_pos = None

    def build_shell(self):
        t = get_theme(getattr(self.parent(), "theme_name", "dark"))
        root = QFrame(self)
        root.setObjectName("DialogRoot")
        outer = QVBoxLayout(root)
        outer.setContentsMargins(1, 1, 1, 1)
        outer.setSpacing(0)

        header = QFrame()
        header.setObjectName("DialogHeader")
        header.setFixedHeight(50)
        h = QHBoxLayout(header)
        h.setContentsMargins(16, 0, 8, 0)
        title = QLabel(self.dialog_title)
        title.setObjectName("DialogHeaderTitle")
        h.addWidget(title)
        h.addStretch()
        close = QPushButton("×")
        close.setObjectName("DialogClose")
        close.setFixedSize(38, 34)
        close.clicked.connect(self.reject)
        h.addWidget(close)
        outer.addWidget(header)

        self.dialog_body = QWidget()
        self.dialog_body.setObjectName("DialogBodyArea")
        outer.addWidget(self.dialog_body, 1)
        self.setStyleSheet(f"""
        QFrame#DialogRoot {{ background:{t['BG_DARK']}; border:1px solid {t['BORDER']}; border-radius:18px; }}
        QFrame#DialogHeader {{ background:rgba(24,34,43,210); border:none; border-top-left-radius:17px; border-top-right-radius:17px; }}
        QLabel#DialogHeaderTitle {{ color:{t['TEXT']}; font-size:12px; font-weight:700; }}
        QPushButton#DialogClose {{ background:transparent; color:{t['MUTED']}; border:none; border-radius:10px; font-size:24px; font-weight:300; }}
        QPushButton#DialogClose:hover {{ background:rgba(217,83,79,180); color:white; }}
        QWidget#DialogBodyArea {{ background:transparent; border:none; }}
        QLineEdit {{ background:{t['PANEL_ALT']}; border:1px solid {t['BORDER']}; border-radius:14px; padding:11px 13px; color:{t['TEXT']}; selection-background-color:{t['STEAM_BLUE']}; }}
        QLineEdit:focus {{ border-color:{t['STEAM_BLUE_HOVER']}; }}
        QLabel#DialogTitle {{ color:{t['TEXT']}; font-size:17px; font-weight:700; }}
        QLabel#DialogBody {{ color:{t['MUTED']}; font-size:11px; }}
        """)
        self.setLayout(QVBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().addWidget(root)
        return root, self.dialog_body

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and event.position().y() <= 52:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._drag_pos is not None and event.buttons() & Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self._drag_pos = None
        super().mouseReleaseEvent(event)


class AccountDialog(StyledDialogBase):
    def __init__(self, parent, account=None, language="en"):
        self.account = account
        self.language = language
        super().__init__(parent, tr(language, "dialog_edit" if account else "dialog_add"), width=520, height=590)
        self._build()

    def _build(self):
        _, body = self.build_shell()
        t = get_theme(getattr(self.parent(), "theme_name", "dark"))
        layout = QVBoxLayout(body)
        layout.setContentsMargins(30, 24, 30, 28)
        layout.setSpacing(11)
        title = QLabel(tr(self.language, "dialog_edit" if self.account else "dialog_add"))
        title.setObjectName("DialogTitle")
        layout.addWidget(title)

        self.name = QLineEdit(self.account.name if self.account else "")
        self.name.setPlaceholderText(tr(self.language, "profile_name")); layout.addWidget(self.name)
        self.login = QLineEdit(self.account.login if self.account else "")
        self.login.setPlaceholderText(tr(self.language, "steam_login")); layout.addWidget(self.login)
        self.steam_id = QLineEdit(self.account.steam_id if self.account else "")
        self.steam_id.setPlaceholderText(tr(self.language, "steam_id")); layout.addWidget(self.steam_id)
        self.note = QLineEdit(self.account.note if self.account else "")
        self.note.setPlaceholderText(tr(self.language, "note")); layout.addWidget(self.note)

        layout.addStretch(1)
        buttons = QHBoxLayout(); buttons.addStretch()
        cancel = RoundButton(tr(self.language, "cancel"))
        save = RoundButton(tr(self.language, "save"), True)
        cancel.clicked.connect(self.reject); save.clicked.connect(self.accept)
        buttons.addWidget(cancel); buttons.addWidget(save); layout.addLayout(buttons)

    def payload(self):
        return {
            "name": self.name.text().strip() or self.login.text().strip(),
            "login": self.login.text().strip(),
            "steam_id": self.steam_id.text().strip(),
            "note": self.note.text().strip() or "No note",
            "avatar": self.account.avatar if self.account else "",
        }


class StyledMessage(StyledDialogBase):
    def __init__(self, parent, title, text="", confirm=False, error=False, language="en", confirm_key="switch", switch_account=None, switch_mode=None):
        self.message_text = text
        self.confirm = confirm
        self.error = error
        self.language = language
        self.confirm_key = confirm_key
        self.switch_account = switch_account
        self.switch_mode = switch_mode
        dialog_height = 390 if switch_account and confirm else (260 if confirm else 220)
        super().__init__(parent, title, width=560 if switch_account else 470, height=dialog_height)
        self._build()

    def _build(self):
        _, body = self.build_shell()
        t = get_theme(getattr(self.parent(), "theme_name", "dark"))
        layout = QVBoxLayout(body)
        layout.setContentsMargins(30, 24, 30, 28)
        layout.setSpacing(12)

        if self.switch_account and self.confirm:
            eyebrow = QLabel(tr(self.language, "confirm_action"))
            eyebrow.setStyleSheet(f"font-size:8px; font-weight:800; letter-spacing:1px; color:{t['STEAM_BLUE_HOVER']};")
            layout.addWidget(eyebrow)

            accent = QFrame()
            accent.setFixedHeight(3)
            accent.setStyleSheet(f"background:{t['STEAM_BLUE']}; border-radius:2px;")
            layout.addWidget(accent)

            heading = QLabel(tr(self.language, "switch_title"))
            heading.setStyleSheet(f"color:{t['TEXT']}; font-size:19px; font-weight:800;")
            layout.addWidget(heading)

            profile = QFrame()
            profile.setObjectName("SwitchProfile")
            profile.setStyleSheet(f"""
                QFrame#SwitchProfile {{
                    background:{t['PANEL_ALT']};
                    border:1px solid {t['BORDER']};
                    border-radius:18px;
                }}
                QLabel#SwitchName {{ color:{t['TEXT']}; font-size:14px; font-weight:800; }}
                QLabel#SwitchLogin {{ color:{t['MUTED']}; font-size:10px; }}
                QLabel#SwitchNote {{ color:{t['MUTED']}; font-size:9px; }}
                QLabel#ModePill {{
                    background:{t['STEAM_BLUE']}; color:white; border-radius:12px;
                    padding:7px 12px; font-size:9px; font-weight:800;
                }}
            """)
            ph = QHBoxLayout(profile)
            ph.setContentsMargins(14, 12, 14, 12)
            ph.setSpacing(12)

            avatar = QLabel()
            avatar.setFixedSize(58, 58)
            avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
            avatar.setStyleSheet(f"background:{t['AVATAR_PLACEHOLDER']}; border:1px solid {t['BORDER']}; border-radius:14px; color:{t['MUTED']};")
            if self.switch_account.avatar and Path(self.switch_account.avatar).is_file():
                pix = QPixmap(self.switch_account.avatar)
                if not pix.isNull():
                    pix = pix.scaled(58, 58, Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation)
                    out = QPixmap(58, 58); out.fill(Qt.GlobalColor.transparent)
                    painter = QPainter(out); painter.setRenderHint(QPainter.RenderHint.Antialiasing)
                    shape = QPainterPath(); shape.addRoundedRect(0, 0, 58, 58, 14, 14)
                    painter.setClipPath(shape); painter.drawPixmap(0, 0, pix); painter.end()
                    avatar.setPixmap(out)
            ph.addWidget(avatar)

            info = QVBoxLayout(); info.setSpacing(2)
            name = QLabel(self.switch_account.name or self.switch_account.login); name.setObjectName("SwitchName")
            login = QLabel(self.switch_account.login); login.setObjectName("SwitchLogin")
            info.addWidget(name); info.addWidget(login)
            if self.switch_account.note:
                note = QLabel(self.switch_account.note); note.setObjectName("SwitchNote"); info.addWidget(note)
            ph.addLayout(info, 1)

            mode_label = QLabel(tr(self.language, self.switch_mode or "online")); mode_label.setObjectName("ModePill")
            mode_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            ph.addWidget(mode_label, 0, Qt.AlignmentFlag.AlignVCenter)
            layout.addWidget(profile)

            description = QLabel(
                f"{tr(self.language, 'launch_mode')}: <b>{tr(self.language, self.switch_mode or 'online')}</b><br>"
                f"{tr(self.language, 'steam_restart')}"
            )
            description.setTextFormat(Qt.TextFormat.RichText)
            description.setWordWrap(True)
            description.setStyleSheet(f"color:{t['MUTED']}; font-size:10px; line-height:140%;")
            layout.addWidget(description)
            layout.addStretch(1)
        else:
            eyebrow = QLabel(tr(self.language, "error") if self.error else (tr(self.language, "confirm_action") if self.confirm else tr(self.language, "app_label")))
            eyebrow.setStyleSheet(f"font-size:8px; font-weight:800; color:{t['STEAM_BLUE_HOVER']};")
            layout.addWidget(eyebrow)
            body_label = QLabel(self.message_text)
            body_label.setWordWrap(True)
            body_label.setObjectName("DialogBody")
            layout.addWidget(body_label)
            layout.addStretch(1)

        row = QHBoxLayout(); row.addStretch()
        if self.confirm:
            cancel = RoundButton(tr(self.language, "cancel")); cancel.clicked.connect(self.reject); row.addWidget(cancel)
            ok = RoundButton(tr(self.language, self.confirm_key), True); ok.clicked.connect(self.accept); row.addWidget(ok)
        else:
            ok = RoundButton(tr(self.language, "ok"), True); ok.clicked.connect(self.accept); row.addWidget(ok)
        layout.addLayout(row)


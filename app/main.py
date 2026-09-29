import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
from app.config import APP_NAME, ICON_FILE
from app.data.store import AccountStore
from app.services.steam import SteamService
from app.ui.main_window import MainWindow


def run():
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    if ICON_FILE.exists():
        app.setWindowIcon(QIcon(str(ICON_FILE)))
    store = AccountStore()
    steam = SteamService()
    window = MainWindow(store, steam)
    window.show()
    return app.exec()

import sys
import os
import ctypes
from pathlib import Path
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from ui.main_window import MainWindow

def main():
    # Fix taskbar icon grouping on Windows
    if sys.platform == "win32":
        try:
            myappid = "PhotoVideoOrganizer.Organizer.2.1"
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        except Exception:
            pass

    # Enable high-DPI scaling
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    app = QApplication(sys.argv)
    app.setApplicationName("Photo & Video Organizer")
    app.setOrganizationName("PhotoVideoOrganizer")

    # Set Application Icon
    assets_dir = Path(__file__).resolve().parent / "assets"
    for icon_name in ("icon.png", "icon.ico", "icon.svg"):
        icon_file = assets_dir / icon_name
        if icon_file.exists():
            app.setWindowIcon(QIcon(str(icon_file)))
            break

    window = MainWindow()
    window.show()

    sys.exit(app.exec())

if __name__ == '__main__':
    main()

import sys, os
from PySide6.QtWidgets import QApplication
from ui.main_window import MainWindow

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.dirname(__file__)
    return os.path.join(base_path, relative_path)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    style_path = resource_path('assets/style.qss')
    if os.path.exists(style_path):
        with open(style_path, 'r', encoding='utf-8') as f:
            app.setStyleSheet(f.read())
    w = MainWindow(); w.show()
    sys.exit(app.exec())

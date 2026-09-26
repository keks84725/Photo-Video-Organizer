from pathlib import Path
from PySide6.QtWidgets import (
    QPushButton, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QFrame
)
from PySide6.QtGui import QColor, QPainter, QBrush, QPen, QPainterPath, QFont, QPixmap, QIcon
from PySide6.QtCore import Qt, Signal, QRectF, QSize

class NotchBadge(QLabel):
    """The distinctive top notch badge containing 'PHOTO-VIDEO-ORGANIZER'."""
    def __init__(self, text="PHOTO-VIDEO-ORGANIZER", parent=None):
        super().__init__(text, parent)
        self.setFixedHeight(30)
        self.setFixedWidth(248)
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("""
            QLabel {
                background-color: #000000;
                border: 1.5px solid #363D56;
                border-top: none;
                border-bottom-left-radius: 13px;
                border-bottom-right-radius: 13px;
                color: #FFFFFF;
                font-family: 'Times New Roman', 'Georgia', serif;
                font-size: 13px;
                font-weight: bold;
                letter-spacing: 1.2px;
                padding-bottom: 2px;
            }
        """)


class ModeButton(QWidget):
    """Blue gradient mode button with clean subtitle underneath (no outline/border)."""
    clicked = Signal(str)

    def __init__(self, mode_id: str, title: str, subtitle: str, parent=None):
        super().__init__(parent)
        self.mode_id = mode_id
        self.is_active = False

        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 4, 6, 4)
        layout.setSpacing(8)
        layout.setAlignment(Qt.AlignCenter)

        self.btn = QPushButton(title)
        self.btn.setFixedSize(126, 48)
        self.btn.setCursor(Qt.PointingHandCursor)
        self.btn.clicked.connect(lambda: self.clicked.emit(self.mode_id))

        self.label = QLabel(subtitle)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("""
            QLabel {
                color: #FFFFFF;
                font-size: 13px;
                font-weight: 500;
                background: transparent;
                border: none;
                outline: none;
            }
        """)

        layout.addWidget(self.btn, alignment=Qt.AlignCenter)
        layout.addWidget(self.label, alignment=Qt.AlignCenter)

        self.update_style()

    def set_active(self, active: bool):
        self.is_active = active
        self.update_style()

    def update_style(self):
        if self.is_active:
            self.btn.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #4E95FF, stop:1 #2563EB);
                    color: white;
                    font-size: 17px;
                    font-weight: 800;
                    border: 2px solid #93C5FD;
                    border-radius: 16px;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #60A5FA, stop:1 #3B82F6);
                }
            """)
        else:
            self.btn.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #3B82F6, stop:1 #1D4ED8);
                    color: #E2E8F0;
                    font-size: 16px;
                    font-weight: 700;
                    border: 1px solid #1E3A8A;
                    border-radius: 16px;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #4B8CF7, stop:1 #2563EB);
                    border: 1px solid #3B82F6;
                }
            """)


class FolderButton(QPushButton):
    """Deep indigo/purple gradient button for folder selection."""
    def __init__(self, text: str, parent=None):
        super().__init__(text, parent)
        self.setFixedSize(114, 58)
        self.setCursor(Qt.PointingHandCursor)
        self.selected_path = None
        self.base_text = text
        self.update_state()

    def set_path(self, path: str):
        self.selected_path = path
        self.setToolTip(path if path else f"Select {self.base_text} folder")
        self.update_state()

    def update_state(self):
        if self.selected_path:
            self.setText(f"{self.base_text} ✓")
            self.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #6366F1, stop:1 #4338CA);
                    color: #F8FAFC;
                    font-size: 16px;
                    font-weight: 700;
                    border: 2px solid #818CF8;
                    border-radius: 14px;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #7175F7, stop:1 #4F46E5);
                }
            """)
        else:
            self.setText(self.base_text)
            self.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #5651B7, stop:1 #453FA6);
                    color: #FFFFFF;
                    font-size: 16px;
                    font-weight: 600;
                    border: 1px solid #353086;
                    border-radius: 14px;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #635DC7, stop:1 #5048B5);
                    border: 1px solid #6366F1;
                }
                QPushButton:pressed {
                    background-color: #383389;
                }
            """)


class StartCircleButton(QPushButton):
    """Large circular START button with double border matching Image 1."""
    def __init__(self, parent=None):
        super().__init__("START", parent)
        self.setFixedSize(96, 96)
        self.setCursor(Qt.PointingHandCursor)
        self.is_running = False
        self.update_state()

    def set_running(self, running: bool):
        self.is_running = running
        self.setText("STOP" if running else "START")
        self.update_state()

    def update_state(self):
        if self.is_running:
            self.setStyleSheet("""
                QPushButton {
                    background-color: #EF4444;
                    color: white;
                    font-size: 18px;
                    font-weight: 900;
                    border-radius: 48px;
                    border: 8px solid #991B1B;
                }
                QPushButton:hover {
                    background-color: #F87171;
                    border: 8px solid #B91C1C;
                }
            """)
        else:
            self.setStyleSheet("""
                QPushButton {
                    background-color: #34C759;
                    color: white;
                    font-size: 18px;
                    font-weight: 900;
                    border-radius: 48px;
                    border: 8px solid #235D2E;
                }
                QPushButton:hover {
                    background-color: #3DDC64;
                    border: 8px solid #2C743A;
                }
                QPushButton:pressed {
                    background-color: #2BA047;
                }
            """)


class SidePillButton(QPushButton):
    """Top '?' pill button matching Image 1."""
    def __init__(self, parent=None):
        super().__init__("?", parent)
        self.setFixedSize(44, 28)
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet("""
            QPushButton {
                background-color: #3A4261;
                border: 1px solid #4C567D;
                border-radius: 14px;
                color: #FFFFFF;
                font-size: 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #485278;
                border: 1px solid #6370A3;
            }
            QPushButton:pressed {
                background-color: #2B3149;
            }
        """)


class FlagIconButton(QPushButton):
    """Flag icon button that displays full-color SVG flags with clean rounded border."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(44, 30)
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet("""
            QPushButton {
                background-color: #0A0C14;
                border: 1.5px solid #282E47;
                border-radius: 6px;
                padding: 0px;
            }
            QPushButton:hover {
                border: 1.5px solid #60A5FA;
            }
        """)

    def set_flag_svg(self, svg_path: str):
        full_path = Path(__file__).parent.parent / svg_path
        if full_path.exists():
            self.setIcon(QIcon(str(full_path)))
            self.setIconSize(QSize(40, 26))


class TileIconButton(QPushButton):
    """Black rounded square tile matching GitHub and Donate in Image 1."""
    def __init__(self, svg_path: str, title: str = "", parent=None):
        super().__init__(parent)
        self.setFixedSize(44, 44)
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet("""
            QPushButton {
                background-color: #000000;
                border: 1.5px solid #202436;
                border-radius: 10px;
                color: #FFFFFF;
                padding: 3px 0px;
            }
            QPushButton:hover {
                background-color: #121522;
                border: 1.5px solid #40486D;
            }
            QPushButton:pressed {
                background-color: #05060A;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 3, 0, 3)
        layout.setSpacing(1)
        layout.setAlignment(Qt.AlignCenter)

        self.icon_label = QLabel()
        self.icon_label.setAlignment(Qt.AlignCenter)
        self.icon_label.setStyleSheet("background: transparent; border: none;")

        full_path = Path(__file__).parent.parent / svg_path
        if full_path.exists():
            pix = QPixmap(str(full_path)).scaled(22, 22, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.icon_label.setPixmap(pix)

        layout.addWidget(self.icon_label, alignment=Qt.AlignCenter)

        if title:
            self.text_label = QLabel(title)
            self.text_label.setAlignment(Qt.AlignCenter)
            self.text_label.setStyleSheet("color: white; font-size: 9px; font-weight: bold; background: transparent; border: none;")
            layout.addWidget(self.text_label, alignment=Qt.AlignCenter)

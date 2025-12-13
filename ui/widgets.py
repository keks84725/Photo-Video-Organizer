from PySide6.QtWidgets import (
    QPushButton, QProgressBar, QWidget, QLabel, QGraphicsDropShadowEffect
)
from PySide6.QtGui import QColor, QPainter, QPen, Qt as QtGui
from PySide6.QtCore import QPropertyAnimation, QEasingCurve, QRect, QSize, Qt

class AnimatedButton(QPushButton):
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.setStyleSheet("""

            QPushButton {
                background-color: #2C2C2C;
                border: 2px solid #6C5CE7;
                border-radius: 14px;
                padding: 8px 24px;
                color: white;
                font-size: 18px;
            }
        """)
        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(0)
        self.shadow.setColor(QColor("#6C5CE7"))
        self.setGraphicsEffect(self.shadow)

class AnimatedProgressBar(QProgressBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimum(0); self.setMaximum(100)
        self.setStyleSheet("""
            QProgressBar {
                background-color: #1E1E1E;
                border-radius: 12px;
                height: 24px;
                color: white;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #6C5CE7,stop:1 #0984E3);
                border-radius: 12px;
            }
        """)

class CircleButton(QPushButton):
    def __init__(self, number="", parent=None):
        super().__init__(number, parent)
        self.setFixedSize(48, 48)
        self.setStyleSheet("""
            QPushButton {
                background-color: #2A2A2A;
                border-radius: 24px;
                color: white;
                font-size: 18px;
            }
        """)
        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setColor(QColor("#6C5CE7"))
        self.setGraphicsEffect(self.shadow)

class InfoButton(QPushButton):
    def __init__(self, parent=None):
        super().__init__("?", parent)
        self.setFixedSize(40, 40)
        self.setStyleSheet("""
            QPushButton {
                background-color: #2C2C2C;
                border-radius: 20px;
                color: #6C5CE7;
                font-size: 22px;
                font-weight: bold;
            }
        """)
        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setColor(QColor("#6C5CE7"))
        self.setGraphicsEffect(self.shadow)

class IconCircleButton(QWidget):
    def __init__(self, icon_char, color, parent=None):
        super().__init__(parent)
        self.icon = icon_char
        self.color = color
        self.setFixedSize(48, 48)
        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setColor(QColor(color))
        self.setGraphicsEffect(self.shadow)
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QColor("#2A2A2A"))
        painter.drawEllipse(0, 0, self.width(), self.height())
        painter.setPen(QPen(QColor(self.color)))
        painter.drawText(self.rect(), Qt.AlignCenter, self.icon)

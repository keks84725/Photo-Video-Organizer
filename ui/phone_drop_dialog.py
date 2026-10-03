import sys
from pathlib import Path
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QListWidget, QListWidgetItem, QApplication
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QFont, QColor, QIcon, QClipboard

from network.local_drop import LocalDropServer, get_local_ip
from core.qr_gen import generate_qr_pixmap

class PhoneDropDialog(QDialog):
    """
    Wi-Fi Phone Drop Dialog:
    Runs a zero-cloud local HTTP server on LAN, presents a scannable QR code
    and URL for iPhone / Android cameras, and receives media files in real-time.
    """
    def __init__(self, target_dir: Path, lang: str = "EN", parent=None):
        super().__init__(parent)
        self.target_dir = Path(target_dir)
        self.target_dir.mkdir(parents=True, exist_ok=True)
        self.lang = lang
        self.received_count = 0
        self.received_bytes = 0
        self.server_url = ""

        self.setWindowTitle("📱 Wi-Fi Phone Drop")
        self.setFixedSize(480, 640)
        self.setStyleSheet("""
            QDialog {
                background-color: #141726;
                color: #FFFFFF;
            }
            QLabel {
                color: #E2E8F0;
                font-family: 'Segoe UI', -apple-system, sans-serif;
            }
            QFrame {
                border: none;
            }
        """)

        self.init_ui()
        self.start_server()

    def tr(self, en_text: str, ru_text: str, zh_text: str) -> str:
        if self.lang == "RU":
            return ru_text
        elif self.lang == "ZH":
            return zh_text
        return en_text

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(22, 18, 22, 20)
        layout.setSpacing(14)

        # Header Badge & Title
        header_layout = QVBoxLayout()
        header_layout.setSpacing(4)
        header_layout.setAlignment(Qt.AlignCenter)

        title_lbl = QLabel(self.tr("📱 Wi-Fi Phone Drop", "📱 Перенос с телефона по Wi-Fi", "📱 手机 Wi-Fi 快传"))
        title_lbl.setStyleSheet("font-size: 20px; font-weight: 800; color: #FFFFFF;")
        title_lbl.setAlignment(Qt.AlignCenter)

        sub_lbl = QLabel(self.tr(
            "Transfer photos & videos from phone to PC over local Wi-Fi",
            "Прямая передача фото и видео с телефона на ПК по домашнему Wi-Fi",
            "通过局域网 Wi-Fi 从手机无线传输照片与视频到电脑"
        ))
        sub_lbl.setStyleSheet("font-size: 12px; color: #94A3B8;")
        sub_lbl.setAlignment(Qt.AlignCenter)

        header_layout.addWidget(title_lbl)
        header_layout.addWidget(sub_lbl)
        layout.addLayout(header_layout)

        # Center Card with QR Code
        qr_card = QFrame()
        qr_card.setStyleSheet("""
            QFrame {
                background-color: #1F2438;
                border: 1.5px solid #2F3754;
                border-radius: 20px;
            }
        """)
        qr_card_layout = QVBoxLayout(qr_card)
        qr_card_layout.setContentsMargins(16, 14, 16, 14)
        qr_card_layout.setSpacing(10)
        qr_card_layout.setAlignment(Qt.AlignCenter)

        # White square box for QR code (optimizes phone camera contrast)
        self.qr_box = QFrame()
        self.qr_box.setFixedSize(210, 210)
        self.qr_box.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border-radius: 16px;
                border: 2px solid #3B82F6;
            }
        """)
        qr_box_layout = QVBoxLayout(self.qr_box)
        qr_box_layout.setContentsMargins(5, 5, 5, 5)
        qr_box_layout.setAlignment(Qt.AlignCenter)

        self.qr_label = QLabel()
        self.qr_label.setFixedSize(200, 200)
        self.qr_label.setAlignment(Qt.AlignCenter)
        qr_box_layout.addWidget(self.qr_label)
        qr_card_layout.addWidget(self.qr_box, alignment=Qt.AlignCenter)

        # URL Bar with Copy Button
        url_bar = QHBoxLayout()
        url_bar.setSpacing(8)

        self.url_label = QLabel("Starting server...")
        self.url_label.setStyleSheet("""
            QLabel {
                background-color: #141726;
                color: #60A5FA;
                font-family: monospace;
                font-size: 13px;
                font-weight: 700;
                padding: 8px 12px;
                border: 1px solid #2B3454;
                border-radius: 10px;
            }
        """)
        self.url_label.setTextInteractionFlags(Qt.TextSelectableByMouse)

        self.btn_copy = QPushButton(self.tr("Copy", "Копировать", "复制"))
        self.btn_copy.setCursor(Qt.PointingHandCursor)
        self.btn_copy.setStyleSheet("""
            QPushButton {
                background-color: #374151;
                color: #F3F4F6;
                font-size: 12px;
                font-weight: 600;
                padding: 8px 14px;
                border-radius: 10px;
                border: 1px solid #4B5563;
            }
            QPushButton:hover {
                background-color: #4B5563;
            }
        """)
        self.btn_copy.clicked.connect(self.copy_url)

        url_bar.addWidget(self.url_label, stretch=1)
        url_bar.addWidget(self.btn_copy)
        qr_card_layout.addLayout(url_bar)

        hint_lbl = QLabel(self.tr(
            "1. Connect phone to same Wi-Fi  •  2. Scan QR with Camera",
            "1. Подключите телефон к тому же Wi-Fi  •  2. Наведите камеру на QR-код",
            "1. 手机连接同一 Wi-Fi  •  2. 使用相机扫描二维码"
        ))
        hint_lbl.setStyleSheet("font-size: 11px; color: #94A3B8;")
        hint_lbl.setAlignment(Qt.AlignCenter)
        qr_card_layout.addWidget(hint_lbl)

        layout.addWidget(qr_card)

        # Live Received Files List Section
        files_header = QHBoxLayout()
        self.lbl_stats = QLabel(self.tr("📥 Received files (0):", "📥 Получено файлов (0):", "📥 已接收文件 (0):"))
        self.lbl_stats.setStyleSheet("font-size: 13px; font-weight: 700; color: #FFFFFF;")
        files_header.addWidget(self.lbl_stats)

        self.lbl_size = QLabel("")
        self.lbl_size.setStyleSheet("font-size: 12px; color: #34D399; font-weight: 600;")
        files_header.addWidget(self.lbl_size, alignment=Qt.AlignRight)
        layout.addLayout(files_header)

        self.file_list = QListWidget()
        self.file_list.setStyleSheet("""
            QListWidget {
                background-color: #191E30;
                border: 1px solid #2B334D;
                border-radius: 14px;
                padding: 6px;
                color: #CBD5E1;
                font-size: 12px;
            }
            QListWidget::item {
                padding: 6px 10px;
                border-bottom: 1px solid #22283E;
            }
        """)
        self.file_list.setFixedHeight(110)
        layout.addWidget(self.file_list)

        # Action Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)

        self.btn_close = QPushButton(self.tr("Cancel", "Отмена", "取消"))
        self.btn_close.setCursor(Qt.PointingHandCursor)
        self.btn_close.setFixedHeight(44)
        self.btn_close.setStyleSheet("""
            QPushButton {
                background-color: #2D334D;
                color: #E2E8F0;
                font-size: 14px;
                font-weight: 600;
                border-radius: 12px;
                border: 1px solid #3F476C;
            }
            QPushButton:hover {
                background-color: #373E5D;
            }
        """)
        self.btn_close.clicked.connect(self.reject)

        self.btn_done = QPushButton(self.tr(
            "✓ Done & Organize Files",
            "✓ Готово • Начать сортировку",
            "✓ 完成并开始整理"
        ))
        self.btn_done.setCursor(Qt.PointingHandCursor)
        self.btn_done.setFixedHeight(44)
        self.btn_done.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #3B82F6, stop:1 #1D4ED8);
                color: #FFFFFF;
                font-size: 14px;
                font-weight: 700;
                border-radius: 12px;
                border: 1px solid #60A5FA;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #4E95FF, stop:1 #2563EB);
            }
        """)
        self.btn_done.clicked.connect(self.accept)

        btn_layout.addWidget(self.btn_close, stretch=1)
        btn_layout.addWidget(self.btn_done, stretch=2)
        layout.addLayout(btn_layout)

    def start_server(self):
        self.server = LocalDropServer(target_dir=self.target_dir)
        self.server.server_started.connect(self.on_server_started)
        self.server.file_received.connect(self.on_file_received)
        self.server.server_error.connect(self.on_server_error)
        self.server.start()

    def on_server_started(self, ip: str, port: int):
        self.server_url = f"http://{ip}:{port}"
        self.url_label.setText(self.server_url)

        # Render QR code
        pixmap = generate_qr_pixmap(self.server_url, 195)
        if pixmap and not pixmap.isNull():
            self.qr_label.setPixmap(pixmap)

    def on_file_received(self, filename: str, file_size: int):
        self.received_count += 1
        self.received_bytes += file_size

        # Format total bytes
        if self.received_bytes > 1024 * 1024 * 1024:
            size_str = f"{self.received_bytes / (1024 * 1024 * 1024):.2f} GB"
        elif self.received_bytes > 1024 * 1024:
            size_str = f"{self.received_bytes / (1024 * 1024):.1f} MB"
        else:
            size_str = f"{self.received_bytes / 1024:.1f} KB"

        self.lbl_stats.setText(self.tr(
            f"📥 Received files ({self.received_count}):",
            f"📥 Получено файлов ({self.received_count}):",
            f"📥 已接收文件 ({self.received_count}):"
        ))
        self.lbl_size.setText(f"Total: {size_str}")

        # Add item to list
        item = QListWidgetItem(f"✓  {filename} ({file_size // 1024} KB)")
        item.setForeground(QColor("#34D399"))
        self.file_list.addItem(item)
        self.file_list.scrollToBottom()

    def on_server_error(self, err_msg: str):
        self.url_label.setText("Error: " + err_msg)
        self.url_label.setStyleSheet("color: #F87171; font-size: 11px;")

    def copy_url(self):
        if self.server_url:
            QApplication.clipboard().setText(self.server_url)
            self.btn_copy.setText(self.tr("Copied!", "Скопировано!", "已复制!"))

    def stop_server(self):
        if hasattr(self, 'server') and self.server and self.server.isRunning():
            self.server.stop()
            self.server.wait(1000)

    def closeEvent(self, event):
        self.stop_server()
        event.accept()

    def reject(self):
        self.stop_server()
        super().reject()

    def accept(self):
        self.stop_server()
        super().accept()

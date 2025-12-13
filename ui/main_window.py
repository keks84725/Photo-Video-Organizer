from PySide6.QtWidgets import (
    QMainWindow, QWidget, QFileDialog, QGridLayout, QHBoxLayout,
    QMessageBox, QLabel  # ← QLabel теперь импортирован!
)
from PySide6.QtCore import Qt
from ui.widgets import (
    AnimatedButton, AnimatedProgressBar, CircleButton,
    InfoButton, IconCircleButton
)
import webbrowser
from core.workers import ScannerWorker

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Photo & Video Organizer")
        self.setMinimumSize(1200, 750)
        self.setStyleSheet("background-color: #101010;")
        self.media_path = None
        self.temp_path = None

        central = QWidget()
        self.setCentralWidget(central)
        main = QGridLayout()
        central.setLayout(main)

        # Info button
        self.btn_readme = InfoButton()
        self.btn_readme.clicked.connect(self.show_readme)
        main.addWidget(self.btn_readme, 0, 3, alignment=Qt.AlignRight)

        # Circle buttons (1–7)
        circle_layout = QHBoxLayout()
        circle_layout.setSpacing(10)
        self.circle_buttons = []
        for i in range(1, 8):
            btn = CircleButton(str(i))
            self.circle_buttons.append(btn)
            circle_layout.addWidget(btn)
        main.addLayout(circle_layout, 0, 0, 1, 3, alignment=Qt.AlignLeft)

        # Info screen
        self.info_screen = QLabel("Status: waiting for input...")
        self.info_screen.setStyleSheet("""
            QLabel {
                background-color: #1A1A1A;
                color: white;
                border: 2px solid #2E2E2E;
                border-radius: 16px;
                padding: 18px;
                font-size: 17px;
            }
        """)
        self.info_screen.setMinimumHeight(350)
        self.info_screen.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        main.addWidget(self.info_screen, 1, 0, 1, 4)

        # Mode buttons
        mode_layout = QHBoxLayout()
        mode_layout.setSpacing(20)
        self.btn_mode_full = AnimatedButton("Full Scan")
        self.btn_mode_full.clicked.connect(lambda: self.set_mode("full"))
        self.btn_mode_dupes = AnimatedButton("Find Duplicates")
        self.btn_mode_dupes.clicked.connect(lambda: self.set_mode("duplicates"))
        self.btn_mode_trash = AnimatedButton("Find Trash Files")
        self.btn_mode_trash.clicked.connect(lambda: self.set_mode("trash"))
        mode_layout.addWidget(self.btn_mode_full)
        mode_layout.addWidget(self.btn_mode_dupes)
        mode_layout.addWidget(self.btn_mode_trash)
        main.addLayout(mode_layout, 2, 0, 1, 4)

        self.current_mode = None

        # Folder selection
        folder_layout = QHBoxLayout()
        folder_layout.setSpacing(20)
        self.btn_media = AnimatedButton("Select MEDIA Folder")
        self.btn_media.clicked.connect(self.select_media)
        self.btn_temp = AnimatedButton("Select TEMP Folder")
        self.btn_temp.clicked.connect(self.select_temp)
        folder_layout.addWidget(self.btn_media)
        folder_layout.addWidget(self.btn_temp)
        main.addLayout(folder_layout, 3, 0, 1, 4)

        # Start button
        self.btn_start = AnimatedButton("START")
        self.btn_start.clicked.connect(self.start_scan)
        self.btn_start.setFixedHeight(60)
        main.addWidget(self.btn_start, 4, 0, 1, 4)

        # Progress bar
        self.progress = AnimatedProgressBar()
        main.addWidget(self.progress, 5, 0, 1, 4)

        # Footer buttons
        self.btn_github = IconCircleButton("G", "#6C5CE7")
        self.btn_github.mousePressEvent = lambda e: webbrowser.open("https://github.com/keks84725/Photo-Video-Organizer")
        main.addWidget(self.btn_github, 6, 2, alignment=Qt.AlignRight)

        self.btn_donate = IconCircleButton("❤", "#FF4F4F")
        self.btn_donate.mousePressEvent = lambda e: webbrowser.open("https://www.donationalerts.com/r/keks84725")
        main.addWidget(self.btn_donate, 6, 3, alignment=Qt.AlignRight)

    def show_readme(self):
        QMessageBox.information(
            self,
            "ReadMe",
            (
                "Photo & Video Organizer — бесплатное приложение.\n\n"
                "КАК ИСПОЛЬЗОВАТЬ:\n"
                "• MEDIA Folder — папка с файлами (например, 'temp')\n"
                "• TEMP Folder — родительская папка (например, 'Photos')\n\n"
                "Full Scan создаёт:\n"
                " • 2025/12/\n"
                " • Screenshots/\n"
                " • Compressed_Media/\n"
                " • Unsorted/Double/\n"
                " • Unsorted/OtherFiles/\n\n"
                "✅ Ничего не удаляется — только перемещение!"
            )
        )

    def set_mode(self, mode):
        self.current_mode = mode
        self.info_screen.setText(f"Mode selected: {mode}")

    def select_media(self):
        path = QFileDialog.getExistingDirectory(self, "Select MEDIA Folder")
        if path:
            self.media_path = path
            self.btn_media.setText(f"MEDIA: {path}")

    def select_temp(self):
        path = QFileDialog.getExistingDirectory(self, "Select TEMP Folder")
        if path:
            self.temp_path = path
            self.btn_temp.setText(f"TEMP: {path}")

    def update_info(self, text):
        current = self.info_screen.text()
        new = f"{current}\n{text}"
        # Ограничиваем длину, чтобы не тормозить интерфейс
        if len(new) > 3000:
            new = new[-3000:]
        self.info_screen.setText(new)

    def start_scan(self):
        if not self.current_mode:
            QMessageBox.warning(self, "Error", "Select scan mode!")
            return
        if not self.media_path:
            QMessageBox.warning(self, "Error", "MEDIA folder not selected!")
            return
        if not self.temp_path:
            QMessageBox.warning(self, "Error", "TEMP folder not selected!")
            return

        # Блокируем кнопки
        self.btn_start.setEnabled(False)
        self.btn_mode_full.setEnabled(False)
        self.btn_mode_dupes.setEnabled(False)
        self.btn_mode_trash.setEnabled(False)
        self.btn_start.setText("WORKING...")

        # Запуск воркера
        self.worker = ScannerWorker(self.current_mode, self.media_path, self.temp_path)
        self.worker.progress.connect(lambda v: self.progress.setAnimatedValue(v))
        self.worker.message.connect(self.update_info)
        self.worker.finished.connect(self.scan_finished)
        self.worker.error.connect(self.scan_error)
        self.worker.start()

    def scan_finished(self, results):
        self.update_info("=== Finished ===")
        moved = results.get("moved", [])
        self.update_info(f"✅ Moved: {len(moved)} files")
        self.update_info(f"   Screenshots: {results.get('screenshots', 0)}")
        self.update_info(f"   Compressed: {results.get('compressed', 0)}")
        self.update_info(f"   Other: {results.get('other', 0)}")
        self.update_info(f"   Duplicates: {results.get('duplicates', 0)}")
        self.update_info(f"   Sorted: {results.get('sorted', 0)}")

        # Разблокируем UI
        self.btn_start.setEnabled(True)
        self.btn_mode_full.setEnabled(True)
        self.btn_mode_dupes.setEnabled(True)
        self.btn_mode_trash.setEnabled(True)
        self.btn_start.setText("DONE")
        self.btn_start.setStyleSheet("QPushButton { background-color: #00FFAA; color: #0b0b0b; font-weight:bold; }")

    def scan_error(self, err_text):
        self.update_info(f"❌ ERROR: {err_text}")
        self.btn_start.setEnabled(True)
        self.btn_mode_full.setEnabled(True)
        self.btn_mode_dupes.setEnabled(True)
        self.btn_mode_trash.setEnabled(True)
        self.btn_start.setText("ERROR")
        self.btn_start.setStyleSheet("QPushButton { background-color: #FF7675; color: white; font-weight:bold; }")
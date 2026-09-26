import sys
import webbrowser
from pathlib import Path

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QTextEdit, QProgressBar, QFileDialog, QMessageBox, QFrame
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon, QTextCursor

from .widgets import (
    NotchBadge, ModeButton, FolderButton,
    StartCircleButton, SidePillButton, FlagIconButton, TileIconButton
)
from core.workers import ScannerWorker
from core.config import load_config, save_config
from core.file_utils import undo_last_run

LANGUAGES = ["EN", "RU", "ZH"]
LANG_FLAGS = {
    "EN": "assets/flag_en.svg",
    "RU": "assets/flag_ru.svg",
    "ZH": "assets/flag_zh.svg"
}

TRANSLATIONS = {
    "EN": {
        "status_ready": "",
        "status_processing": "Processing: {current} / {total} files ({pct}%)",
        "status_completed": "Completed successfully! 🎉",
        "status_error": "Error: {err}",
        "full_sub": "Full Check",
        "dup_sub": "Duplicate Check",
        "other_sub": "Other Check",
        "mode_selected": "Mode: {mode}",
        "folder_selected": "📁 {key}: {path}",
        "missing_temp": "Please select the 'Temp' folder containing your photos and videos first!",
        "missing_media": "Please select the 'Media' destination folder for sorted photos & videos!",
        "help_title": "Help / Information",
        "help_content": (
            "<h3>Photo & Video Organizer</h3>"
            "<p><b>Folders:</b></p>"
            "<ul>"
            "<li><b>Temp:</b> Source directory with unorganized photos and videos.</li>"
            "<li><b>Media:</b> Target library organized by Year/Month.</li>"
            "<li><b>Duplicate:</b> Folder for identical files based on SHA-256 hash.</li>"
            "<li><b>Other:</b> Folder for screenshots (&lt;100KB or keyword) and non-media.</li>"
            "</ul>"
            "<p><b>Modes:</b></p>"
            "<ul>"
            "<li><b>FULL:</b> Organizes media by date, moves duplicates & screenshots.</li>"
            "<li><b>DUPLICATE:</b> Only checks for duplicates.</li>"
            "<li><b>OTHER:</b> Extracts screenshots and unsupported files.</li>"
            "</ul>"
        ),
        "undo_btn": "Undo Last Sort",
        "undo_success": "Successfully restored {count} files back to their original locations!",
        "undo_none": "No previous operation history found to undo."
    },
    "RU": {
        "status_ready": "",
        "status_processing": "Обработка: {current} / {total} файлов ({pct}%)",
        "status_completed": "Сортировка успешно завершена! 🎉",
        "status_error": "Ошибка: {err}",
        "full_sub": "Полная проверка",
        "dup_sub": "Поиск дубликатов",
        "other_sub": "Прочие файлы",
        "mode_selected": "Режим: {mode}",
        "folder_selected": "📁 {key}: {path}",
        "missing_temp": "Сначала выберите исходную папку 'Temp' с файлами!",
        "missing_media": "Выберите целевую папку 'Media' для отсортированных фото и видео!",
        "help_title": "Помощь / Справка",
        "help_content": (
            "<h3>Организатор фото и видео</h3>"
            "<p><b>Папки:</b></p>"
            "<ul>"
            "<li><b>Temp:</b> Исходная папка с несортированными медиафайлами.</li>"
            "<li><b>Media:</b> Папка назначения со структурой Год/Месяц.</li>"
            "<li><b>Duplicate:</b> Папка для одинаковых файлов (хэш SHA-256).</li>"
            "<li><b>Other:</b> Папка для скриншотов (&lt;100КБ или по ключевым словам) и прочего.</li>"
            "</ul>"
            "<p><b>Режимы:</b></p>"
            "<ul>"
            "<li><b>FULL:</b> Полная сортировка по датам EXIF + отсев дубликатов и скриншотов.</li>"
            "<li><b>DUPLICATE:</b> Только поиск и перемещение дубликатов.</li>"
            "<li><b>OTHER:</b> Вынос скриншотов и неподдерживаемых файлов.</li>"
            "</ul>"
        ),
        "undo_btn": "Отменить последнюю сортировку",
        "undo_success": "Успешно возвращено {count} файлов в исходные папки!",
        "undo_none": "История предыдущей сортировки не найдена."
    },
    "ZH": {
        "status_ready": "",
        "status_processing": "正在处理：{current} / {total} 个文件 ({pct}%)",
        "status_completed": "整理成功完成！🎉",
        "status_error": "错误：{err}",
        "full_sub": "全盘检查",
        "dup_sub": "重复检查",
        "other_sub": "其他文件",
        "mode_selected": "模式：{mode}",
        "folder_selected": "📁 {key}：{path}",
        "missing_temp": "请先选择包含照片和视频的 'Temp' 源文件夹！",
        "missing_media": "请选择存放整理结果的 'Media' 目标文件夹！",
        "help_title": "帮助与说明",
        "help_content": (
            "<h3>照片与视频整理器 (Photo & Video Organizer)</h3>"
            "<p><b>文件夹说明：</b></p>"
            "<ul>"
            "<li><b>Temp：</b> 存放未整理照片和视频的源文件夹。</li>"
            "<li><b>Media：</b> 整理后按 年/月 归档的目标媒体库。</li>"
            "<li><b>Duplicate：</b> 基于 SHA-256 哈希识别出的完全相同文件。</li>"
            "<li><b>Other：</b> 屏幕截图（&lt;100KB 或关键词）及不支持格式的文件。</li>"
            "</ul>"
            "<p><b>运行模式：</b></p>"
            "<ul>"
            "<li><b>FULL：</b> 全功能处理，按 EXIF 日期归档，隔离重复项与截图。</li>"
            "<li><b>DUPLICATE：</b> 仅扫描并隔离重复文件。</li>"
            "<li><b>OTHER：</b> 仅提取截图与非媒体格式文件。</li>"
            "</ul>"
        ),
        "undo_btn": "撤销上次整理",
        "undo_success": "已成功将 {count} 个文件恢复到原始位置！",
        "undo_none": "未找到可撤销的历史记录。"
    }
}

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Photo & Video Organizer")
        self.setFixedSize(585, 720)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #141726;
            }
            QLabel {
                background: transparent;
                border: none;
                outline: none;
            }
            QToolTip {
                background-color: #1F2438;
                color: #FFFFFF;
                border: 1px solid #3F476C;
                padding: 6px;
                border-radius: 6px;
                font-size: 12px;
            }
        """)

        # Load persisted config
        self.config = load_config()
        self.current_lang_idx = LANGUAGES.index(self.config.get("language", "EN")) if self.config.get("language") in LANGUAGES else 0
        self.current_mode = self.config.get("mode", "full")
        self.worker = None

        self.paths = {
            "temp": self.config.get("temp_path", ""),
            "media": self.config.get("media_path", ""),
            "duplicate": self.config.get("duplicate_path", ""),
            "other": self.config.get("other_path", "")
        }

        self.init_ui()
        self.restore_paths_ui()

    @property
    def current_lang(self) -> str:
        return LANGUAGES[self.current_lang_idx]

    def tr(self, key: str) -> str:
        return TRANSLATIONS[self.current_lang].get(key, "")

    def init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(18, 14, 18, 18)
        main_layout.setSpacing(14)

        # ----------------------------------------------------
        # TOP CARD: Clean Screen with Top Center Notch Badge
        # ----------------------------------------------------
        self.screen_card = QFrame()
        self.screen_card.setFixedHeight(265)
        self.screen_card.setStyleSheet("""
            QFrame {
                background-color: #313754;
                border-radius: 24px;
                border: 1px solid #3D4466;
            }
        """)
        screen_layout = QVBoxLayout(self.screen_card)
        screen_layout.setContentsMargins(0, 0, 0, 12)
        screen_layout.setSpacing(6)

        # Top Notch attached flush to top border
        notch_container = QHBoxLayout()
        notch_container.setContentsMargins(0, 0, 0, 0)
        notch_container.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
        self.notch_widget = NotchBadge("PHOTO-VIDEO-ORGANIZER")
        notch_container.addWidget(self.notch_widget)
        screen_layout.addLayout(notch_container)

        # Seamless Integrated Console (matches screen background exactly)
        self.console = QTextEdit()
        self.console.setReadOnly(True)
        self.console.setStyleSheet("""
            QTextEdit {
                background-color: transparent;
                color: #CBD5E1;
                font-family: 'Segoe UI', -apple-system, sans-serif;
                font-size: 12px;
                border: none;
                padding: 10px 18px;
            }
        """)
        screen_layout.addWidget(self.console, stretch=1)

        # Minimal Progress Bar (visible only when processing)
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedHeight(6)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                background-color: #242A42;
                border-radius: 3px;
                border: none;
                margin: 0px 18px;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #3B82F6, stop:1 #10B981);
                border-radius: 3px;
            }
        """)
        screen_layout.addWidget(self.progress_bar)

        main_layout.addWidget(self.screen_card)

        # ----------------------------------------------------
        # MIDDLE CARD: Mode Selection (FULL, DUPLICATE, OTHER)
        # ----------------------------------------------------
        self.mode_card = QFrame()
        self.mode_card.setFixedHeight(102)
        self.mode_card.setStyleSheet("""
            QFrame {
                background-color: #191D30;
                border: 1.5px solid #282E47;
                border-radius: 20px;
            }
        """)
        mode_layout = QHBoxLayout(self.mode_card)
        mode_layout.setContentsMargins(12, 6, 12, 6)
        mode_layout.setSpacing(10)

        self.btn_mode_full = ModeButton("full", "FULL", self.tr("full_sub"))
        self.btn_mode_duplicate = ModeButton("duplicate", "DUPLICATE", self.tr("dup_sub"))
        self.btn_mode_other = ModeButton("other", "OTHER", self.tr("other_sub"))

        self.btn_mode_full.clicked.connect(self.set_mode)
        self.btn_mode_duplicate.clicked.connect(self.set_mode)
        self.btn_mode_other.clicked.connect(self.set_mode)

        mode_layout.addWidget(self.btn_mode_full)
        mode_layout.addWidget(self.btn_mode_duplicate)
        mode_layout.addWidget(self.btn_mode_other)

        self.set_mode(self.current_mode)
        main_layout.addWidget(self.mode_card)

        # ----------------------------------------------------
        # BOTTOM SECTION: Folder Buttons + START + Utility Icons
        # ----------------------------------------------------
        bottom_container = QHBoxLayout()
        bottom_container.setSpacing(12)

        # Left Card: Folders + START button
        self.bottom_card = QFrame()
        self.bottom_card.setStyleSheet("""
            QFrame {
                background-color: #242A42;
                border: 1.5px solid #2E3553;
                border-radius: 24px;
            }
        """)
        bottom_card_layout = QHBoxLayout(self.bottom_card)
        bottom_card_layout.setContentsMargins(20, 16, 20, 16)
        bottom_card_layout.setSpacing(20)

        # 2x2 Grid of Folder Buttons (Media, Temp, Duplicate, Other)
        folder_grid = QGridLayout()
        folder_grid.setHorizontalSpacing(16)
        folder_grid.setVerticalSpacing(14)

        self.btn_media = FolderButton("Media")
        self.btn_temp = FolderButton("Temp")
        self.btn_duplicate = FolderButton("Duplicate")
        self.btn_other = FolderButton("Other")

        self.btn_media.clicked.connect(lambda: self.select_folder("media", self.btn_media))
        self.btn_temp.clicked.connect(lambda: self.select_folder("temp", self.btn_temp))
        self.btn_duplicate.clicked.connect(lambda: self.select_folder("duplicate", self.btn_duplicate))
        self.btn_other.clicked.connect(lambda: self.select_folder("other", self.btn_other))

        folder_grid.addWidget(self.btn_media, 0, 0)
        folder_grid.addWidget(self.btn_temp, 0, 1)
        folder_grid.addWidget(self.btn_duplicate, 1, 0)
        folder_grid.addWidget(self.btn_other, 1, 1)

        bottom_card_layout.addLayout(folder_grid)

        # Big Circular START Button
        self.btn_start = StartCircleButton()
        self.btn_start.clicked.connect(self.toggle_start)
        bottom_card_layout.addWidget(self.btn_start, alignment=Qt.AlignCenter)

        bottom_container.addWidget(self.bottom_card, stretch=1)

        # Right Vertical Utility Toolbar
        util_layout = QVBoxLayout()
        util_layout.setContentsMargins(0, 2, 0, 2)
        util_layout.setSpacing(10)
        util_layout.setAlignment(Qt.AlignCenter)

        # 1. '?' Pill button
        self.btn_help = SidePillButton()
        self.btn_help.setToolTip("Help / Information")
        self.btn_help.clicked.connect(self.show_help)
        util_layout.addWidget(self.btn_help)

        # 2. Flag button (Full color SVG UK / RU / ZH)
        self.btn_flag = FlagIconButton()
        self.btn_flag.set_flag_svg(LANG_FLAGS[self.current_lang])
        self.btn_flag.setToolTip("Switch Language (EN / RU / ZH)")
        self.btn_flag.clicked.connect(self.cycle_language)
        util_layout.addWidget(self.btn_flag)

        # 3. GitHub button (Octocat + "GitHub" text)
        self.btn_github = TileIconButton("assets/github.svg", "GitHub")
        self.btn_github.setToolTip("GitHub Repository")
        self.btn_github.clicked.connect(self.open_github)
        util_layout.addWidget(self.btn_github)

        # 4. Donate button (Hand holding dollar coin)
        self.btn_donate = TileIconButton("assets/donate.svg", "")
        self.btn_donate.setToolTip("Support Developer")
        self.btn_donate.clicked.connect(self.open_donate)
        util_layout.addWidget(self.btn_donate)

        bottom_container.addLayout(util_layout)
        main_layout.addLayout(bottom_container)

    def restore_paths_ui(self):
        for key, btn in [("media", self.btn_media), ("temp", self.btn_temp),
                         ("duplicate", self.btn_duplicate), ("other", self.btn_other)]:
            p = self.paths.get(key)
            if p and Path(p).exists():
                btn.set_path(p)

    def cycle_language(self):
        self.current_lang_idx = (self.current_lang_idx + 1) % len(LANGUAGES)
        self.btn_flag.set_flag_svg(LANG_FLAGS[self.current_lang])

        self.btn_mode_full.label.setText(self.tr("full_sub"))
        self.btn_mode_duplicate.label.setText(self.tr("dup_sub"))
        self.btn_mode_other.label.setText(self.tr("other_sub"))

        self.config["language"] = self.current_lang
        save_config(self.config)

    def set_mode(self, mode_id: str):
        self.current_mode = mode_id
        self.btn_mode_full.set_active(mode_id == "full")
        self.btn_mode_duplicate.set_active(mode_id == "duplicate")
        self.btn_mode_other.set_active(mode_id == "other")

        self.config["mode"] = mode_id
        save_config(self.config)

    def select_folder(self, key: str, button: FolderButton):
        folder = QFileDialog.getExistingDirectory(self, f"Select {key.capitalize()} Folder")
        if folder:
            self.paths[key] = folder
            button.set_path(folder)
            self.config[f"{key}_path"] = folder
            save_config(self.config)

    def toggle_start(self):
        if self.worker and self.worker.isRunning():
            self.worker.cancel()
            self.btn_start.set_running(False)
            self.console.append("<span style='color: #F87171;'>🛑 Stopped by user.</span>")
            return

        if not self.paths["temp"]:
            QMessageBox.warning(self, "Warning", self.tr("missing_temp"))
            return

        if self.current_mode == "full" and not self.paths["media"]:
            QMessageBox.warning(self, "Warning", self.tr("missing_media"))
            return

        self.console.clear()
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.btn_start.set_running(True)

        self.worker = ScannerWorker(
            mode=self.current_mode,
            temp_path=self.paths["temp"],
            media_path=self.paths["media"],
            duplicate_path=self.paths["duplicate"],
            other_path=self.paths["other"]
        )

        self.worker.log_message.connect(self.on_log)
        self.worker.progress_changed.connect(self.on_progress)
        self.worker.finished_success.connect(self.on_finished)
        self.worker.error_occurred.connect(self.on_error)

        self.worker.start()

    def on_log(self, msg: str):
        self.console.append(msg)
        self.console.moveCursor(QTextCursor.End)

    def on_progress(self, current: int, total: int):
        pct = int((current / total) * 100) if total > 0 else 0
        self.progress_bar.setValue(pct)

    def on_finished(self, stats: dict):
        self.btn_start.set_running(False)
        self.progress_bar.setValue(100)

    def on_error(self, err: str):
        self.btn_start.set_running(False)
        QMessageBox.critical(self, "Error", f"Error: {err}")

    def show_help(self):
        box = QMessageBox(self)
        box.setWindowTitle(self.tr("help_title"))
        box.setTextFormat(Qt.RichText)
        box.setText(self.tr("help_content"))

        undo_btn = box.addButton(self.tr("undo_btn"), QMessageBox.ActionRole)
        box.addButton(QMessageBox.Ok)

        box.exec()

        if box.clickedButton() == undo_btn:
            self.execute_undo()

    def execute_undo(self):
        if not self.paths["temp"]:
            QMessageBox.information(self, "Undo", self.tr("missing_temp"))
            return

        hist_file = Path(self.paths["temp"]) / ".organizer_last_run.json"
        restored, errors = undo_last_run(hist_file)

        if restored > 0:
            QMessageBox.information(self, "Undo", self.tr("undo_success").format(count=restored))
            self.console.append(f"<span style='color: #10B981;'>↩️ Undo completed: {restored} files restored!</span>")
        else:
            QMessageBox.information(self, "Undo", self.tr("undo_none"))

    def open_github(self):
        webbrowser.open("https://github.com/keks84725/Photo-Video-Organizer")

    def open_donate(self):
        webbrowser.open("https://github.com/keks84725")

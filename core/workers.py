from PySide6.QtCore import QThread, Signal
from pathlib import Path
from .file_utils import (
    is_media_file, is_screenshot, is_small_file,
    is_duplicate_in_folder, safe_move_to
)

class ScannerWorker(QThread):
    progress = Signal(int)
    message = Signal(str)
    finished = Signal(dict)
    error = Signal(str)

    def __init__(self, mode: str, media_path: str, temp_path: str):
        super().__init__()
        self.mode = mode
        self.media_root = Path(media_path)   # ← КУДА: media/2025/12/
        self.temp_root = Path(temp_path)     # ← ОТКУДА: temp/
        # Папки — ВСЕ внутри temp/other/ (как в KB)
        self.other_root = self.temp_root / "other"
        self.screenshots_path = self.other_root / "screenshots"
        self.compressed_path = self.other_root / "compressed"
        self.duplicates_path = self.other_root / "duplicates"
        self.other_files_path = self.other_root / "other_files"

    def safe_iterdir(self, path: Path):
        """Безопасное сканирование — без зависаний"""
        try:
            for item in path.rglob('*'):
                if item.is_file():
                    yield item
        except Exception as e:
            self.message.emit(f"⚠️ Skipped {path}: {e}")

    def run(self):
        try:
            self.message.emit("🔍 Scanning TEMP folder...")
            files = list(self.safe_iterdir(self.temp_root))  # ← ТОЛЬКО TEMP!
            total = len(files)
            self.message.emit(f"✅ Found {total} files. Starting '{self.mode}'...")

            results = {
                "moved": [], "screenshots": 0, "compressed": 0,
                "other": 0, "duplicates": 0, "sorted": 0
            }

            if self.mode == "duplicates":
                self._process_duplicates(files, results, total)
            elif self.mode == "trash":
                self._process_trash(files, results, total)
            elif self.mode == "full":
                self._process_full(files, results, total)

            self.progress.emit(100)
            self.message.emit("✅ All done!")
            self.finished.emit(results)

        except Exception as e:
            self.error.emit(str(e))

    def _update_progress(self, start_pct, end_pct, current, total):
        if total <= 0:
            return
        pct = start_pct + (end_pct - start_pct) * (current / total)
        self.progress.emit(int(pct))

    def _process_duplicates(self, files, results, total):
        media_files = [f for f in files if is_media_file(f)]
        for i, f in enumerate(media_files):
            try:
                # Дата из имени или системной даты (EXIF — опционально, можно добавить позже)
                from datetime import datetime
                ctime = f.stat().st_ctime
                mtime = f.stat().st_mtime
                ts = min(ctime, mtime)
                dt = datetime.fromtimestamp(ts)
                target_folder = self.media_root / f"{dt.year}" / f"{dt.month:02d}"
                if is_duplicate_in_folder(f, target_folder):
                    tgt = safe_move_to(f, self.duplicates_path)
                    if tgt:
                        results["moved"].append((f, tgt))
                        results["duplicates"] += 1
                        self.message.emit(f"🔁 Duplicate: {f.name}")
            except Exception as e:
                self.message.emit(f"Skip {f.name}: {e}")
            self._update_progress(0, 100, i + 1, len(media_files))

    def _process_trash(self, files, results, total):
        for i, f in enumerate(files):
            try:
                if is_screenshot(f):
                    tgt = safe_move_to(f, self.screenshots_path)
                    if tgt:
                        results["moved"].append((f, tgt))
                        results["screenshots"] += 1
                        self.message.emit(f"📸 Screenshot: {f.name}")
                elif is_small_file(f) and is_media_file(f):
                    tgt = safe_move_to(f, self.compressed_path)
                    if tgt:
                        results["moved"].append((f, tgt))
                        results["compressed"] += 1
                        self.message.emit(f"📦 <100KB: {f.name}")
                elif not is_media_file(f):
                    tgt = safe_move_to(f, self.other_files_path)
                    if tgt:
                        results["moved"].append((f, tgt))
                        results["other"] += 1
                        self.message.emit(f"🗑️ Other: {f.name}")
            except Exception as e:
                self.message.emit(f"Skip {f.name}: {e}")
            self._update_progress(0, 100, i + 1, total)

    def _process_full(self, files, results, total):
        # 1. Скриншоты (0–15%)
        screenshots = [f for f in files if is_screenshot(f)]
        for i, f in enumerate(screenshots):
            tgt = safe_move_to(f, self.screenshots_path)
            if tgt:
                results["moved"].append((f, tgt))
                results["screenshots"] += 1
                self.message.emit(f"📸 Screenshot: {f.name}")
            self._update_progress(0, 15, i + 1, max(1, len(screenshots)))

        # 2. Мелкие медиа + другие файлы (15–35%)
        rest = [f for f in files if f not in screenshots]
        for i, f in enumerate(rest):
            try:
                if is_small_file(f) and is_media_file(f):
                    tgt = safe_move_to(f, self.compressed_path)
                    if tgt:
                        results["moved"].append((f, tgt))
                        results["compressed"] += 1
                elif not is_media_file(f):
                    tgt = safe_move_to(f, self.other_files_path)
                    if tgt:
                        results["moved"].append((f, tgt))
                        results["other"] += 1
            except:
                pass
            self._update_progress(15, 35, i + 1, max(1, len(rest)))

        # 3. Сортировка медиа (35–100%)
        media_files = [f for f in rest if is_media_file(f)]
        for i, f in enumerate(media_files):
            try:
                # Дата — min(ctime, mtime), как в PS
                from datetime import datetime
                ctime = f.stat().st_ctime
                mtime = f.stat().st_mtime
                ts = min(ctime, mtime)
                dt = datetime.fromtimestamp(ts)
                target_folder = self.media_root / f"{dt.year}" / f"{dt.month:02d}"
                if is_duplicate_in_folder(f, target_folder):
                    tgt = safe_move_to(f, self.duplicates_path)
                    if tgt:
                        results["moved"].append((f, tgt))
                        results["duplicates"] += 1
                        self.message.emit(f"🔁 Duplicate: {f.name}")
                else:
                    tgt = safe_move_to(f, target_folder)
                    if tgt:
                        results["moved"].append((f, tgt))
                        results["sorted"] += 1
                        self.message.emit(f"📅 Sorted: {f.name}")
            except Exception as e:
                self.message.emit(f"Skip {f.name}: {e}")
            self._update_progress(35, 100, i + 1, max(1, len(media_files)))
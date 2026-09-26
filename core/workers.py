from pathlib import Path
from PySide6.QtCore import QThread, Signal

from .file_utils import (
    is_media_file, is_screenshot, is_small_file,
    get_file_hash, get_media_date, safe_move_file,
    generate_thumbnail, save_history
)

class ScannerWorker(QThread):
    log_message = Signal(str)
    progress_changed = Signal(int, int)  # current, total
    stats_updated = Signal(dict)
    thumbnail_ready = Signal(str)        # path to generated thumbnail
    finished_success = Signal(dict)
    error_occurred = Signal(str)

    def __init__(self, mode: str, temp_path: str, media_path: str, duplicate_path: str, other_path: str):
        super().__init__()
        self.mode = mode.lower()
        self.temp_dir = Path(temp_path) if temp_path else None
        self.media_dir = Path(media_path) if media_path else None
        self.duplicate_dir = Path(duplicate_path) if duplicate_path else None
        self.other_dir = Path(other_path) if other_path else None
        self._is_cancelled = False
        self.manifest = []

    def cancel(self):
        self._is_cancelled = True

    def run(self):
        try:
            if not self.temp_dir or not self.temp_dir.exists():
                self.error_occurred.emit("Temp folder is not selected or does not exist!")
                return

            self.log_message.emit(f"🚀 Starting task: {self.mode.upper()} mode")
            self.log_message.emit(f"📂 Scanning folder: {self.temp_dir}")

            all_files = []
            for p in self.temp_dir.rglob('*'):
                if self._is_cancelled:
                    self.log_message.emit("🛑 Process cancelled by user.")
                    return
                # Do not scan history json or hidden files
                if p.is_file() and not p.name.startswith('.'):
                    all_files.append(p)

            total = len(all_files)
            if total == 0:
                self.log_message.emit("ℹ️ No files found in the Temp folder.")
                self.finished_success.emit({"total": 0, "processed": 0})
                return

            self.log_message.emit(f"📊 Found {total} files to process.")

            stats = {
                "total": total,
                "processed": 0,
                "sorted_media": 0,
                "screenshots": 0,
                "duplicates": 0,
                "other_files": 0
            }

            known_hashes = {}
            if self.media_dir and self.media_dir.exists():
                self.log_message.emit("🔍 Indexing existing Media library for duplicates...")
                for existing in self.media_dir.rglob('*'):
                    if self._is_cancelled:
                        return
                    if existing.is_file() and not existing.name.startswith('.'):
                        h = get_file_hash(existing)
                        if h:
                            known_hashes[h] = existing

            for idx, file_path in enumerate(all_files, 1):
                if self._is_cancelled:
                    self.log_message.emit("🛑 Process cancelled by user.")
                    return

                self.progress_changed.emit(idx, total)
                stats["processed"] = idx

                # Generate thumbnail preview
                thumb = generate_thumbnail(file_path)
                if thumb:
                    self.thumbnail_ready.emit(thumb)

                # 1. Check for duplicates
                f_hash = get_file_hash(file_path)
                if f_hash and f_hash in known_hashes:
                    dest_folder = self.duplicate_dir or (self.temp_dir / "Duplicates")
                    moved = safe_move_file(file_path, dest_folder)
                    self.manifest.append({"src": str(file_path), "dest": str(moved)})
                    stats["duplicates"] += 1
                    self.log_message.emit(f"👯 <span style='color:#FBBF24;'>[DUPLICATE]</span> {file_path.name} ➔ Duplicates/")
                    self.stats_updated.emit(stats)
                    continue

                if f_hash:
                    known_hashes[f_hash] = file_path

                # 2. Check for screenshots or compressed small files
                if is_screenshot(file_path) or is_small_file(file_path):
                    if self.mode in ("full", "other"):
                        dest_folder = (self.other_dir or (self.temp_dir / "Other")) / "Screenshots"
                        moved = safe_move_file(file_path, dest_folder)
                        self.manifest.append({"src": str(file_path), "dest": str(moved)})
                        stats["screenshots"] += 1
                        self.log_message.emit(f"📸 <span style='color:#A78BFA;'>[SCREENSHOT]</span> {file_path.name} ➔ Other/Screenshots/")
                        self.stats_updated.emit(stats)
                        continue

                # 3. Check if it's media or non-media
                if not is_media_file(file_path):
                    if self.mode in ("full", "other"):
                        dest_folder = (self.other_dir or (self.temp_dir / "Other")) / "NonMedia"
                        moved = safe_move_file(file_path, dest_folder)
                        self.manifest.append({"src": str(file_path), "dest": str(moved)})
                        stats["other_files"] += 1
                        self.log_message.emit(f"📄 <span style='color:#9CA3AF;'>[OTHER]</span> {file_path.name} ➔ Other/NonMedia/")
                        self.stats_updated.emit(stats)
                        continue
                    else:
                        continue

                # 4. If media and mode is FULL -> Sort into Year/Month
                if self.mode == "full":
                    if self.media_dir:
                        dt = get_media_date(file_path)
                        year_str = dt.strftime('%Y')
                        month_str = dt.strftime('%m')
                        dest_folder = self.media_dir / year_str / month_str
                        moved = safe_move_file(file_path, dest_folder)
                        self.manifest.append({"src": str(file_path), "dest": str(moved)})
                        stats["sorted_media"] += 1
                        self.log_message.emit(f"✨ <span style='color:#34D399;'>[SORTED]</span> {file_path.name} ➔ {year_str}/{month_str}/")
                        self.stats_updated.emit(stats)

            # Save history manifest for undo
            if self.manifest and self.temp_dir:
                save_history(self.manifest, self.temp_dir)

            self.log_message.emit("🎉 <span style='color:#10B981; font-weight:bold;'>Operation completed successfully!</span>")
            self.log_message.emit(
                f"📈 <b>Summary:</b> Media: {stats['sorted_media']} | Duplicates: {stats['duplicates']} | "
                f"Screenshots: {stats['screenshots']} | Other: {stats['other_files']}"
            )
            self.finished_success.emit(stats)

        except Exception as e:
            self.error_occurred.emit(str(e))
            self.log_message.emit(f"❌ Error: {e}")

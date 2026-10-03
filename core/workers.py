from pathlib import Path

try:
    from PySide6.QtCore import QThread, Signal
except ImportError:
    class SignalInstance:
        def __init__(self):
            self._callbacks = []
        def emit(self, *args, **kwargs):
            for cb in list(self._callbacks):
                cb(*args, **kwargs)
        def connect(self, fn):
            self._callbacks.append(fn)

    class Signal:
        def __init__(self, *args):
            pass
        def __get__(self, instance, owner):
            if instance is None:
                return self
            if not hasattr(instance, '_signal_instances'):
                instance._signal_instances = {}
            if id(self) not in instance._signal_instances:
                instance._signal_instances[id(self)] = SignalInstance()
            return instance._signal_instances[id(self)]

    class QThread:
        def __init__(self):
            pass
        def start(self):
            self.run()
        def isRunning(self):
            return False

from .file_utils import (
    is_media_file, is_screenshot, is_small_file,
    get_file_hash, get_media_date, safe_move_file,
    generate_thumbnail, save_history
)
from .takeout_healer import heal_media_file, find_json_sidecar

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

            # Process media files first so Takeout JSON sidecars remain available during healing
            all_files.sort(key=lambda p: (0 if is_media_file(p) else 1, p.name.lower()))

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
                "other_files": 0,
                "takeout_healed": 0,
                "json_cleaned": 0
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

                # File might have been cleaned up if it was a sidecar .json
                if not file_path.exists():
                    continue

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
                # Note: Takeout photos or files with JSON sidecars are authentic photos and should not be treated as screenshots
                has_sidecar = bool(find_json_sidecar(file_path)) if is_media_file(file_path) else False
                if is_screenshot(file_path) or (is_small_file(file_path) and not has_sidecar and self.mode != "takeout"):
                    if self.mode in ("full", "other", "takeout"):
                        dest_folder = (self.other_dir or (self.temp_dir / "Other")) / "Screenshots"
                        moved = safe_move_file(file_path, dest_folder)
                        self.manifest.append({"src": str(file_path), "dest": str(moved)})
                        stats["screenshots"] += 1
                        self.log_message.emit(f"📸 <span style='color:#A78BFA;'>[SCREENSHOT]</span> {file_path.name} ➔ Other/Screenshots/")
                        self.stats_updated.emit(stats)
                        continue

                # 3. Check if it's media or non-media
                if not is_media_file(file_path):
                    if file_path.suffix.lower() == ".json" and self.mode in ("takeout", "full"):
                        # Standalone / orphan JSON metadata file from Takeout
                        dest_folder = (self.other_dir or (self.temp_dir / "Other")) / "TakeoutMetadata"
                        moved = safe_move_file(file_path, dest_folder)
                        self.manifest.append({"src": str(file_path), "dest": str(moved)})
                        stats["other_files"] += 1
                        stats["json_cleaned"] += 1
                        self.stats_updated.emit(stats)
                        continue

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

                # 4. If media and mode is FULL or TAKEOUT -> Heal Takeout & Sort into Year/Month
                if self.mode in ("full", "takeout"):
                    if self.media_dir:
                        # Attempt to heal Google Takeout JSON sidecars
                        dt, meta, json_path = heal_media_file(file_path)
                        if meta:
                            stats["takeout_healed"] += 1
                            if json_path and json_path.exists():
                                try:
                                    json_path.unlink(missing_ok=True)
                                    stats["json_cleaned"] += 1
                                except OSError:
                                    pass
                            self.log_message.emit(
                                f"🩹 <span style='color:#38BDF8;'>[TAKEOUT HEALED]</span> {file_path.name} "
                                f"(Date: {dt.strftime('%Y-%m-%d')}, JSON cleaned)"
                            )

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
            summary_parts = [
                f"Media: {stats['sorted_media']}",
                f"Duplicates: {stats['duplicates']}",
                f"Screenshots: {stats['screenshots']}"
            ]
            if stats["takeout_healed"] > 0:
                summary_parts.append(f"Takeout Healed: {stats['takeout_healed']}")
            if stats["json_cleaned"] > 0:
                summary_parts.append(f"JSON Cleaned: {stats['json_cleaned']}")
            if stats["other_files"] > 0:
                summary_parts.append(f"Other: {stats['other_files']}")

            self.log_message.emit(f"📈 <b>Summary:</b> {' | '.join(summary_parts)}")
            self.finished_success.emit(stats)

        except Exception as e:
            self.error_occurred.emit(str(e))
            self.log_message.emit(f"❌ Error: {e}")

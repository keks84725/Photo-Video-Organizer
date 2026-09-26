import os
import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Tuple

PHOTO_EXTENSIONS = {
    '.jpg', '.jpeg', '.jpe', '.jfif', '.png', '.bmp', '.tiff', '.tif',
    '.gif', '.webp', '.heic', '.heif', '.raw', '.arw', '.cr2', '.cr3',
    '.nef', '.nrw', '.dng', '.orf', '.raf', '.rw2', '.pef', '.srf',
    '.sr2', '.mrw', '.dcr', '.x3f', '.erf', '.mdc', '.psd', '.ai', '.eps'
}

VIDEO_EXTENSIONS = {
    '.mp4', '.m4v', '.mov', '.avi', '.wmv', '.mpg', '.mpeg', '.m2ts',
    '.mts', '.mkv', '.flv', '.f4v', '.webm', '.vob', '.ogv', '.3gp',
    '.3g2', '.mxf', '.ts'
}

MEDIA_EXTENSIONS = PHOTO_EXTENSIONS | VIDEO_EXTENSIONS

SCREENSHOT_KEYWORDS = [
    'screenshot', 'скриншот', 'screen shot', 'скрин', 'снимок экрана',
    'screencap', 'screen_cap', 'screengrab', 'screen_grab', 'snapshot',
    'screencapture', 'printscreen', 'prntscrn', 'capture', 'ss'
]

def is_media_file(path: Path) -> bool:
    return path.suffix.lower() in MEDIA_EXTENSIONS

def is_photo(path: Path) -> bool:
    return path.suffix.lower() in PHOTO_EXTENSIONS

def is_video(path: Path) -> bool:
    return path.suffix.lower() in VIDEO_EXTENSIONS

def is_screenshot(path: Path) -> bool:
    name_lower = path.stem.lower()
    for kw in SCREENSHOT_KEYWORDS:
        if kw in name_lower:
            return True
    return False

def is_small_file(path: Path, max_kb: int = 100) -> bool:
    try:
        return path.stat().st_size < (max_kb * 1024)
    except OSError:
        return False

def get_file_hash(path: Path, chunk_size: int = 65536) -> str:
    """Calculate SHA-256 hash of a file for duplicate detection."""
    sha256 = hashlib.sha256()
    try:
        with open(path, 'rb') as f:
            while chunk := f.read(chunk_size):
                sha256.update(chunk)
        return sha256.hexdigest()
    except Exception:
        return ""

def get_media_date(path: Path) -> datetime:
    """Extract creation date via EXIF or fallback to file system timestamps."""
    if is_photo(path):
        try:
            from PIL import Image, ExifTags
            with Image.open(path) as img:
                exif_data = img._getexif()
                if exif_data:
                    for tag_id, value in exif_data.items():
                        tag_name = ExifTags.TAGS.get(tag_id, tag_id)
                        if tag_name in ('DateTimeOriginal', 'DateTimeDigitized', 'DateTime'):
                            if isinstance(value, str):
                                try:
                                    return datetime.strptime(value[:19], '%Y:%m:%d %H:%M:%S')
                                except ValueError:
                                    pass
        except Exception:
            pass

    try:
        stat = path.stat()
        mtime = datetime.fromtimestamp(stat.st_mtime)
        ctime = datetime.fromtimestamp(stat.st_ctime)
        return min(mtime, ctime)
    except Exception:
        return datetime.now()

def safe_move_file(source: Path, target_dir: Path) -> Path:
    """Safely move a file, auto-renaming if a file with the same name already exists."""
    target_dir.mkdir(parents=True, exist_ok=True)
    destination = target_dir / source.name

    if not destination.exists():
        source.rename(destination)
        return destination

    base_name = source.stem
    ext = source.suffix
    counter = 1
    while destination.exists():
        destination = target_dir / f"{base_name}_{counter}{ext}"
        counter += 1

    source.rename(destination)
    return destination

def generate_thumbnail(path: Path, size=(120, 120)) -> Optional[str]:
    """Generates a small thumbnail image and returns its path in cache, if supported."""
    if not is_photo(path):
        return None
    try:
        from PIL import Image
        cache_dir = Path.home() / ".photo_video_organizer_cache"
        cache_dir.mkdir(parents=True, exist_ok=True)
        thumb_path = cache_dir / f"thumb_{path.stem[:20]}_{hash(str(path)) % 10000}.jpg"
        if thumb_path.exists():
            return str(thumb_path)

        with Image.open(path) as img:
            img.thumbnail(size)
            rgb_img = img.convert('RGB')
            rgb_img.save(thumb_path, "JPEG", quality=80)
            return str(thumb_path)
    except Exception:
        return None

def save_history(manifest: List[Dict[str, str]], log_dir: Path) -> Path:
    """Saves move operations to an undo history file."""
    history_file = log_dir / ".organizer_last_run.json"
    try:
        with open(history_file, "w", encoding="utf-8") as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "moves": manifest
            }, f, indent=2, ensure_ascii=False)
        return history_file
    except Exception:
        return None

def undo_last_run(history_file: Path) -> Tuple[int, List[str]]:
    """Restores files moved during the last run based on the history JSON."""
    if not history_file.exists():
        return 0, ["History file not found."]

    try:
        with open(history_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        moves = data.get("moves", [])
        restored = 0
        errors = []

        for item in reversed(moves):
            src_orig = Path(item["src"])
            current_dest = Path(item["dest"])
            if current_dest.exists():
                src_orig.parent.mkdir(parents=True, exist_ok=True)
                current_dest.rename(src_orig)
                restored += 1
            else:
                errors.append(f"Missing file: {current_dest.name}")

        history_file.unlink(missing_ok=True)
        return restored, errors
    except Exception as e:
        return 0, [str(e)]

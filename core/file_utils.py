from pathlib import Path

# Поддерживаемые расширения — как в KB
MEDIA_EXT = {
    '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.heic',
    '.cr2', '.nef', '.arw', '.dng',
    '.mp4', '.mov', '.avi', '.mkv', '.webm', '.ts'
}

# Ключевые слова для скриншотов — точный список из KB
SCREENSHOT_KEYWORDS = {
    'screenshot', 'screen', 'скрин', 'printscreen', 'prnt', 'ss', 'capture',
    'screencap', 'screen_cap', 'screengrab', 'screen_grab', 'snapshot',
    'screencapture', 'prntscrn', 'запись экрана', 'снимок экрана'
}

def is_media_file(path: Path) -> bool:
    return path.suffix.lower() in MEDIA_EXT

def is_small_file(path: Path) -> bool:
    """Менее 100 KB — для compressed/other"""
    try:
        return path.stat().st_size < 100 * 1024
    except:
        return False

def is_screenshot(path: Path) -> bool:
    """ТОЛЬКО по имени — без ограничения по размеру"""
    name = path.stem.lower()
    return any(kw in name for kw in SCREENSHOT_KEYWORDS)

def is_duplicate_in_folder(file_path: Path, target_folder: Path) -> bool:
    """Только имя + размер — как в PowerShell"""
    target = target_folder / file_path.name
    if not target.exists():
        return False
    try:
        return target.stat().st_size == file_path.stat().st_size
    except:
        return False

def safe_move_to(file_path: Path, target_folder: Path) -> Path | None:
    target_folder.mkdir(parents=True, exist_ok=True)
    target = target_folder / file_path.name
    if target.exists():
        stem, ext = target.stem, target.suffix
        i = 1
        while (target_folder / f"{stem}({i}){ext}").exists():
            i += 1
        target = target_folder / f"{stem}({i}){ext}"
    try:
        import shutil
        shutil.move(str(file_path), str(target))
        return target
    except:
        return None
import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, Tuple

from .file_utils import is_photo, is_media_file

def find_json_sidecar(media_path: Path) -> Optional[Path]:
    """
    Finds the associated Google Takeout JSON sidecar file for a given media file.
    Handles Google Takeout's idiosyncratic naming conventions:
      - photo.jpg -> photo.jpg.json
      - photo.jpg -> photo.json
      - 47/51 character title truncations
      - photo-edited.jpg -> photo.jpg.json
      - photo(1).jpg -> photo.jpg(1).json or photo(1).jpg.json
    """
    parent = media_path.parent
    name = media_path.name
    stem = media_path.stem
    ext = media_path.suffix

    candidates = [
        parent / f"{name}.json",
        parent / f"{stem}.json",
    ]

    # Google Takeout length truncation (typically at 47-51 chars)
    if len(name) > 47:
        candidates.append(parent / f"{name[:47]}.json")
    if len(stem) > 47:
        candidates.append(parent / f"{stem[:47]}.json")

    # Edited versions (e.g. photo-edited.jpg -> photo.jpg.json)
    if "-edited" in stem.lower():
        orig_stem = re.sub(r"-edited$", "", stem, flags=re.IGNORECASE)
        candidates.append(parent / f"{orig_stem}{ext}.json")
        candidates.append(parent / f"{orig_stem}.json")

    # Numbered copies: IMG_001(1).jpg -> IMG_001.jpg(1).json, IMG_001(1).jpg.json, IMG_001(1).json
    m = re.search(r"^(.*?)\((\d+)\)$", stem)
    if m:
        base, idx = m.group(1), m.group(2)
        candidates.append(parent / f"{base}{ext}({idx}).json")
        candidates.append(parent / f"{base}({idx}){ext}.json")
        candidates.append(parent / f"{base}({idx}).json")

    for cand in candidates:
        if cand.exists() and cand.is_file():
            return cand

    # Case-insensitive fallback search in the same directory
    target_lower = f"{name}.json".lower()
    try:
        for f in parent.iterdir():
            if f.is_file() and f.name.lower() == target_lower:
                return f
    except OSError:
        pass

    return None

def parse_takeout_json(json_path: Path) -> Optional[Dict[str, Any]]:
    """
    Parses a Google Takeout JSON sidecar and extracts authentic creation timestamp,
    GPS coordinates, and user descriptions.
    """
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        taken_dt = None
        # 1. Primary: photoTakenTime.timestamp
        if "photoTakenTime" in data and "timestamp" in data["photoTakenTime"]:
            try:
                ts = float(data["photoTakenTime"]["timestamp"])
                if ts > 0:
                    taken_dt = datetime.fromtimestamp(ts)
            except (ValueError, TypeError, OSError):
                pass

        # 2. Secondary: creationTime.timestamp
        if not taken_dt and "creationTime" in data and "timestamp" in data["creationTime"]:
            try:
                ts = float(data["creationTime"]["timestamp"])
                if ts > 0:
                    taken_dt = datetime.fromtimestamp(ts)
            except (ValueError, TypeError, OSError):
                pass

        if not taken_dt:
            return None

        # GPS coordinates
        lat = None
        lon = None
        alt = None
        geo = data.get("geoData") or data.get("geoDataExif")
        if geo:
            try:
                raw_lat = float(geo.get("latitude", 0.0))
                raw_lon = float(geo.get("longitude", 0.0))
                raw_alt = float(geo.get("altitude", 0.0))
                # Skip (0, 0) "Null Island"
                if not (abs(raw_lat) < 0.0001 and abs(raw_lon) < 0.0001):
                    lat = raw_lat
                    lon = raw_lon
                    alt = raw_alt
            except (ValueError, TypeError):
                pass

        description = str(data.get("description", "")).strip()

        return {
            "date": taken_dt,
            "timestamp": taken_dt.timestamp(),
            "latitude": lat,
            "longitude": lon,
            "altitude": alt,
            "description": description,
            "title": data.get("title", "")
        }
    except Exception:
        return None

def _deg_to_dms(deg_val: float) -> Tuple[Tuple[int, int], Tuple[int, int], Tuple[int, int]]:
    """Converts decimal degrees to (deg, min, sec) rational tuples for EXIF."""
    abs_deg = abs(deg_val)
    d = int(abs_deg)
    rem_min = (abs_deg - d) * 60
    m = int(rem_min)
    s = round((rem_min - m) * 60, 4)
    return ((d, 1), (m, 1), (int(s * 10000), 10000))

def apply_metadata_to_file(media_path: Path, meta: Dict[str, Any]) -> bool:
    """
    Applies authentic timestamp and GPS to the media file:
    1. Sets filesystem mtime/atime via os.utime.
    2. Writes DateTimeOriginal, DateTimeDigitized, and GPS tags into EXIF via Pillow if supported.
    """
    success = False
    ts = meta.get("timestamp")

    # 1. Update OS filesystem timestamps
    if ts:
        try:
            os.utime(media_path, (ts, ts))
            success = True
        except OSError:
            pass

    # 2. Update EXIF tags for photos (JPEG, PNG, TIFF, WEBP)
    if is_photo(media_path):
        try:
            from PIL import Image
            dt = meta.get("date")
            if dt:
                date_str = dt.strftime("%Y:%m:%d %H:%M:%S")
                with Image.open(media_path) as img:
                    exif = img.getexif()

                    # 306 = DateTime, 36867 = DateTimeOriginal, 36868 = DateTimeDigitized
                    exif[306] = date_str
                    exif[36867] = date_str
                    exif[36868] = date_str

                    desc = meta.get("description")
                    if desc:
                        exif[270] = desc  # ImageDescription

                    # GPS tags (IFD 34853)
                    lat = meta.get("latitude")
                    lon = meta.get("longitude")
                    if lat is not None and lon is not None:
                        gps_ifd = {}
                        gps_ifd[1] = "N" if lat >= 0 else "S"
                        gps_ifd[2] = _deg_to_dms(lat)
                        gps_ifd[3] = "E" if lon >= 0 else "W"
                        gps_ifd[4] = _deg_to_dms(lon)
                        alt = meta.get("altitude")
                        if alt is not None:
                            gps_ifd[5] = b"\x00" if alt >= 0 else b"\x01"
                            gps_ifd[6] = (int(abs(alt) * 100), 100)

                        exif[34853] = gps_ifd

                    # Save updated EXIF back to image
                    format_name = img.format or "JPEG"
                    if format_name.upper() in ("JPEG", "JPG", "TIFF", "WEBP"):
                        img.save(media_path, format=format_name, exif=exif)

            success = True
        except Exception:
            # Fallback to filesystem timestamp
            pass

    return success

def heal_media_file(media_path: Path) -> Tuple[datetime, Optional[Dict[str, Any]], Optional[Path]]:
    """
    Attempts to heal a single media file using its Google Takeout JSON sidecar.
    Returns: (resolved_datetime, metadata_dict_or_None, json_path_or_None)
    """
    json_path = find_json_sidecar(media_path)
    if json_path:
        meta = parse_takeout_json(json_path)
        if meta:
            apply_metadata_to_file(media_path, meta)
            return meta["date"], meta, json_path

    # Fallback to standard EXIF or OS timestamps
    from .file_utils import get_media_date
    return get_media_date(media_path), None, None

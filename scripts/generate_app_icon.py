#!/usr/bin/env python3
"""
Generate multi-resolution Windows ICO and PNG assets from assets/icon.svg.
Produces:
  - assets/icon.png (256x256)
  - assets/icon.ico (Multi-size: 16x16, 24x24, 32x32, 48x48, 64x64, 128x128, 256x256)
"""
import os
import shutil
import struct
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
SVG_FILE = ASSETS / "icon.svg"
PNG_FILE = ASSETS / "icon.png"
ICO_FILE = ASSETS / "icon.ico"

SIZES = [16, 24, 32, 48, 64, 128, 256]

def pack_ico(png_dict: dict) -> bytes:
    """
    Packs a dictionary of {size: png_bytes} into a standard multi-resolution Windows ICO.
    """
    count = len(png_dict)
    # Header: 2 bytes reserved (0), 2 bytes type (1 for icon), 2 bytes image count
    header = struct.pack("<HHH", 0, 1, count)
    
    entries = bytearray()
    images_data = bytearray()
    
    # Calculate offset where image data begins
    offset = 6 + (16 * count)
    
    for size, data in sorted(png_dict.items(), key=lambda x: x[0]):
        width_byte = 0 if size >= 256 else size
        height_byte = 0 if size >= 256 else size
        color_count = 0
        reserved = 0
        planes = 1
        bpp = 32
        data_len = len(data)
        
        # Directory entry: 16 bytes
        entry = struct.pack(
            "<BBBBHHII",
            width_byte, height_byte, color_count, reserved,
            planes, bpp, data_len, offset
        )
        entries.extend(entry)
        images_data.extend(data)
        offset += data_len
        
    return header + bytes(entries) + bytes(images_data)

def generate_with_sips():
    """Generates PNGs and ICO on macOS using native sips tool."""
    temp_dir = Path(tempfile.mkdtemp(prefix="organizer_icon_"))
    try:
        # 1. Rasterize master 256x256 PNG
        subprocess.run(["sips", "-s", "format", "png", str(SVG_FILE), "--out", str(PNG_FILE)], check=True)
        
        png_dict = {}
        for sz in SIZES:
            target_png = temp_dir / f"icon_{sz}.png"
            if sz == 256:
                shutil.copy(PNG_FILE, target_png)
            else:
                subprocess.run(["sips", "-z", str(sz), str(sz), str(PNG_FILE), "--out", str(target_png)], check=True)
            png_dict[sz] = target_png.read_bytes()
            
        ico_bytes = pack_ico(png_dict)
        ICO_FILE.write_bytes(ico_bytes)
        print(f"✅ Generated {ICO_FILE} ({len(ico_bytes)} bytes, {len(png_dict)} sizes)")
        return True
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

def generate_with_pillow():
    """Fallback generator using Pillow if available."""
    try:
        from PIL import Image
        if PNG_FILE.exists():
            img = Image.open(PNG_FILE)
            ico_sizes = [(s, s) for s in SIZES]
            img.save(ICO_FILE, format="ICO", sizes=ico_sizes)
            print(f"✅ Generated {ICO_FILE} via Pillow")
            return True
    except Exception as e:
        print(f"Pillow fallback failed: {e}", file=sys.stderr)
    return False

def main():
    if not SVG_FILE.exists():
        print(f"ERROR: {SVG_FILE} does not exist!", file=sys.stderr)
        sys.exit(1)
        
    if shutil.which("sips"):
        if generate_with_sips():
            return
            
    if generate_with_pillow():
        return
        
    print("Warning: Could not rasterize SVG. Keeping existing PNG/ICO if present.")

if __name__ == "__main__":
    main()

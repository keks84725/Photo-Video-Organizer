#!/usr/bin/env python3
"""
Test Suite for Photo & Video Organizer v2.1:
  - Google Takeout Healer
  - ScannerWorker Takeout Mode & Cleanup
  - Local Wi-Fi Phone Drop Server & Uploads
  - QR Code Generation
"""
import io
import json
import os
import shutil
import sys
import tempfile
import time
import urllib.request
from pathlib import Path
from datetime import datetime

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from core.takeout_healer import (
    find_json_sidecar, parse_takeout_json, heal_media_file
)
from network.local_drop import get_local_ip, LocalDropServer
from core.qr_gen import generate_qr_svg

def test_takeout_healer():
    print("🧪 [1/4] Testing Google Takeout Healer...")
    test_dir = Path(tempfile.mkdtemp(prefix="test_takeout_"))
    try:
        # Create media file & companion json
        img_path = test_dir / "IMG_20210815_142300(1).jpg"
        img_path.write_bytes(b"dummy image data 12345")

        json_path = test_dir / "IMG_20210815_142300.jpg(1).json"
        json_data = {
            "title": "IMG_20210815_142300.jpg",
            "description": "Vacation at the beach",
            "photoTakenTime": {
                "timestamp": "1629037380", # 2021-08-15 14:23:00 UTC approx
                "formatted": "Aug 15, 2021, 2:23:00 PM UTC"
            },
            "geoData": {
                "latitude": 36.7212,
                "longitude": -4.4214,
                "altitude": 15.0
            }
        }
        json_path.write_text(json.dumps(json_data), encoding="utf-8")

        # Test sidecar matching
        matched_json = find_json_sidecar(img_path)
        assert matched_json == json_path, f"Failed to match sidecar: {matched_json} != {json_path}"

        # Test JSON parsing
        meta = parse_takeout_json(matched_json)
        assert meta is not None, "Failed to parse takeout json"
        assert meta["latitude"] == 36.7212
        assert meta["description"] == "Vacation at the beach"
        assert meta["date"].year == 2021
        assert meta["date"].month == 8

        # Test heal_media_file
        resolved_dt, parsed_meta, sidecar = heal_media_file(img_path)
        assert resolved_dt.year == 2021
        assert parsed_meta is not None
        assert sidecar == json_path

        print("  ✅ Google Takeout Healer: PASS")
    finally:
        shutil.rmtree(test_dir, ignore_errors=True)

def test_scanner_worker_takeout():
    print("🧪 [2/4] Testing ScannerWorker in Takeout Mode...")
    test_dir = Path(tempfile.mkdtemp(prefix="test_worker_"))
    try:
        temp_dir = test_dir / "Temp"
        media_dir = test_dir / "Media"
        dup_dir = test_dir / "Duplicates"
        other_dir = test_dir / "Other"

        temp_dir.mkdir()
        media_dir.mkdir()

        # Create photo with takeout json
        p1 = temp_dir / "vacation_photo.jpg"
        p1.write_bytes(b"image_content_A")
        j1 = temp_dir / "vacation_photo.jpg.json"
        j1.write_text(json.dumps({
            "photoTakenTime": {"timestamp": "1588291200"} # 2020-05-01
        }))

        # Create duplicate of p1
        p2 = temp_dir / "vacation_photo_copy.jpg"
        p2.write_bytes(b"image_content_A")

        # Create a screenshot
        p3 = temp_dir / "screenshot_2023.png"
        p3.write_bytes(b"screenshot_content_bytes")

        # Mock ScannerWorker execution without Qt GUI loop
        from core.workers import ScannerWorker
        worker = ScannerWorker(
            mode="takeout",
            temp_path=str(temp_dir),
            media_path=str(media_dir),
            duplicate_path=str(dup_dir),
            other_path=str(other_dir)
        )

        logs = []
        worker.log_message.connect(lambda msg: logs.append(msg))

        finished_stats = {}
        worker.finished_success.connect(lambda s: finished_stats.update(s))

        worker.run()

        # Verify sorted results
        assert finished_stats.get("sorted_media") == 1, f"Expected 1 sorted media, got {finished_stats.get('sorted_media')}"
        assert finished_stats.get("takeout_healed") == 1, f"Expected 1 takeout healed, got {finished_stats.get('takeout_healed')}"
        assert finished_stats.get("json_cleaned") == 1, f"Expected 1 json cleaned, got {finished_stats.get('json_cleaned')}"
        assert finished_stats.get("duplicates") == 1, f"Expected 1 duplicate, got {finished_stats.get('duplicates')}"
        assert finished_stats.get("screenshots") == 1, f"Expected 1 screenshot, got {finished_stats.get('screenshots')}"

        # Verify target folder structure: Media/2020/05/vacation_photo.jpg
        expected_dest = media_dir / "2020" / "05" / "vacation_photo.jpg"
        assert expected_dest.exists(), f"Target media file not found at {expected_dest}"

        # Verify json sidecar was cleaned up
        assert not j1.exists(), "JSON sidecar was not cleaned up!"

        print("  ✅ ScannerWorker Takeout Mode: PASS")
    finally:
        shutil.rmtree(test_dir, ignore_errors=True)

def test_local_drop_server():
    print("🧪 [3/4] Testing Local Drop HTTP Server & Uploads...")
    test_dir = Path(tempfile.mkdtemp(prefix="test_drop_"))
    try:
        drop_folder = test_dir / "Uploads"
        drop_folder.mkdir()

        from network.local_drop import LocalDropRequestHandler, LocalDropServer

        class MockRequest:
            def __init__(self, raw_bytes):
                self._rfile = io.BytesIO(raw_bytes)
                self._wfile = io.BytesIO()
            def makefile(self, mode, *args, **kwargs):
                if 'b' in mode:
                    return self._rfile if 'r' in mode else self._wfile
                return self._rfile
            def sendall(self, data):
                self._wfile.write(data)

        LocalDropRequestHandler.target_dir = drop_folder

        fake_photo_bytes = b"EXIF_JPEG_PAYLOAD_FROM_PHONE" * 100
        hdr = (
            f"POST /upload?filename=phone_photo.jpg HTTP/1.1\r\n"
            f"Host: 127.0.0.1\r\n"
            f"Content-Length: {len(fake_photo_bytes)}\r\n\r\n"
        ).encode("utf-8")
        raw_req = hdr + fake_photo_bytes

        req = MockRequest(raw_req)
        handler = LocalDropRequestHandler(req, ('127.0.0.1', 12345), None)

        # Verify file arrived on disk
        saved_file = drop_folder / "phone_photo.jpg"
        assert saved_file.exists(), "Uploaded file not saved on disk!"
        assert saved_file.read_bytes() == fake_photo_bytes

        # Verify GET /ping
        ping_req = (
            b'GET /ping HTTP/1.1\r\n'
            b'Host: 127.0.0.1\r\n\r\n'
        )
        req_ping = MockRequest(ping_req)
        handler_ping = LocalDropRequestHandler(req_ping, ('127.0.0.1', 12345), None)
        assert b'"status": "active"' in req_ping._wfile.getvalue()

        print("  ✅ Local Drop Server & Streaming Upload: PASS")
    finally:
        shutil.rmtree(test_dir, ignore_errors=True)

def test_qr_gen():
    print("🧪 [4/4] Testing QR Code generation...")
    svg = generate_qr_svg("http://192.168.1.50:8080", size=200)
    assert "<svg" in svg and "</svg>" in svg
    assert "192.168.1.50" in svg or "xmlns" in svg
    print("  ✅ QR Code Generation: PASS")

if __name__ == "__main__":
    print("==========================================")
    print("Photo & Video Organizer v2.1 Test Suite")
    print("==========================================")
    test_takeout_healer()
    test_scanner_worker_takeout()
    test_local_drop_server()
    test_qr_gen()
    print("==========================================")
    print("🎉 ALL TESTS PASSED SUCCESSFULLY!")
    print("==========================================")

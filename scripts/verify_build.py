#!/usr/bin/env python3
import os
import hashlib
import pathlib
import sys

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

def main():
    exe_path = pathlib.Path("dist") / "PhotoVideoOrganizer.exe"
    if not exe_path.exists():
        print("ERROR: dist/PhotoVideoOrganizer.exe was not found!", file=sys.stderr)
        sys.exit(1)

    data = exe_path.read_bytes()
    size_mb = round(len(data) / (1024 * 1024), 2)
    sha256 = hashlib.sha256(data).hexdigest()

    print(f"[OK] PhotoVideoOrganizer.exe verified successfully!")
    print(f"[FILE SIZE] {size_mb} MB ({len(data)} bytes)")
    print(f"[SHA-256] {sha256}")

    # Export to GITHUB_ENV if running inside GitHub Actions
    github_env = os.environ.get("GITHUB_ENV")
    if github_env and os.path.exists(github_env):
        with open(github_env, "a", encoding="utf-8") as f:
            f.write(f"EXE_SHA256={sha256}\n")

    # Export to GITHUB_STEP_SUMMARY if running inside GitHub Actions
    summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary_path and os.path.exists(summary_path):
        with open(summary_path, "a", encoding="utf-8") as f:
            f.write("### 📦 Build Artifact Summary\n")
            f.write(f"* **File:** `PhotoVideoOrganizer.exe`\n")
            f.write(f"* **Size:** {size_mb} MB\n")
            f.write(f"* **SHA-256 Checksum:** `{sha256}`\n")

if __name__ == "__main__":
    main()

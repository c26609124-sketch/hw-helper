#!/usr/bin/env python3
"""Regenerate file hashes for version.json"""

import json
import hashlib
from pathlib import Path


def calculate_sha256(file_path: Path) -> str:
    """Calculate SHA256 hash of a file"""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def get_all_files(root_dir: Path) -> list:
    """Get all files to hash (excluding certain directories)"""
    exclude_dirs = {
        '__pycache__', '.git', 'venv', 'ENV', 'env',
        '.hwhelper', 'node_modules', 'build', 'dist',
        'screenshots', 'saved_screenshots', '.update_backup',
        'downloads', 'eggs', '.eggs'
    }

    exclude_patterns = {
        '.pyc', '.pyo', '.pyd', '.so', '.egg-info',
        '.DS_Store', 'Thumbs.db', '.swp', '.swo'
    }

    files = []
    for file_path in root_dir.rglob('*'):
        # Skip if in excluded directory
        if any(excluded in file_path.parts for excluded in exclude_dirs):
            continue

        # Skip if excluded pattern
        if any(file_path.name.endswith(pattern) for pattern in exclude_patterns):
            continue

        # Skip directories
        if file_path.is_dir():
            continue

        # Get relative path
        rel_path = file_path.relative_to(root_dir)

        # Convert to forward slashes for consistency
        rel_path_str = str(rel_path).replace('\\', '/')

        files.append((rel_path_str, file_path))

    return sorted(files)


def main():
    root_dir = Path(__file__).parent
    version_file = root_dir / "version.json"

    print("🔍 Scanning for files...")
    files = get_all_files(root_dir)

    print(f"📝 Calculating hashes for {len(files)} files...")
    file_hashes = {}

    for rel_path, full_path in files:
        try:
            file_hash = calculate_sha256(full_path)
            file_hashes[rel_path] = file_hash
            print(f"  ✓ {rel_path}")
        except Exception as e:
            print(f"  ✗ {rel_path}: {e}")

    # Load existing version.json
    print("\n📖 Loading version.json...")
    with open(version_file, 'r', encoding='utf-8') as f:
        version_data = json.load(f)

    # Update file_hashes
    version_data['file_hashes'] = file_hashes

    # Save updated version.json
    print("💾 Saving updated version.json...")
    with open(version_file, 'w', encoding='utf-8') as f:
        json.dump(version_data, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Regenerated hashes for {len(file_hashes)} files")
    print(f"📊 Total files: {len(file_hashes)}")


if __name__ == "__main__":
    main()

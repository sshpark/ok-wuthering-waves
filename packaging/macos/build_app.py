#!/usr/bin/env python3
"""
build_app.py - Build macOS .app bundle and optional .dmg for ok-wuthering-waves.

Usage:
    python packaging/macos/build_app.py [--dmg]
"""
import argparse
import os
import shutil
import subprocess
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))


def ensure_icns():
    """Generate icon.icns from icon.png using macOS sips & iconutil."""
    icns_path = os.path.join(PROJECT_ROOT, 'icons', 'icon.icns')
    png_path = os.path.join(PROJECT_ROOT, 'icons', 'icon.png')

    if os.path.exists(icns_path):
        print(f"Icon already exists: {icns_path}")
        return icns_path

    if not os.path.exists(png_path):
        print(f"Warning: {png_path} not found, skipping icon generation.")
        return None

    print(f"Generating icon.icns from {png_path}...")
    iconset_dir = os.path.join(PROJECT_ROOT, 'icons', 'icon.iconset')
    os.makedirs(iconset_dir, exist_ok=True)

    try:
        sizes = [16, 32, 64, 128, 256, 512]
        for s in sizes:
            subprocess.run(['sips', '-z', str(s), str(s), png_path,
                            '--out', f'{iconset_dir}/icon_{s}x{s}.png'], check=True, capture_output=True)
            subprocess.run(['sips', '-z', str(s * 2), str(s * 2), png_path,
                            '--out', f'{iconset_dir}/icon_{s}x{s}@2x.png'], check=True, capture_output=True)

        subprocess.run(['iconutil', '-c', 'icns', iconset_dir, '-o', icns_path], check=True, capture_output=True)
        print(f"Icon generated successfully: {icns_path}")
        return icns_path
    finally:
        if os.path.exists(iconset_dir):
            shutil.rmtree(iconset_dir, ignore_errors=True)


def build_app():
    """Run PyInstaller with the spec file."""
    spec_path = os.path.join(PROJECT_ROOT, 'packaging', 'macos', 'OK-Wuthering-Waves.spec')
    dist_dir = os.path.join(PROJECT_ROOT, 'dist_macos')
    build_dir = os.path.join(PROJECT_ROOT, 'build_macos')

    ensure_icns()

    print("=" * 60)
    print("Building macOS App Bundle with PyInstaller...")
    print(f"Spec file: {spec_path}")
    print(f"Output directory: {dist_dir}")
    print("=" * 60)

    cmd = [
        sys.executable, '-m', 'PyInstaller',
        spec_path,
        '--noconfirm',
        '--distpath', dist_dir,
        '--workpath', build_dir,
    ]

    result = subprocess.run(cmd, cwd=PROJECT_ROOT)
    if result.returncode != 0:
        print("PyInstaller build failed!", file=sys.stderr)
        return False

    app_path = os.path.join(dist_dir, 'OK-Wuthering-Waves.app')
    if os.path.exists(app_path):
        binary_path = os.path.join(app_path, 'Contents', 'MacOS', 'ok-wuthering-waves')
        print("Signing macOS app bundle...")
        subprocess.run(['codesign', '-s', '-', '--force', binary_path], check=False)
        subprocess.run(['codesign', '-s', '-', '--force', app_path], check=False)
        print("=" * 60)
        print(f"Build succeeded! macOS App bundle created at:\n  {app_path}")
        print("=" * 60)
        return True
    else:
        print(f"Error: expected app bundle not found at {app_path}", file=sys.stderr)
        return False


def build_dmg():
    """Create a .dmg disk image from the built .app bundle."""
    dist_dir = os.path.join(PROJECT_ROOT, 'dist_macos')
    app_path = os.path.join(dist_dir, 'OK-Wuthering-Waves.app')
    dmg_path = os.path.join(dist_dir, 'OK-Wuthering-Waves-macOS.dmg')

    if not os.path.exists(app_path):
        print(f"Cannot create DMG: {app_path} does not exist. Build the app first.", file=sys.stderr)
        return False

    print("=" * 60)
    print(f"Creating DMG image: {dmg_path}...")
    print("=" * 60)

    # Temporary staging directory to include /Applications symlink
    staging_dir = os.path.join(dist_dir, 'dmg_staging')
    if os.path.exists(staging_dir):
        shutil.rmtree(staging_dir)
    os.makedirs(staging_dir)

    try:
        shutil.copytree(app_path, os.path.join(staging_dir, 'OK-Wuthering-Waves.app'), symlinks=True)
        # Create Applications symlink for drag & drop installation
        os.symlink('/Applications', os.path.join(staging_dir, 'Applications'))

        if os.path.exists(dmg_path):
            os.remove(dmg_path)

        cmd = [
            'hdiutil', 'create',
            '-volname', 'OK-Wuthering-Waves',
            '-srcfolder', staging_dir,
            '-ov',
            '-format', 'UDZO',
            dmg_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"hdiutil failed: {result.stderr}", file=sys.stderr)
            return False

        print(f"DMG installer created successfully:\n  {dmg_path}")
        return True
    finally:
        if os.path.exists(staging_dir):
            shutil.rmtree(staging_dir, ignore_errors=True)


def main():
    parser = argparse.ArgumentParser(description="Build OK-Wuthering-Waves macOS application.")
    parser.add_argument('--dmg', action='store_true', help="Also generate a .dmg disk image installer.")
    args = parser.parse_args()

    success = build_app()
    if success and args.dmg:
        build_dmg()


if __name__ == '__main__':
    main()

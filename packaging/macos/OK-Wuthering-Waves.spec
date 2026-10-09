# -*- mode: python ; coding: utf-8 -*-
import os
import sys
from PyInstaller.utils.hooks import collect_data_files, collect_submodules, collect_dynamic_libs

block_cipher = None

project_dir = os.path.abspath(os.path.join(SPECPATH, '..', '..'))
ok_script_dir = os.path.abspath(os.path.join(project_dir, '..', 'ok-script'))

added_files = [
    (os.path.join(project_dir, 'config.py'), '.'),
    (os.path.join(project_dir, 'configs'), 'configs'),
    (os.path.join(project_dir, 'assets'), 'assets'),
    (os.path.join(project_dir, 'i18n'), 'i18n'),
    (os.path.join(project_dir, 'icons'), 'icons'),
    (os.path.join(project_dir, 'ok_templates'), 'ok_templates'),
    (os.path.join(project_dir, 'src'), 'src'),
]

# Collect package data
for pkg in ['ok', 'qfluentwidgets', 'onnxocr', 'onnxocr_ppocrv5']:
    try:
        added_files += collect_data_files(pkg)
    except Exception as e:
        print(f"Warning: could not collect data for {pkg}: {e}")

# Collect OpenVINO frontend and device plugin dynamic libraries
binaries = []
try:
    import openvino
    ov_libs_dir = os.path.join(os.path.dirname(openvino.__file__), 'libs')
    if os.path.isdir(ov_libs_dir):
        for f in os.listdir(ov_libs_dir):
            if f.endswith(('.dylib', '.so')) and 'hwloc' not in f and 'tbbbind' not in f:
                binaries.append((os.path.join(ov_libs_dir, f), 'openvino/libs'))
except Exception as e:
    print(f"Warning: could not collect openvino dynamic libs: {e}")

# Collect all modules under src recursively
src_modules = []
src_dir = os.path.join(project_dir, 'src')
for root, _, files in os.walk(src_dir):
    for f in files:
        if f.endswith('.py'):
            rel = os.path.relpath(os.path.join(root, f[:-3]), project_dir)
            mod = rel.replace(os.sep, '.')
            src_modules.append(mod)

hidden_imports = [
    'config',
    'ok',
    'Quartz',
    'AppKit',
    'Foundation',
    'ApplicationServices',
    'pynput.keyboard._darwin',
    'pynput.mouse._darwin',
    'openvino',
    'openvino.frontend',
    'openvino.frontend.onnx',
    'openvino.frontend.onnx.py_onnx_frontend',
    'onnxocr',
    'onnxocr_ppocrv5',
    'cv2',
    'PIL',
    'numpy',
] + src_modules

try:
    hidden_imports += collect_submodules('ok')
except Exception as e:
    print(f"Warning: could not collect submodules for ok: {e}")

a = Analysis(
    [os.path.join(project_dir, 'main.py')],
    pathex=[project_dir, ok_script_dir],
    binaries=binaries,
    datas=added_files,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'win32api', 'win32con', 'win32gui', 'win32process',
        'win32ui', 'win32com', 'pythoncom', 'pycaw', 'comtypes'
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='ok-wuthering-waves',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='ok-wuthering-waves',
)

icon_path = os.path.join(project_dir, 'icons', 'icon.icns')
if not os.path.exists(icon_path):
    icon_path = None

app = BUNDLE(
    coll,
    name='OK-Wuthering-Waves.app',
    icon=icon_path,
    bundle_identifier='com.okscript.okww',
    info_plist={
        'CFBundleName': 'OK-Wuthering-Waves',
        'CFBundleDisplayName': '鸣潮小助手',
        'CFBundleIdentifier': 'com.okscript.okww',
        'CFBundleVersion': '3.7.5',
        'CFBundleShortVersionString': '3.7.5',
        'NSHighResolutionCapable': 'True',
        'NSSupportsAutomaticGraphicsSwitching': 'True',
        'NSRequiresAquaSystemAppearance': 'False',
        'NSScreenCaptureUsageDescription': '需要屏幕录制权限以捕获游戏画面进行图像识别和分析。',
        'NSAccessibilityUsageDescription': '需要辅助功能权限以模拟键盘和鼠标操作。',
    },
)

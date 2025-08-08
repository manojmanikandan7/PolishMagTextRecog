#!/usr/bin/env python3
"""
Build script for creating standalone executable of the Polish Magazine Transcriber.
"""

import subprocess
import sys
from pathlib import Path


tesseract_path = Path("/opt/homebrew/")


def build_executable():
    """Build the standalone executable using PyInstaller."""
    print("Building Polish Magazine Transcriber executable...")

    # PyInstaller command
    cmd = [
        "pyinstaller",
        "--onefile",
        "--windowed",
        "--name=PolishMagazineTranscriber",
        "--add-data=src/text_recog:src/text_recog",
        "--add-data=samples:samples",
        f"--add-data={tesseract_path / 'share/tessdata'}:tesseract/tessdata",
        f"--add-binary={tesseract_path / 'bin/tesseract'}:tesseract",
        "--hidden-import=cv2",
        "--hidden-import=PIL",
        "--hidden-import=pytesseract",
        "--hidden-import=pandas",
        "--hidden-import=matplotlib",
        "--hidden-import=openpyxl",
        "--hidden-import=tkinter",
        "--hidden-import=tkinter.ttk",
        "--hidden-import=tkinter.filedialog",
        "--hidden-import=tkinter.messagebox",
        "--exclude-module=matplotlib.tests",
        "--exclude-module=pandas.tests",
        "--exclude-module=PIL.tests",
        "src/text_recog/interactive_transcriber.py",
    ]

    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("Build successful!")
        print(f"Executable created in: dist/PolishMagazineTranscriber")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Build failed: {e}")
        print(f"Error output: {e.stderr}")
        return False


def main():
    """Main build function."""
    print("Polish Magazine Transcriber Build Script")
    print("=" * 50)

    # Check if PyInstaller is installed
    try:
        import PyInstaller

        print(f"PyInstaller version: {PyInstaller.__version__}")
    except ImportError:
        print("PyInstaller not found. Installing...")
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "pyinstaller"], check=True
        )

    # Build the executable
    success = build_executable()

    if success:
        print("\n Build completed successfully!")
        print("You can find the executable in the 'dist' directory.")
    else:
        print("\n Build failed. Please check the error messages above.")
        sys.exit(1)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Build script for creating standalone executable of the Polish Magazine Transcriber.
"""

import subprocess
import sys
from pathlib import Path


brew_path = Path("/opt/homebrew/")


def build_executable():
    """Build the standalone executable using PyInstaller."""
    # Check if PyInstaller is installed
    try:
        import PyInstaller

        print(f"PyInstaller version: {PyInstaller.__version__}\n")

    except ImportError:
        print("PyInstaller not found. Installing...\n")
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "pyinstaller"], check=True
        )



    # PyInstaller command
    cmd = [
        "src/text_recog/interactive_transcriber.py",
        "--onefile",
        "--windowed",
        "--name=PolishMagazineTranscriber",
        "--add-data=src/text_recog:src/text_recog",
        "--add-data=samples:samples",
        f"--add-data={brew_path / 'share/tessdata'}:tesseract/tessdata",
        f"--add-binary={brew_path / 'bin/tesseract'}:tesseract",
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
        "--noconfirm",
    ]

    print("Building Polish Magazine Transcriber executable...")
    import PyInstaller.__main__
    PyInstaller.__main__.run(cmd)


def main():
    """Main build function."""
    print("Polish Magazine Transcriber Build Script")
    print("=" * 50)

    # Build the executable
    build_executable()



if __name__ == "__main__":
    main()

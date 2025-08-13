# Interactive Magazine Transcriber

An interactive GUI application for transcribing Polish magazine images using OCR with user-selectable text regions.
Primarily built on the [Google's tesseract-ocr engine](https://github.com/tesseract-ocr/tesseract) and [pytesseract](https://github.com/madmaze/pytesseract)

## License Notice

[tesseract-ocr](https://github.com/tesseract-ocr/tesseract) and [pytesseract](https://github.com/madmaze/pytesseract) are licensed under the [Apache 2.0 License](http://www.apache.org/licenses/LICENSE-2.0), a copy of which can be found at [APACHE_2.0_LICENSE](APACHE_2.0_LICENSE).

## Features

- **Interactive GUI**: User-friendly interface built with tkinter
- **Multi-language OCR**: Support for Polish, English, and German text recognition
- **Visual Layout Analysis**: Automatic detection and visualization of text blocks
- **Selective Transcription**: Choose which text blocks to include in the final transcript
- **Multiple Output Formats**: Export transcripts in JSON, CSV, Excel, and plain text
- **Image Navigation**: Browse through multiple images with Previous/Next controls
- **Zoom Controls**: Interactive zoom in/out for detailed text inspection
- **Output Directory Selection**: Flexible output location configuration
- **Batch Processing**: Process multiple images efficiently

## Technology Stack

### Core Technologies

- **OpenCV**: Image processing and computer vision
- **Tesseract OCR**: Multi-language text recognition engine
- **Pandas**: Data manipulation and export
- **PIL/Pillow**: Image handling and GUI support
- **Matplotlib**: Visualization and analysis plots

### Development Tools

- **Hatchling**: Modern Python build backend
- **PyInstaller**: Standalone executable creation

### GUI Framework

- **tkinter**: Cross-platform GUI toolkit
- **ttk**: Themed widgets for modern appearance

## Installation

### Prerequisites

1. **Python 3.8 or higher**
2. **Tesseract OCR Engine**:
   - **macOS**: `brew install tesseract tesseract-lang`
   - **Ubuntu/Debian**: `sudo apt-get install tesseract-ocr tesseract-ocr-pol tesseract-ocr-eng`
   - **Windows**: Download from [UB-Mannheim/tesseract](https://github.com/UB-Mannheim/tesseract/wiki)

### Quick Start

1. **Clone the repository**:

   ```bash
   git clone https://github.com/manojmanikandan7/PolishMagTextRecog
   cd PolishMagTextRecog
   ```

2. **Install dependencies**:

   ```bash
   # Install production dependencies
   pip install -r requirements.txt
   
   # Or install with development tools
   make install-dev
   ```

3. **Run the application**:

   ```bash
   # Direct execution
   python src/text_recog/interactive_transcriber.py
   
   # Or using make
   make run
   ```

## Usage

### Starting the Application

```bash
# Method 1: Direct execution
python src/text_recog/interactive_transcriber.py

# Method 2: Using make
make run

# Method 3: As installed package
polish-magazine-transcriber
```

### Using the Interface

1. **Load Images**:
   - Click "Select Image Folder" to choose a directory with magazine images
   - The application automatically loads images from `samples/` on startup
   - Use "Previous"/"Next" buttons to navigate through multiple images

2. **Analyze Layout**:
   - Images are automatically processed with Tesseract OCR
   - Text blocks are detected and highlighted with colored rectangles
   - Each block is labeled with a Block ID (B1, B2, etc.)

3. **Select Text Blocks**:
   - The right panel shows all detected text blocks with preview text
   - All blocks are selected by default
   - Click on blocks in the list to select/deselect them
   - Use "Select All" or "Select None" buttons for quick selection
   - Preview full text by clicking on any block

4. **Configure Output**:
   - Click "Select Output Directory" to choose where transcripts are saved
   - Or let the application prompt you when generating transcripts

5. **Generate Transcript**:
   - Click "Generate Transcript" to create the final output
   - Transcripts are saved in multiple formats (JSON, CSV, Excel, TXT)
   - Success message shows the file locations

### Output Formats

**JSON Format** (`*_transcript.json`):
```json
[
  {
    "block_id": 1,
    "full_text": "Extracted text content",
    "left": 100,
    "top": 200,
    "width": 300,
    "height": 50
  }
]
```

**CSV Format** (`*_transcript.csv`):

- Structured data with block information and coordinates

**Excel Format** (`*_transcript.xlsx`):

- Spreadsheet format with multiple sheets

**Text Format** (`*_transcript.txt`):

- Clean plain text with block separators

## Building Standalone Executable

Create a standalone executable that doesn't require Python installation:

```bash
# Build executable
make build-app

# Or directly
python build_app.py
```

The executable will be created in the `dist/` directory and can be distributed to users without Python installed.

## Project Structure

```
PolishMagTextRecog/
├── src/text_recog/
│   ├── interactive_transcriber.py  # Main GUI application
│   ├── layout.py                   # Layout analysis classes
│   └──  segment.py                  # OCR and analysis engine
├── samples/magazines/              # Input images for testing
├── outputs/
│   ├── transcripts/               # Generated transcripts
│   └── analysis/                  # Analysis visualizations
├── pyproject.toml                 # Project configuration
├── requirements.txt               # Dependencies
├── build_app.py                   # PyInstaller build script
├── Makefile                       # Development commands
└── README.md                      # This file
```

## Development

### Building Package

```bash
# Build wheel and source distribution
make build

# Clean build artifacts
make clean
```

## Configuration

### Language Support

The application supports multiple languages for OCR:

- **Polish** (primary)
- **English** (secondary)
- **German** (tertiary)

To modify language support, edit the `LANG` parameter in `segment.py`:

```python
LANG = "pol+eng+deu"
```

### Output Directory

The application allows flexible output directory selection:

- Default: `outputs/transcripts/`
- User-selectable via GUI
- Automatic directory creation

## Troubleshooting

### Common Issues

1. **Tesseract Not Found**:

   ```bash
   # macOS
   brew install tesseract tesseract-lang
   
   # Ubuntu/Debian
   sudo apt-get install tesseract-ocr tesseract-ocr-pol
   
   # Verify installation
   tesseract --version
   ```

2. **Import Errors**:

   ```bash
   # Reinstall dependencies
   pip install -r requirements.txt
   
   # Or install in development mode
   make install-dev
   ```

3. **GUI Issues**:
   - Ensure tkinter is available: `python -c "import tkinter"`
   - On Linux, install: `sudo apt-get install python3-tk`

4. **Performance Issues**:
   - Large images may take longer to process
   - Use zoom controls for better performance
   - Consider resizing very large images

### Debug Mode

Run with verbose output:

```bash
python -v src/text_recog/interactive_transcriber.py
```

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes and add tests
4. Commit your changes: `git commit -m 'Add amazing feature'`
5. Push to the branch: `git push origin feature/amazing-feature`
6. Open a Pull Request

### Development Guidelines

- Follow PEP 8 style guidelines
- Add type hints to all functions
- Update documentation for API changes
- Use conventional commit messages

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- **Issues**: [GitHub Issues](https://github.com/manojmanikandan7/PolishMagTextRecog/issues)

## Acknowledgments

This project is built on excellent open-source libraries and tools. Special thanks to:

### Core Libraries

- **[OpenCV](https://opencv.org/)** - Computer vision and image processing
- **[Tesseract OCR](https://github.com/tesseract-ocr/tesseract)** - Multi-language OCR engine
- **[pytesseract](https://github.com/madmaze/pytesseract)** - Python wrapper for Tesseract
- **[Pandas](https://pandas.pydata.org/)** - Data manipulation and analysis
- **[Pillow](https://python-pillow.org/)** - Image handling library
- **[Matplotlib](https://matplotlib.org/)** - Plotting and visualization
- **[openpyxl](https://openpyxl.readthedocs.io/)** - Excel file handling

### GUI & Build Tools

- **[tkinter](https://docs.python.org/3/library/tkinter.html)** - GUI framework
- **[Hatchling](https://hatch.pypa.io/)** - Modern Python build backend
- **[PyInstaller](https://pyinstaller.org/)** - Standalone executable creation

### Additional Resources

- **[Tesseract Community](https://github.com/tesseract-ocr/tessdata)** - Language packs and OCR improvements

---


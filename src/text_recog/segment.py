from pathlib import Path

import cv2
import matplotlib.pyplot as plt
import pandas as pd
import pytesseract

from layout import Page


class MagazineLayoutAnalyzer:
    def __init__(self, image_path: Path):
        """Initialize with image path"""
        self.image_path = image_path
        self.image = cv2.imread(image_path.as_posix())
        assert self.image is not None
        self.gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        # self.binary = self.preprocess_image()
        self.height, self.width = self.gray.shape

    def analyze_with_tesseract(self) -> dict[int, Page]:
        """Use Tesseract for layout analysis"""

        # Get detailed data from Tesseract
        data: pd.DataFrame = pytesseract.image_to_data(self.image, lang="pol+eng", output_type=pytesseract.Output.DATAFRAME)

        from layout import df_to_layout

        pages = df_to_layout(data)

        return pages

    def visualize_analysis(self, analysis_save_path=None):
        """Comprehensive visualization of the analysis"""
        fig, axes = plt.subplots(1, 2, figsize=(18, 12))

        # Original image
        axes[0].imshow(cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB))
        axes[0].set_title('Original Image')
        axes[0].axis('off')

        # Tesseract analysis
        tesseract_blocks = self.analyze_with_tesseract()
        img_tesseract = self.image.copy()

        import random
        colours = [random.choices(range(256), k=3) for _ in range(16)]
        for block_id, block in tesseract_blocks.items():
            if not block.get_text():
                continue
            colour = colours[block_id % len(colours)]
            cv2.rectangle(img_tesseract,
                        (block.left, block.top),
                        (block.left + block.width, block.top + block.height),
                        colour, 2)

        axes[1].imshow(cv2.cvtColor(img_tesseract, cv2.COLOR_BGR2RGB))
        axes[1].set_title(f'Tesseract Blocks ({len(tesseract_blocks)})')
        axes[1].axis('off')

        plt.tight_layout()

        if analysis_save_path:
            plt.savefig(analysis_save_path, dpi=300, bbox_inches='tight')


        # Print analysis summary
        print("\n=== ANALYSIS SUMMARY ===")
        print(f"File name: {self.image_path.name}")
        print(f"Image dimensions: {self.width}x{self.height}")
        print(f"Tesseract blocks: {len(tesseract_blocks)}")

    
if __name__ == "__main__":
    # Initialize analyzer
    samples_dir = Path("samples/magazines")
    output_analysis_dir = Path("outputs/analysis")
    output_pdf_dir = Path("outputs/searchable")
    output_analysis_dir.mkdir(parents=True, exist_ok=True)
    for file in samples_dir.glob("*.jpg"):
        cwd = Path('.')
        analyzer = MagazineLayoutAnalyzer(file.relative_to('.'))
    
        # Run complete analysis with visualization
        analyzer.visualize_analysis(output_analysis_dir / f"{file.stem}.png")
    
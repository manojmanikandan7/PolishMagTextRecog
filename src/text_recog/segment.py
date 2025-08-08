from pathlib import Path
from typing import Literal, Sequence

import cv2
from text_recog import layout
import pandas as pd
import pytesseract
import os
import sys


LANG = "pol+eng+deu"

def get_tesseract_path():
    if getattr(sys, "frozen", False):
        # Running as PyInstaller bundle
        base_path = sys._MEIPASS
        return os.path.join(base_path, "tesseract", "tesseract")
    else:
        # Running as normal Python script
        return "tesseract"  # Assumes tesseract is in the PATH


# Set the tesseract command path
pytesseract.pytesseract.tesseract_cmd = get_tesseract_path()


class MagazineLayoutAnalyzer:
    def __init__(self, image_path: Path):
        """Initialize with image path"""
        self.image_path = image_path
        self.image = cv2.imread(image_path.as_posix())
        assert self.image is not None
        self.gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        # self.binary = self.preprocess_image()
        self.height, self.width = self.gray.shape

    def analyze_with_tesseract(self) -> dict[int, layout.Page]:
        """Use Tesseract for layout analysis"""

        # Get detailed data from Tesseract
        data: pd.DataFrame = pytesseract.image_to_data(
            self.image, lang=LANG, output_type=pytesseract.Output.DATAFRAME
        )
        pages = layout.df_to_layout(data)

        return pages

    def visualize_analysis(
        self, blocks: dict[int, layout.Block], analysis_save_path=None
    ):
        """Comprehensive visualization of the analysis
        :param blocks:
        :param analysis_save_path:
        """
        import matplotlib.pyplot as plt

        fig, axes = plt.subplots(1, 2, figsize=(18, 12))

        # Original image
        axes[0].imshow(cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB))
        axes[0].set_title("Original Image")
        axes[0].axis("off")

        img_tesseract = self.add_block_overlay(blocks)

        axes[1].imshow(cv2.cvtColor(img_tesseract, cv2.COLOR_BGR2RGB))
        axes[1].set_title(f"Tesseract Blocks ({len(blocks)})")
        axes[1].axis("off")

        plt.tight_layout()

        if analysis_save_path:
            plt.savefig(analysis_save_path, dpi=300, bbox_inches="tight")

        # Print analysis summary
        print("\n=== ANALYSIS SUMMARY ===")
        print(f"File name: {self.image_path.name}")
        print(f"Image dimensions: {self.width}x{self.height}")
        print(f"Tesseract blocks: {len(blocks)}")

    def add_block_overlay(self, blocks):
        img_overlay = self.image.copy()

        colours = [
            (255, 179, 186),  # Pastel Red
            (255, 223, 186),  # Pastel Orange
            (255, 204, 188),  # Pastel Peach
            (255, 209, 163),  # Pastel Apricot
            (255, 255, 186),  # Pastel Yellow
            (255, 250, 205),  # Pastel Lemon
            (223, 255, 186),  # Pastel Chartreuse
            (186, 255, 201),  # Pastel Mint
            (186, 255, 201),  # Pastel Green
            (178, 255, 255),  # Pastel Seafoam
            (174, 255, 255),  # Pastel Turquoise
            (186, 225, 255),  # Pastel Sky Blue
            (174, 198, 255),  # Pastel Blue
            (204, 204, 255),  # Pastel Periwinkle
            (220, 208, 255),  # Pastel Lavender
            (229, 204, 255),  # Pastel Purple
            (255, 186, 255),  # Pastel Magenta
            (255, 192, 203),  # Pastel Pink
            (255, 204, 229),  # Pastel Rose
            (255, 197, 208),  # Pastel Blush
        ]
        for block_id, block in blocks.items():
            if not block.get_text():
                continue
            colour = colours[block_id % len(colours)]
            cv2.rectangle(
                img_overlay,
                (block.left, block.top),
                (block.left + block.width, block.top + block.height),
                colour,
                2,
            )

            # Add block ID label
            cv2.putText(
                img_overlay,
                f"B{block_id}",
                (int(block.left), int(block.top) - 5),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.75,
                colour,
                2,
            )

        return img_overlay

    def generate_transcript(
        self,
        transcripts_dir: Path,
        blocks: dict[int, layout.Block],
        ignore_blank_blocks: bool = False,
        formats: Sequence[Literal["json", "csv", "excel", "text"]] = (
            "json",
            "csv",
            "excel",
            "text",
        ),
    ) -> dict[Literal["json", "csv", "excel", "text"], Path]:
        """

        :param formats:
        :param ignore_blank_blocks:
        :param transcripts_dir:
        :param blocks:
        """
        transcripts_dir.mkdir(parents=True, exist_ok=True)

        # Collect text from selected blocks
        transcript_data = []
        full_text = []

        for block_id, block in blocks.items():
            block_content = block.get_text()
            if ignore_blank_blocks and not block_content:
                continue

            block_info = {
                "block_id": block_id,
                "full_text": block_content,
                "left": block.left,
                "top": block.top,
                "width": block.width,
                "height": block.height,
            }

            transcript_data.append(block_info)
            full_text.append(block_content)

        data_df = pd.DataFrame(transcript_data)
        # Save transcript
        output_filename = f"{self.image_path.stem}_transcript"

        paths = {}
        if "json" in formats:
            json_output_dir = transcripts_dir / "json"
            json_output_dir.mkdir(exist_ok=True, parents=True)
            json_output_path = json_output_dir / f"{output_filename}.json"
            data_df.to_json(json_output_path, orient="records", indent=2)
            paths["json"] = json_output_path

        if "csv" in formats:
            csv_output_dir = transcripts_dir / "csv"
            csv_output_dir.mkdir(exist_ok=True, parents=True)
            csv_output_path = csv_output_dir / f"{output_filename}.csv"
            data_df.to_csv(csv_output_path, index=False)
            paths["csv"] = csv_output_path

        if "excel" in formats:
            excel_output_dir = transcripts_dir / "excel"
            excel_output_dir.mkdir(exist_ok=True, parents=True)
            excel_output_path = excel_output_dir / f"{output_filename}.xlsx"
            data_df.to_excel(excel_output_path, index=False)
            paths["excel"] = excel_output_path

        if "text" in formats:
            text_output_dir = transcripts_dir / "text"
            text_output_dir.mkdir(exist_ok=True, parents=True)
            text_output_path = text_output_dir / f"{output_filename}.txt"
            text_output_path.open("w").write("\n\n".join(full_text))
            paths["text"] = text_output_path

        return paths


if __name__ == "__main__":
    # Initialize analyzer
    samples_dir = Path("magazines")
    output_analysis_dir = Path("outputs/analysis")
    output_transcripts_dir = Path("outputs/transcripts")
    output_analysis_dir.mkdir(parents=True, exist_ok=True)
    for file in samples_dir.glob("*.jpg"):
        cwd = Path(".")
        analyzer = MagazineLayoutAnalyzer(file.relative_to("."))

        # Tesseract analysis
        tesseract_blocks = analyzer.analyze_with_tesseract()[1].blocks

        # Run complete analysis with visualization
        analyzer.visualize_analysis(
            tesseract_blocks, output_analysis_dir / f"{file.stem}.png"
        )

        analyzer.generate_transcript(
            output_transcripts_dir, tesseract_blocks, ignore_blank_blocks=True
        )

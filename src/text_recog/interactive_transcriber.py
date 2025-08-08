import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

import cv2
from PIL import Image, ImageTk

from text_recog.segment import MagazineLayoutAnalyzer

SAMPLES_DIR = Path("samples")
DEFAULT_ZOOM_LEVEL = 0.5


class InteractiveTranscriber:
    def __init__(self, root):
        # UI elements
        self.photo = None
        self.status_var = None
        self.preview_text = None
        self.blocks_listbox = None
        self.canvas = None
        self.file_label = None

        self.root = root
        self.root.title("Interactive Magazine Transcriber")
        self.root.geometry("1200x1000")

        # Initialize variables
        self.current_image_path = None
        self.image_dir_path = None
        self.current_image_index = -1
        self.image_files = []

        # OCR data
        self.current_analyzer = None
        self.blocks_data = {}
        self.selected_blocks = set()

        # Track OCR data
        self.ocr_data = None

        # Zoom variables
        self.zoom_level = DEFAULT_ZOOM_LEVEL
        self.original_image = None

        # Highlight variables
        self.alpha = 0.5

        # Output directory
        self.output_directory = None

        self.setup_ui()

    def setup_ui(self, load_sample: bool = True):
        """Setup the user interface"""
        # Main container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Top frame for controls
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=(0, 10))

        # File selection
        ttk.Button(
            control_frame, text="Select Image Folder", command=self.select_image_dir
        ).pack(side=tk.LEFT, padx=(0, 5))

        self.file_label = ttk.Label(control_frame, text="No file selected")
        self.file_label.pack(side=tk.LEFT, padx=(5, 0))

        # Zoom controls
        zoom_frame = ttk.Frame(control_frame)
        zoom_frame.pack(side=tk.LEFT, padx=(20, 0))

        ttk.Button(zoom_frame, text="Zoom In", command=self.zoom_in).pack(
            side=tk.LEFT, padx=2
        )
        ttk.Button(zoom_frame, text="Zoom Out", command=self.zoom_out).pack(
            side=tk.LEFT, padx=2
        )

        # Navigation buttons
        nav_frame = ttk.Frame(control_frame)
        nav_frame.pack(side=tk.RIGHT)

        self.prev_button = ttk.Button(
            nav_frame, text="Previous", command=self.previous_image, state=tk.DISABLED
        )
        self.next_button = ttk.Button(
            nav_frame, text="Next", command=self.next_image, state=tk.DISABLED
        )
        self.prev_button.pack(side=tk.LEFT, padx=2)
        self.next_button.pack(side=tk.LEFT, padx=2)

        # Content area
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)

        # Left panel - Image display
        image_frame = ttk.LabelFrame(content_frame, text="Image with Layout")
        image_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        # Canvas for image with scrollbars
        canvas_frame = ttk.Frame(image_frame)
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.canvas = tk.Canvas(canvas_frame, bg="gray")
        h_scrollbar = ttk.Scrollbar(
            canvas_frame, orient=tk.HORIZONTAL, command=self.canvas.xview
        )
        v_scrollbar = ttk.Scrollbar(
            canvas_frame, orient=tk.VERTICAL, command=self.canvas.yview
        )
        self.canvas.configure(
            xscrollcommand=h_scrollbar.set, yscrollcommand=v_scrollbar.set
        )

        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y, padx=5, pady=5)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5)
        self.canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Right panel - Block selection
        selection_frame = ttk.LabelFrame(content_frame, text="Text Blocks Selection")
        selection_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(5, 0))
        selection_frame.configure(width=300)

        # Select all/none buttons
        button_frame = ttk.Frame(selection_frame)
        button_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(
            button_frame, text="Select All", command=self.select_all_blocks
        ).pack(side=tk.LEFT, padx=2)
        ttk.Button(
            button_frame, text="Select None", command=self.deselect_all_blocks
        ).pack(side=tk.LEFT, padx=2)

        # Scrollable list of blocks
        list_frame = ttk.Frame(selection_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.blocks_listbox = tk.Listbox(list_frame, selectmode=tk.MULTIPLE)
        blocks_scrollbar = ttk.Scrollbar(
            list_frame, orient="vertical", command=self.blocks_listbox.yview
        )
        self.blocks_listbox.configure(yscrollcommand=blocks_scrollbar.set)

        self.blocks_listbox.pack(side="left", fill="both", expand=True)
        blocks_scrollbar.pack(side="right", fill="y")

        # Bind listbox selection
        self.blocks_listbox.bind("<<ListboxSelect>>", self.on_block_selection_change)

        # Preview text area
        preview_frame = ttk.LabelFrame(selection_frame, text="Block Preview")
        preview_frame.pack(fill=tk.X, padx=5, pady=5)

        self.preview_text = tk.Text(preview_frame, height=6, wrap=tk.WORD)
        preview_scrollbar = ttk.Scrollbar(
            preview_frame, orient=tk.VERTICAL, command=self.preview_text.yview
        )
        self.preview_text.configure(yscrollcommand=preview_scrollbar.set)

        self.preview_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        preview_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Bottom frame for action buttons
        action_frame = ttk.Frame(main_frame)
        action_frame.pack(fill=tk.X, pady=(10, 0))

        # Output directory selection
        output_frame = ttk.Frame(action_frame)
        output_frame.pack(side=tk.LEFT, padx=5)

        ttk.Button(
            output_frame, text="Select Output Directory", command=self.select_output_dir
        ).pack(side=tk.LEFT, padx=(0, 5))

        self.output_dir_label = ttk.Label(
            output_frame, text="No output directory selected"
        )
        self.output_dir_label.pack(side=tk.LEFT, padx=(5, 0))

        # Action buttons
        ttk.Button(action_frame, text="Quit", command=self.quit_prog).pack(
            side=tk.RIGHT, padx=5
        )
        ttk.Button(
            action_frame, text="Generate Transcript", command=self.generate_transcript
        ).pack(side=tk.RIGHT, padx=5)

        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready - Select a folder with image(s) to begin")
        status_bar = ttk.Label(
            main_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W
        )
        status_bar.pack(fill=tk.X, pady=(5, 0))

        if load_sample:
            self.image_dir_path = SAMPLES_DIR
            # Initialize with sample images if available
            self.load_images_from_dir()
        else:
            # Initialize with home directory
            self.image_dir_path = Path.home()

    def update_nav_button(self):
        """
        Updates the nav buttons (previous and next) according the image's index
        """
        self.prev_button["state"] = (
            tk.NORMAL if self.current_image_index > 0 else tk.DISABLED
        )
        self.next_button["state"] = (
            tk.NORMAL
            if self.current_image_index < len(self.image_files) - 1
            else tk.DISABLED
        )

    def load_images_from_dir(self, dir_path: Path = SAMPLES_DIR):
        """Load list of sample images"""
        if dir_path.exists():
            self.image_files = list(dir_path.glob("*.jpg"))
            self.current_image_index = 0
            if self.image_files:
                self.load_image(self.image_files[0])
                self.update_nav_button()
        else:
            self.image_files = []
            self.current_image_index = -1

    def update_output_dir_label(self):
        """Update the output directory label with the given path"""
        if self.output_directory is None:
            self.output_dir_label.config(text="No output directory selected")
            return

        display_path = self.output_directory.absolute().as_posix()
        self.output_dir_label.config(text=f"Output: {display_path}")

    def select_image_dir(self):
        """Open file dialog to select an image directory"""
        self.image_dir_path = filedialog.askdirectory(
            title="Select Magazine Image Directory",
            mustexist=True,
            initialdir=Path.home(),
        )
        if self.image_dir_path:
            self.load_images_from_dir(Path(self.image_dir_path))

    def select_output_dir(self):
        """Open file dialog to select an output directory"""
        dir_path = filedialog.askdirectory(
            title="Select Output Directory",
            mustexist=False,
            initialdir=self.image_dir_path,
        )
        if dir_path:
            self.output_directory = Path(dir_path)
            # Update the label to show the selected directory
            self.update_output_dir_label()

    def previous_image(self):
        """Load previous image in the list"""
        if self.image_files and self.current_image_index > 0:
            self.current_image_index -= 1
            self.load_image(self.image_files[self.current_image_index])
        self.update_nav_button()

    def next_image(self):
        """Load next image in the list"""
        if self.image_files and self.current_image_index < len(self.image_files) - 1:
            self.current_image_index += 1
            self.load_image(self.image_files[self.current_image_index])
        self.update_nav_button()

    def load_image(self, image_path):
        """Load and analyze an image"""
        if self.status_var is None:
            return

        self.status_var.set("Loading and analyzing image...")
        self.root.update()

        try:
            self.current_image_path = image_path
            if self.file_label is not None:
                self.file_label.config(text=image_path.name)

            # Create analyzer and perform OCR
            self.current_analyzer = MagazineLayoutAnalyzer(image_path)
            self.blocks_data = self.current_analyzer.analyze_with_tesseract()[1].blocks

            # Display image with overlays
            self.display_image_with_overlays()

            # Populate blocks list
            self.populate_blocks_list()

            # Select all blocks by default
            self.select_all_blocks()

            if self.status_var is not None:
                self.status_var.set(f"Loaded: {image_path.name}")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load image: {str(e)}")
            if self.status_var is not None:
                self.status_var.set("Error loading image")

    def generate_highlights(self) -> cv2.typing.MatLike | None:
        """Update highlights on the canvas for selected blocks"""
        if (
            not self.blocks_data
            or self.original_image is None
            or self.blocks_listbox is None
        ):
            return

        annotated = self.original_image.copy()
        # Get selected block indices
        selected_indices = self.blocks_listbox.curselection()

        for index in selected_indices:
            block_text = self.blocks_listbox.get(index)
            block_id = int(block_text.split(":")[0].replace("Block ", ""))

            if block_id in self.blocks_data:
                block = self.blocks_data[block_id]

                # Calculate coordinates with zoom
                x1 = block.left
                y1 = block.top
                x2 = block.left + block.width
                y2 = block.top + block.height

                # Create highlight rectangle with semi-transparent fill
                cv2.rectangle(annotated, (x1, y1), (x2, y2), (203, 250, 50), cv2.FILLED)
        return annotated

    def update_image_display(self):
        """Update the image display with current zoom level"""
        if self.original_image is None or self.canvas is None:
            return

        # Redraw highlights for selected blocks
        annotated = self.generate_highlights()

        if annotated is None:
            return

        image_new = cv2.addWeighted(
            annotated, self.alpha, self.original_image, 1 - self.alpha, 0
        )
        img_rgb = Image.fromarray(cv2.cvtColor(image_new, cv2.COLOR_BGR2RGB))

        # Calculate new size based on zoom level
        original_width, original_height = img_rgb.size
        new_width = int(original_width * self.zoom_level)
        new_height = int(original_height * self.zoom_level)

        # Resize image
        resized_image = img_rgb.resize(
            (new_width, new_height), Image.Resampling.LANCZOS
        )

        # Convert to PhotoImage and display
        self.photo = ImageTk.PhotoImage(resized_image)
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def zoom_in(self):
        """Increase zoom level"""
        if self.original_image is not None:
            self.zoom_level = min(self.zoom_level * 1.15, 5.0)  # Max zoom 5x
            self.update_image_display()

    def zoom_out(self):
        """Decrease zoom level"""
        if self.original_image is not None:
            self.zoom_level = max(self.zoom_level / 1.15, 0.1)  # Min zoom 0.1x
            self.update_image_display()

    def display_image_with_overlays(self):
        """Display image with block overlays"""
        if self.current_analyzer is None:
            return

        # Create image with overlays
        # Store as original
        self.original_image = self.current_analyzer.add_block_overlay(self.blocks_data)

        # Update display
        self.update_image_display()

    def populate_blocks_list(self):
        """Populate the blocks listbox with available blocks"""
        if self.blocks_listbox is None:
            return

        self.blocks_listbox.delete(0, tk.END)

        for block_id, block in self.blocks_data.items():
            block_text = block.get_text()
            if not block_text:
                continue

            # Get text from this block
            preview = block_text[:50] + "..." if len(block_text) > 50 else block_text

            self.blocks_listbox.insert(tk.END, f"Block {block_id}: {preview}")

    def select_all_blocks(self):
        """Select all blocks in the listbox"""
        if self.blocks_listbox is None:
            return
        self.blocks_listbox.select_set(0, tk.END)
        self.on_block_selection_change()

    def deselect_all_blocks(self):
        """Deselect all blocks in the listbox"""
        if self.blocks_listbox is None:
            return
        self.blocks_listbox.select_clear(0, tk.END)
        self.on_block_selection_change()

    def on_block_selection_change(self, event=None):
        """Handle block selection changes"""
        if self.blocks_listbox is None or self.preview_text is None:
            return

        selected_indices = self.blocks_listbox.curselection()

        if selected_indices:
            # Show preview of the last selected block
            last_selected = selected_indices[-1]
            block_text = self.blocks_listbox.get(last_selected)
            block_id = int(block_text.split(":")[0].replace("Block ", ""))

            preview_text = self.blocks_data[block_id].get_text()
            self.preview_text.delete(1.0, tk.END)
            self.preview_text.insert(1.0, preview_text)
        else:
            self.preview_text.delete(1.0, tk.END)

        # Update highlights on the image
        self.update_image_display()

    def generate_transcript(self):
        """Generate transcript from selected blocks"""
        if not self.current_image_path:
            messagebox.showwarning("Warning", "No image loaded")
            return

        if self.blocks_listbox is None:
            messagebox.showwarning("Warning", "UI not properly initialized")
            return

        selected_indices = self.blocks_listbox.curselection()
        if not selected_indices:
            messagebox.showwarning("Warning", "No blocks selected")
            return

        # Check if output directory is set, prompt if not
        if self.output_directory is None:
            dir_path = filedialog.askdirectory(
                title="Select Output Directory for Transcript",
                mustexist=False,
                initialdir=self.image_dir_path,
            )
            if not dir_path:
                return  # User cancelled
            self.output_directory = Path(dir_path)
            # Update the label
            self.update_output_dir_label()

        try:
            blocks = {}
            for index in selected_indices:
                block_text = self.blocks_listbox.get(index)
                block_id = int(block_text.split(":")[0].replace("Block ", ""))
                blocks[block_id] = self.blocks_data[block_id]

            if self.current_analyzer is None:
                messagebox.showerror("Error", "No analyzer available")
                return

            paths = self.current_analyzer.generate_transcript(
                self.output_directory, blocks
            )

            messagebox.showinfo(
                "Success",
                "Saved to:\n"
                + "\n".join([f"{key}: {value}" for key, value in paths.items()]),
                icon="info",
            )

            if self.status_var is not None:
                self.status_var.set(
                    f"Transcript saved for {self.current_image_path.name}"
                )

        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate transcript: {str(e)}")

    def quit_prog(self):
        """Cancel current operation and reset selections"""
        self.root.destroy()


def main():
    """Main function to run the interactive transcriber"""
    root = tk.Tk()
    InteractiveTranscriber(root)
    root.mainloop()


if __name__ == "__main__":
    main()

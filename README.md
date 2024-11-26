# PDF curator

PDF Curator is a tool designed to convert any PDF file into a structured JSON format. Using OCR, Layout Detection, and Image Captioning techniques, the resulting JSON file captures key document elements, including:
- Text from individual pages
- Coordinates of text blocks
- Chapter headings and chapter lists
- Coordinates and descriptions of non-text elements
- A list of non-text elements, and more.

```ruby
{
    "metadata": {},
    "pages": [
        {
            "page":
            "detections": [
                {
                    "class":
                    "bbox":
                    "text": 
                    "description":
                }
            ]
        }
    ]
}
```

The software also includes a user-friendly GUI for managing PDFs and their JSON files. You can edit text, rename chapters, add new ones, and interact with non-text elements in the document.

The software is modular, allowing users to replace or upgrade any component used for converting PDFs to JSON with newer or more suitable techniques/models as needed.

# Installation

Two installation options are available: full installation or GUI-only installation.
- Full Installation: Includes all libraries required for automated PDF-to-JSON conversion and the GUI.
- GUI-Only Installation: Installs only the components necessary to run the GUI for manual conversion.

## Full Installation

We recommend installing in a dedicated virtual environment using tools like venv or Anaconda. Python version 3.9 or later is required.

#### Steps:

1.	Clone the repository:

```
git clone https://github.com/FilipJy/PDFcurator.git
```

2.	Install dependencies:

```
cd PDFcurator
pip install -r requirements.txt
```

3.	Install Tesseract:

Ensure the Tesseract OCR engine is installed separately from the pytesseract library. Follow the instructions here - https://tesseract-ocr.github.io/tessdoc/Installation.html

4.	Download the Layout Detection Model:

Since the software is designed to allow the use of the most suitable systems/models for each task, the Layout Detection model is not included. By default, the Layout Detection component is configured to use a pre-trained YOLO model. The model should be placed in the PDFcurator/data/models folder, and the path can be adjusted in PDFcurator/data/core/parsing_utils/layout_detection.py:

```ruby
def _initialize_detector():
    model_path = "PATH_TO_DETECTION_MODEL"  
    return LayoutDetector(model_path=model_path)
```
The default path is set to /data/models/*.pt.

As an example, We recommend using the model “yolov11x_best.pt” from YOLOv11 Document Layout Analysis, trained on the DocLayNet-base dataset - https://github.com/moured/YOLOv11-Document-Layout-Analysis. To simplify, a script named example.py is provided in PDFcurator/data/models to download and save the model to the required folder:

```
cd PDFcurator/data/models
python example.py
```

#### Running the Software:

Software spustíte 

```
cd PDFcurator
python run.py
```

On first launch, the software will automatically download additional required models like GOT_OCR2 and moondream2.

## GUI-Only Installation

If you prefer to use the GUI for manual PDF conversion without automated processing, install the reduced dependencies:

```
cd PDFcurator
pip install -r requirements_gui.txt
```

#### Running the GUI:

Run the GUI with:

```
cd PDFcurator
python run_gui.py
```

# Features of Automatic Conversion

All components used for automatic conversion are modular, making them easily replaceable or customizable.

## OCR

OCR extracts text from the document. The software supports three OCR engines:


1.	Tesseract OCR: A widely used and reliable engine. - https://github.com/tesseract-ocr/tesseract

2.	PaddleOCR: Suitable for more complex layouts and text elements. - https://github.com/PaddlePaddle/PaddleOCR

3.	GOT-OCR2.0: An advanced multimodal OCR engine. - https://github.com/Ucas-HaoranWei/GOT-OCR2.0


Tesseract and PaddleOCR come pre-configured with a few basic languages, but more can be added with minor code modifications. All engines are configured to run on CPU by default, but GPU acceleration is supported (recommended for GOT-OCR2.0).

## Image Captioning

Image Captioning generates human-readable descriptions of non-text elements like images. These descriptions are included in the JSON file and can be used during export to other formats, such as alt text for images.

By default, the moondream2 model is used - https://github.com/vikhyat/moondream
Other models, such as omnivision-968M, can also be used - https://huggingface.co/NexaAIDev/omnivision-968M

## Layout Detection

By default, the software uses a pre-trained YOLO model for layout detection, though this can be replaced with alternatives. Layout Detection identifies text blocks, headings, and non-text elements, passing these details to the OCR and Image Captioning systems. All results are saved in JSON.

# GUI Features

The GUI allows you to refine the JSON file or manually convert PDFs to JSON. Its primary functions include editing text, managing non-text elements, and marking chapter headings, making the JSON suitable for exporting to other formats like EPUB or layered PDFs.

### Text Editing

- Edit, delete, or create new text.
- Mark text as a chapter start.

Switch between two modes:
- Block Mode: Edit entire text blocks detected by Layout Detection.
- Word Mode: Edit individual words.

Clicking a block or word opens an edit window for modifications. Chapter lists are displayed on the right, showing chapter names and page numbers. Double-click a chapter to navigate to its page. Right-click to rename or delete chapters.

### Managing Non-Text Elements

Automatically detected non-text elements are listed on the right. You can rename or delete these elements. Alternatively, in Image Mode, non-text elements can be manually marked on the PDF.

## Export

One of the key advantages of converting a document to JSON format is the ability to transform it into other human-readable formats. We have chosen PDF, EPUB, and TXT as the primary export options. Each of these formats presents unique challenges, and there are various approaches to handling the export process. For this reason, we have focused on implementing only basic methods, providing users with the flexibility to adapt or expand them according to their needs. This is an area we plan to develop further in future versions of the software. For instance, one of our objectives is to enable the creation of near-perfect replicas of original PDF documents while incorporating all the benefits of the extracted and processed data.

## Metadata

Metadata can be added manually or fetched via the Google Books API using an ISBN.

# Acknowledgment

The software was funded by the Institutional support for long term conceptual development of a research organization (The Moravian Library) by the Czech Ministry of Culture.






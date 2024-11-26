from reportlab.lib.pagesizes import letter, A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
import fitz
import os
import tkinter as tk
from tkinter import messagebox, filedialog
from PIL import Image
import uuid

class PDFExporter:
    def __init__(self, data, metadata, pdf_path):
        self.data = data
        self.metadata = metadata
        self.pdf_path = pdf_path

    def export_to_pdf(self, parent):
        if not self.validate_metadata_and_toc():
            messagebox.showerror("Error", "Metadata and Table of Contents are required to export to PDF.")
            return

        file_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
        if not file_path:
            return

        
        page_size = letter
        if self.metadata.get("Page Size") == "A4":
            page_size = A4

        c = canvas.Canvas(file_path, pagesize=page_size)
        width, height = page_size

        
        chapter_starts = []
        for page_data in self.data['pages']:
            if page_data.get('ignore', False):
                continue
            for detection in page_data.get('detections', []):
                if detection.get('class') == 'Section-header':
                    chapter_starts.append((page_data, detection))

        for idx, (chapter_page_data, chapter_detection) in enumerate(chapter_starts):
            chapter_title = chapter_detection['text']
            chapter_content, chapter_images = self.get_chapter_content(chapter_detection)

            
            c.setFont("Times-Bold", 16)
            c.drawCentredString(width / 2, height - inch, chapter_title)
            c.setFont("Times-Roman", 12)
            y_position = height - inch * 1.5

            for element in chapter_content:
                if element['type'] == 'text':
                    text = element['text']
                    lines = self.wrap_text(text, c, width - 2 * inch)
                    for line in lines:
                        if y_position < inch:
                            c.showPage()
                            c.setFont("Times-Roman", 12)
                            y_position = height - inch
                        c.drawString(inch, y_position, line)
                        y_position -= 14  
                elif element['type'] == 'image':
                    img_filename = self.process_image(element['detection'], element['page_data'])
                    if os.path.exists(img_filename):
                        img = Image.open(img_filename)
                        img_width, img_height = img.size
                        aspect = img_height / float(img_width)

                        
                        display_width = width - 2 * inch
                        display_height = display_width * aspect

                        if y_position - display_height < inch:
                            c.showPage()
                            c.setFont("Times-Roman", 12)
                            y_position = height - inch

                        c.drawImage(img_filename, inch, y_position - display_height, width=display_width, height=display_height)
                        y_position -= (display_height + inch / 2)
                        
                        os.remove(img_filename)

            c.showPage()

        c.save()
        messagebox.showinfo("Success", f"PDF exported successfully to {file_path}")

    def validate_metadata_and_toc(self):
        required_metadata_fields = ["Title", "Author"]
        for field in required_metadata_fields:
            if not self.metadata.get(field):
                return False
        toc_exists = any(
            detection.get('class') == 'Section-header'
            for page_data in self.data['pages']
            if not page_data.get('ignore', False)
            for detection in page_data.get('detections', [])
        )
        return toc_exists

    def get_chapter_content(self, chapter_detection):
        elements = []
        collecting = False

        for page_data in self.data['pages']:
            if page_data.get('ignore', False):
                continue
            detections = page_data.get('detections', [])
            for detection in detections:
                if detection.get('class') == 'Section-header' and detection == chapter_detection:
                    collecting = True
                    elements.append({'type': 'chapter_start', 'text': detection['text']})
                elif detection.get('class') == 'Section-header' and collecting:
                    
                    collecting = False
                    break
                elif collecting:
                    if detection.get('class') == 'Text':
                        elements.append({'type': 'text', 'text': detection['text']})
                    elif detection.get('class') == 'Picture':
                        elements.append({'type': 'image', 'detection': detection, 'page_data': page_data})
            if not collecting and 'collecting' not in locals():
                
                break

        return elements, []

    def wrap_text(self, text, canvas, max_width):
        words = text.split()
        lines = []
        line = ""
        for word in words:
            if canvas.stringWidth(line + " " + word if line else word, "Times-Roman", 12) < max_width:
                line += (" " if line else "") + word
            else:
                lines.append(line)
                line = word
        if line:
            lines.append(line)
        return lines

    def process_image(self, detection, page_data):
        page_num = page_data['page'] - 1  
        bbox = detection['bbox']

        doc = fitz.open(self.pdf_path)
        page = doc.load_page(page_num)
        pix = page.get_pixmap()
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        doc.close()

        x1, y1, x2, y2 = bbox
        cropped_img = img.crop((min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2)))

        unique_id = uuid.uuid4().hex
        img_filename = f'img_{unique_id}.jpg'
        cropped_img.save(img_filename, 'JPEG')

        return img_filename

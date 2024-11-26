from ebooklib import epub
import fitz
import os
import json
import tkinter as tk
from tkinter import messagebox, filedialog
from PIL import Image
import uuid  

class EPUBExporter:
    def __init__(self, data, metadata, pdf_path):
        self.data = data
        self.metadata = metadata
        self.pdf_path = pdf_path
        self.image_counter = 0  

    def export_to_epub(self, parent):
        if not self.validate_metadata_and_toc():
            messagebox.showerror("Error", "Metadata and Table of Contents are required to export to EPUB.")
            return

        file_path = filedialog.asksaveasfilename(defaultextension=".epub", filetypes=[("EPUB files", "*.epub")])
        if not file_path:
            return

        book = epub.EpubBook()

        self.set_metadata(book)

        spine = ['nav']
        toc = []

        
        chapter_starts = []
        for page_data in self.data['pages']:
            if page_data.get('ignore', False):
                continue
            for detection in page_data.get('detections', []):
                if detection.get('class') == 'Section-header':
                    chapter_starts.append((page_data, detection))

        image_filenames = []  

        for idx, (chapter_page_data, chapter_detection) in enumerate(chapter_starts):
            chapter_title = chapter_detection['text']  
            chapter_content, chapter_image_filenames = self.get_chapter_content(chapter_detection)
            image_filenames.extend(chapter_image_filenames)
            chapter = epub.EpubHtml(title=chapter_title, file_name=f'chap_{idx}.xhtml', lang='en')
            chapter.content = chapter_content
            book.add_item(chapter)
            spine.append(chapter)
            toc.append(epub.Link(chapter.file_name, chapter_title, f'chap_{idx}'))

        book.toc = toc
        book.spine = spine
        book.add_item(epub.EpubNcx())
        book.add_item(epub.EpubNav())

        style = '''
        body {
            font-family: Times, Times New Roman, serif;
            font-size: 14px;
            line-height: 1.5;
            margin: 0;
            padding: 0;
        }
        h1 {
            font-size: 1.5em;
            text-align: center;
            margin-top: 1em;
            margin-bottom: 1em;
        }
        p {
            font-size: 1em;
            text-indent: 1.2em;
            margin-top: 0;
            margin-bottom: 1em;
        }
        .chapter-start {
            font-size: 1.5em;
            text-align: center;
            margin-top: 1em;
            margin-bottom: 1em;
            font-weight: bold;
        }
        .image {
            text-align: center;
            margin-top: 1em;
            margin-bottom: 1em;
        }
        '''

        nav_css = epub.EpubItem(uid="style_nav", file_name="style/nav.css", media_type="text/css", content=style)
        book.add_item(nav_css)

        
        for img_filename in set(image_filenames):  
            img_item = epub.EpubItem(
                uid=img_filename,
                file_name=img_filename,
                media_type='image/jpeg',
                content=open(img_filename, 'rb').read()
            )
            book.add_item(img_item)

        epub.write_epub(file_path, book, {})

        
        for img_file in set(image_filenames):
            if os.path.exists(img_file):
                os.remove(img_file)

        messagebox.showinfo("Success", f"EPUB exported successfully to {file_path}")

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

    def set_metadata(self, book):
        book.set_identifier('id123456')
        book.set_title(self.metadata.get("Title", "Untitled"))
        book.set_language(self.metadata.get("Language", "en"))
        book.add_author(self.metadata.get("Author", "Unknown"))
        book.add_metadata('DC', 'publisher', self.metadata.get("Publisher", "Unknown"))
        for meta_field in ["ISBN", "Edition", "Genre", "Original Title"]:
            value = self.metadata.get(meta_field)
            if value:
                book.add_metadata('DC', meta_field.lower().replace(' ', '_'), value)

    def get_chapter_content(self, chapter_detection):
        elements = []
        collecting = False
        image_filenames = []

        chapter_start_found = False

        for page_data in self.data['pages']:
            if page_data.get('ignore', False):
                continue
            detections = page_data.get('detections', [])
            for detection in detections:
                if detection.get('class') == 'Section-header' and detection == chapter_detection:
                    collecting = True
                    chapter_start_found = True
                    elements.append({'type': 'chapter_start', 'text': detection['text']})
                elif detection.get('class') == 'Section-header' and chapter_start_found:
                    
                    collecting = False
                    break
                elif collecting:
                    if detection.get('class') == 'Text':
                        elements.append({'type': 'text', 'text': detection['text']})
                    elif detection.get('class') == 'Picture':
                        elements.append({'type': 'image', 'detection': detection, 'page_data': page_data})
            if not collecting and chapter_start_found:
                
                break

        
        content, image_filenames = self.format_chapter_content(elements)
        return content, image_filenames

    def format_chapter_content(self, elements):
        content = ''
        image_filenames = []

        for element in elements:
            if element['type'] == 'chapter_start':
                content += f'<h1>{element["text"]}</h1>\n'
            elif element['type'] == 'text':
                content += f'<p>{element["text"]}</p>\n'
            elif element['type'] == 'image':
                
                img_filename = self.process_image(element['detection'], element['page_data'])
                image_filenames.append(img_filename)
                content += f'<div class="image"><img src="{img_filename}" alt="Image"/></div>\n'

        return content, image_filenames

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

    def open_export_window(self, parent):
        confirm = messagebox.askyesno("Export to EPUB", "Are you sure you want to export to EPUB?")
        if confirm:
            self.export_to_epub(parent)

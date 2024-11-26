import tkinter as tk
from tkinter import messagebox, filedialog
import os

class TextExporter:
    def __init__(self, data, metadata, pdf_path):
        self.data = data
        self.metadata = metadata
        self.pdf_path = pdf_path

    def export_to_txt(self, parent):
        if not self.validate_metadata_and_toc():
            messagebox.showerror("Error", "Metadata and Table of Contents are required to export to Plain Text.")
            return

        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
        if not file_path:
            return

        with open(file_path, 'w', encoding='utf-8') as txt_file:
            
            txt_file.write(f"Title: {self.metadata.get('Title', 'Untitled')}\n")
            txt_file.write(f"Author: {self.metadata.get('Author', 'Unknown')}\n")
            txt_file.write(f"Publisher: {self.metadata.get('Publisher', 'Unknown')}\n")
            txt_file.write(f"ISBN: {self.metadata.get('ISBN', 'N/A')}\n")
            txt_file.write(f"Edition: {self.metadata.get('Edition', 'N/A')}\n")
            txt_file.write(f"Genre: {self.metadata.get('Genre', 'N/A')}\n")
            txt_file.write(f"Original Title: {self.metadata.get('Original Title', 'N/A')}\n")
            txt_file.write("\n")

            
            chapter_starts = []
            for page_data in self.data['pages']:
                if page_data.get('ignore', False):
                    continue
                for detection in page_data.get('detections', []):
                    if detection.get('class') == 'Section-header':
                        chapter_starts.append((page_data, detection))

            for idx, (chapter_page_data, chapter_detection) in enumerate(chapter_starts):
                chapter_title = chapter_detection['text']
                txt_file.write(f"{chapter_title}\n")
                txt_file.write("=" * len(chapter_title) + "\n\n")

                chapter_content = self.get_chapter_content(chapter_detection)

                for element in chapter_content:
                    if element['type'] == 'text':
                        text = element['text']
                        txt_file.write(text + "\n\n")
                txt_file.write("\n\n")

        messagebox.showinfo("Success", f"Plain Text exported successfully to {file_path}")

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
            if not collecting and 'collecting' not in locals():
                
                break

        return elements

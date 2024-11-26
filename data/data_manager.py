import json
import os
import fitz  
from tkinter import messagebox

class DataManager:
    def __init__(self, json_path, pdf_path):
        self.json_path = json_path
        self.pdf_path = pdf_path
        self.data = {}
        self.metadata = {}
        self.doc = None

        self.load_data()

    def load_data(self):
        try:
            if not os.path.exists(self.json_path):
                messagebox.showerror("Error", f"JSON file not found: {self.json_path}")
                return
            else:
                with open(self.json_path, 'r', encoding='utf-8') as f:
                    self.data = json.load(f)
            self.doc = fitz.open(self.pdf_path)

            self.metadata = self.data.get("metadata", {})

            self.image_counter = 0
            self.chapter_counter = 0

            for page_data in self.data['pages']:
                page_data['ignore'] = page_data.get('ignore', False)
                page_data['index'] = self.data['pages'].index(page_data)

                detections = page_data.get('detections', [])
                for idx, detection in enumerate(detections):
                    detection['id'] = detection.get('id', idx)
                    if detection['class'] == 'Picture':
                        if 'name' not in detection:
                            detection['name'] = f"image_{self.image_counter}"
                            self.image_counter += 1
                        else:
                            try:
                                idx = int(detection['name'].split('_')[1])
                                if idx >= self.image_counter:
                                    self.image_counter = idx + 1
                            except (IndexError, ValueError):
                                pass  
                    if detection.get('class') == 'Section-header':
                        if 'name' not in detection:
                            detection['name'] = detection['text']
                            self.chapter_counter += 1
                        else:
                            try:
                                idx = int(detection['name'].split(' ')[1])
                                if idx >= self.chapter_counter:
                                    self.chapter_counter = idx
                            except (IndexError, ValueError):
                                pass  

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while loading data: {e}")

    def save_data(self):
        with open(self.json_path, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=4, ensure_ascii=False)

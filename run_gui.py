import tkinter as tk
from tkinter import filedialog, messagebox
import logging
import os
import json
import fitz  

from data.core.main_gui import PDFViewer  

class StartGUIApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("PDF Curator - Start")
        self.geometry("400x200")  

        self.label = tk.Label(self, text="Welcome to PDF Curator", font=("Helvetica", 16))
        self.label.pack(pady=10)

        self.load_button = tk.Button(self, text="Load PDF and JSON", command=self.load_files)
        self.load_button.pack(pady=5)

        self.new_button = tk.Button(self, text="New PDF", command=self.new_pdf)
        self.new_button.pack(pady=5)

        self.pdf_path = None
        self.json_path = None

    def load_files(self):
        
        pdf_file_path = filedialog.askopenfilename(title="Select PDF File", filetypes=[("PDF files", "*.pdf")])
        if not pdf_file_path:
            messagebox.showerror("Error", "No PDF file selected.")
            return

        json_file_path = filedialog.askopenfilename(title="Select JSON File", filetypes=[("JSON files", "*.json")])
        if not json_file_path:
            messagebox.showerror("Error", "No JSON file selected.")
            return

        self.pdf_path = pdf_file_path
        self.json_path = json_file_path
        self.start_pdf_viewer(self.pdf_path, self.json_path)

    def new_pdf(self):
        
        pdf_file_path = filedialog.askopenfilename(title="Select PDF File", filetypes=[("PDF files", "*.pdf")])
        if not pdf_file_path:
            messagebox.showerror("Error", "No PDF file selected.")
            return
 
        json_file_path = self.create_empty_json(pdf_file_path)
        self.pdf_path = pdf_file_path
        self.json_path = json_file_path
        self.start_pdf_viewer(self.pdf_path, self.json_path)

    def create_empty_json(self, pdf_path):
        json_file = os.path.splitext(os.path.basename(pdf_path))[0] + ".json"
        json_path = os.path.join(os.path.dirname(pdf_path), json_file)
        
        pdf_document = fitz.open(pdf_path)
        num_pages = pdf_document.page_count
        
        empty_json_structure = {
            "metadata": {},
            "pages": [
                {
                    "page": i + 1,
                    "detections": [],
                    "ignore": False,
                    "index": i
                } for i in range(num_pages)
            ]
        }
        
        with open(json_path, 'w') as json_file:
            json.dump(empty_json_structure, json_file)  
        return json_path

    def start_pdf_viewer(self, pdf_path, json_path):
        
        self.destroy()
        PDFViewer(json_path, pdf_path).mainloop()

if __name__ == '__main__':
    

    app = StartGUIApp()
    app.mainloop()
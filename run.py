import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import threading
import time
import importlib.util
import logging
import queue  

from data.core.main_gui import PDFViewer  

class StartApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("PDF Curator - Start")
        self.geometry("400x200")  
        
        self.label = tk.Label(self, text="Welcome to PDF Curator", font=("Helvetica", 16))
        self.label.pack(pady=10)

        self.load_button = tk.Button(self, text="Load JSON", command=self.load_json_workflow)
        self.load_button.pack(pady=5)

        self.create_button = tk.Button(self, text="Create JSON", command=self.create_json_workflow)
        self.create_button.pack(pady=5)

        self.pdf_path = None
        self.json_path = None

    def load_json_workflow(self):
        
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

    def create_json_workflow(self):
        
        self.destroy()
        OCRConfigWindow()

    def start_pdf_viewer(self, pdf_path, json_path):
        
        self.destroy()
        PDFViewer(json_path, pdf_path).mainloop()

class OCRConfigWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("OCR Configuration")
        self.geometry("400x350")

        self.ocr_model_label = tk.Label(self, text="Select OCR Model:", font=("Helvetica", 12))
        self.ocr_model_label.pack(pady=5)

        self.ocr_model_var = tk.StringVar(value="GOT-OCR2_CPU")
        self.ocr_model_options = ["GOT-OCR2_CPU", "Tesseract", "PaddleOCR"]
        self.ocr_model_menu = ttk.Combobox(self, textvariable=self.ocr_model_var, values=self.ocr_model_options, state="readonly")
        self.ocr_model_menu.pack(pady=5)
        self.ocr_model_menu.bind("<<ComboboxSelected>>", self.on_ocr_model_change)

        self.language_label = tk.Label(self, text="Select Language:", font=("Helvetica", 12))
        self.language_var = tk.StringVar()
        self.language_options = []
        self.language_menu = ttk.Combobox(self, textvariable=self.language_var, values=self.language_options, state="readonly")

        self.use_captioning_var = tk.BooleanVar(value=False)
        self.caption_checkbox = tk.Checkbutton(self, text="Use Image Captioning", variable=self.use_captioning_var)
        self.caption_checkbox.pack(pady=5)

        self.open_pdf_button = tk.Button(self, text="Select PDF and Start OCR", command=self.process_pdf)
        self.open_pdf_button.pack(pady=10)

        self.pdf_path = None
        self.json_path = None
        self.progress_bar = ttk.Progressbar(self, orient='horizontal', mode='determinate')
        self.ocr_thread = None
        self.start_time = None  
        self.ocr_exception = None  

        self.on_ocr_model_change()

    def on_ocr_model_change(self, event=None):
        selected_model = self.ocr_model_var.get()
        if selected_model in ["Tesseract", "PaddleOCR"]:
            
            self.language_label.pack(pady=5)
            self.language_menu.pack(pady=5)
            
            if selected_model == "Tesseract":
                self.language_options = ["eng", "ces", "deu"]
                
                self.language_menu['values'] = self.language_options
                self.language_var.set(self.language_options[0])
                
                self.language_menu.unbind("<<ComboboxSelected>>")
            elif selected_model == "PaddleOCR":
                self.language_options = {
                    "English": "en",
                    "Czech": "cs",
                    "German": "german"
                    
                }
                self.language_menu['values'] = list(self.language_options.keys())
                self.language_var.set(list(self.language_options.keys())[0])
                
                self.language_menu.bind("<<ComboboxSelected>>", self.on_language_change)
                
                self.on_language_change()
        else:
            
            self.language_label.pack_forget()
            self.language_menu.pack_forget()

    def on_language_change(self, event=None):
        selected_language_name = self.language_menu.get()
        language_code = self.language_options.get(selected_language_name, 'en')
        self.language_var.set(language_code)

    def process_pdf(self):
        pdf_file_path = filedialog.askopenfilename(title="Select PDF File", filetypes=[("PDF files", "*.pdf")])
        if not pdf_file_path:
            messagebox.showerror("Error", "No PDF file selected.")
            return

        self.pdf_path = pdf_file_path
        output_json = self.get_json_path(self.pdf_path)
        self.json_path = output_json

        selected_model = self.ocr_model_var.get()
        if selected_model in ['Tesseract', 'PaddleOCR']:
            language = self.language_var.get()
        else:
            language = None

        use_captioning = self.use_captioning_var.get()

        self.open_pdf_button.config(state='disabled')

        self.progress_label = tk.Label(self, text="Generating JSON...", font=("Helvetica", 12))
        self.progress_label.pack(pady=5)

        self.progress_bar.pack(pady=5, padx=20, fill=tk.X)
        self.progress_bar['value'] = 0
        self.update_idletasks()

        self.start_time = time.time()

        self.ocr_exception = None

        self.progress_queue = queue.Queue()

        self.ocr_thread = threading.Thread(target=self.run_ocr, args=(self.pdf_path, output_json, selected_model, language, use_captioning))
        self.ocr_thread.start()
 
        self.process_queue()

    def run_ocr(self, pdf_path, output_json, selected_model, language, use_captioning):
        
        if selected_model == "GOT-OCR2_CPU":
            module_name = "data/core/parsing_utils/ocr_got_cpu"
            ocr_kwargs = {}
        elif selected_model == "Tesseract":
            module_name = "data/core/parsing_utils/ocr_tesseract"
            ocr_kwargs = {'language': language}
        elif selected_model == "PaddleOCR":
            module_name = "data/core/parsing_utils/ocr_paddle"
            ocr_kwargs = {'language': language}
        else:
            logging.error(f"Unsupported OCR model selected: {selected_model}")
            self.ocr_exception = Exception(f"Unsupported OCR model selected: {selected_model}")
            return

        try:
            
            script_dir = os.path.dirname(os.path.abspath(__file__))
            module_path = os.path.join(script_dir, f"{module_name}.py")

            
            if not os.path.isfile(module_path):
                raise FileNotFoundError(f"OCR module file not found: {module_path}")

            spec = importlib.util.spec_from_file_location(module_name, module_path)
            ocr_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(ocr_module)

            
            ocr_module.extract_text_from_pdf(pdf_path, output_json, self.progress_queue, use_captioning=use_captioning, **ocr_kwargs)
            self.ocr_exception = None  
        except Exception as e:
            logging.error(f"Error during OCR processing: {e}")
            self.ocr_exception = e  

    def process_queue(self):
        try:
            while True:
                progress = self.progress_queue.get_nowait()
                self._update_progress_ui(progress)
                self.progress_queue.task_done()
        except queue.Empty:
            pass
        if self.ocr_thread.is_alive():
            self.after(100, self.process_queue)
        else:
            
            if self.ocr_exception:
                
                message = f"An error occurred during OCR processing:\n{self.ocr_exception}"
                messagebox.showerror("OCR Error", message)
                self.reset_ui()
            else:
                
                self.progress_bar.pack_forget()
                self.progress_label.pack_forget()
                if hasattr(self, 'time_remaining_label'):
                    self.time_remaining_label.pack_forget()
                
                self.open_pdf_button.config(state='normal')
                
                self.start_pdf_viewer(self.pdf_path, self.json_path)

    def _update_progress_ui(self, progress):
        self.progress_bar['value'] = progress * 100
        self.update_idletasks()
        
        elapsed_time = time.time() - self.start_time
        if progress > 0:
            total_estimated_time = elapsed_time / progress
            time_remaining = total_estimated_time - elapsed_time
            mins, secs = divmod(int(time_remaining), 60)
            time_format = f"Estimated time remaining: {mins} min {secs} sec"
        else:
            time_format = "Calculating time remaining..."
        
        if hasattr(self, 'time_remaining_label'):
            self.time_remaining_label.config(text=time_format)
        else:
            self.time_remaining_label = tk.Label(self, text=time_format)
            self.time_remaining_label.pack(pady=5)

    def reset_ui(self):
        
        self.progress_bar.pack_forget()
        self.progress_label.pack_forget()
        if hasattr(self, 'time_remaining_label'):
            self.time_remaining_label.pack_forget()
        self.open_pdf_button.config(state='normal')

    def get_json_path(self, pdf_path):
        json_file = os.path.splitext(os.path.basename(pdf_path))[0] + ".json"
        return os.path.join(os.path.dirname(pdf_path), json_file)

    def start_pdf_viewer(self, pdf_path, json_path):
        
        self.destroy()
        PDFViewer(json_path, pdf_path).mainloop()

if __name__ == '__main__':


    app = StartApp()
    app.mainloop()

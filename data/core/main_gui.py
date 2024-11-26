
import platform
import tkinter as tk
from tkinter import messagebox, simpledialog
from PIL import Image
from tkinter import font as tkFont

from data.data_manager import DataManager
from image_utils.image_utils import ImageUtils
from handlers.event_handlers import EventHandlers
from image_utils.image_bbox import ImageBBoxMode
from data.exporters.export_epub import EPUBExporter
from data.metadata.metadata_manager import MetadataManager
from data.exporters.export_pdf import PDFExporter
from data.exporters.export_plain import TextExporter

from handlers.on_click_handler import handle_click  

class PDFViewer(tk.Tk):
    def __init__(self, json_path, pdf_path):
        super().__init__()
        self.title("PDF Viewer and Editor")
        self.geometry("1400x800")
        self.json_path = json_path
        self.pdf_path = pdf_path

        self.page_index = 0
        self.text_scale = 1.0
        self.edit_mode = 'block'  
        self.view_format = "Original"  
        self.page_images = {}  
        self.selected_font = "Helvetica"

        self.image_bbox_mode = ImageBBoxMode()

        self.show_text_bboxes = True

        self.add_text_mode = False

        self.data_manager = DataManager(self.json_path, self.pdf_path)
        self.data = self.data_manager.data
        self.metadata = self.data_manager.metadata
        self.doc = self.data_manager.doc

        self.image_utils = ImageUtils()
        self.event_handlers = EventHandlers(self)
        self.metadata_manager = MetadataManager(self)

        self.image_counter = self.data_manager.image_counter
        self.chapter_counter = self.data_manager.chapter_counter

        left_panel_width = 200
        right_panel_width = 300
        middle_panel_width = self.winfo_screenwidth() - left_panel_width - right_panel_width

        if platform.system() == 'Darwin':  
            right_click_event = "<Button-2>"
        else:  
            right_click_event = "<Button-3>"

        self.controls_frame = tk.Frame(self, width=left_panel_width, bg="grey")
        self.controls_frame.pack(side=tk.LEFT, fill=tk.Y)
        self.controls_frame.pack_propagate(False)

        self.toc_frame = tk.Frame(self, width=right_panel_width, bg="lightgrey")
        self.toc_frame.pack(side=tk.RIGHT, fill=tk.Y)
        self.toc_frame.pack_propagate(False)

        self.view_frame = tk.Frame(self, width=middle_panel_width, bg="white")
        self.view_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.view_frame.pack_propagate(True)
        
        self.left_frame = tk.Frame(self.view_frame, bg="white")
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.right_frame = tk.Frame(self.view_frame, bg="white")
        self.right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.left_canvas = tk.Canvas(self.left_frame, bg="white")
        self.left_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.right_canvas = tk.Canvas(self.right_frame, bg="white")
        self.right_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.mode_label = tk.Label(self.controls_frame, text=f"Mode: {self.edit_mode.capitalize()}", bg="grey", fg="white")
        self.mode_label.pack(pady=10)

        self.back_button = tk.Button(self.controls_frame, text="Previous Page", command=self.previous_page)
        self.back_button.pack(pady=10, padx=20, fill=tk.X)

        self.next_button = tk.Button(self.controls_frame, text="Next Page", command=self.next_page)
        self.next_button.pack(pady=10, padx=20, fill=tk.X)

        self.ignore_page_button = tk.Button(self.controls_frame, text="Ignore This Page", command=self.toggle_ignore_page)
        self.ignore_page_button.pack(pady=10, padx=20, fill=tk.X)

        self.toggle_button = tk.Button(self.controls_frame, text="Toggle Edit Mode", command=self.toggle_edit_mode)
        self.toggle_button.pack(pady=10, padx=20, fill=tk.X)

        self.add_text_button = tk.Button(
            self.controls_frame,
            text="Add New Text",
            command=self.toggle_add_text_mode
        )
        self.add_text_button.pack(pady=10, padx=20, fill=tk.X)

        self.scale_label = tk.Label(self.controls_frame, text="Text Scale:", bg="grey", fg="white")
        self.scale_label.pack(pady=10)

        self.scale_slider = tk.Scale(self.controls_frame, from_=0.5, to=2.0, orient=tk.HORIZONTAL, resolution=0.1, command=self.update_scale)
        self.scale_slider.set(1.0)
        self.scale_slider.pack(pady=10, padx=20, fill=tk.X)

        self.image_mode_button = tk.Button(self.controls_frame, text="Image Mode: OFF", command=self.toggle_image_mode)
        self.image_mode_button.pack(pady=10, padx=20, fill=tk.X)
     
        self.export_as_button = tk.Button(self.controls_frame, text="Export as", command=self.open_export_dialog)
        self.export_as_button.pack(pady=10, padx=20, fill=tk.X)
               
        self.toggle_bboxes_button = tk.Button(
            self.controls_frame,
            text="Hide Text BBoxes",
            command=self.toggle_bbox_visibility
        )
        self.toggle_bboxes_button.pack(pady=10, padx=20, fill=tk.X)
        
        self.page_counter_label = tk.Label(self.controls_frame, text="", bg="grey", fg="white", font=("Helvetica", 12))
        self.page_counter_label.pack(pady=10)
               
        self.toc_label = tk.Label(self.toc_frame, text="Table of Contents", bg="lightgrey", fg="black")
        self.toc_label.pack(pady=10)

        self.toc_listbox = tk.Listbox(self.toc_frame, width=30)
        self.toc_listbox.pack(pady=5, padx=20, fill=tk.BOTH, expand=True)
     
        self.toc_context_menu = tk.Menu(self.toc_listbox, tearoff=0)
        self.toc_context_menu.add_command(label="Delete", command=self.delete_toc_entry)
        self.toc_context_menu.add_command(label="Rename", command=self.rename_toc_entry)  

        self.toc_listbox.bind(right_click_event, self.show_toc_context_menu)
         
        self.images_label = tk.Label(self.toc_frame, text="Images", bg="lightgrey", fg="black")
        self.images_label.pack(pady=10)
 
        self.images_listbox = tk.Listbox(self.toc_frame, width=30)
        self.images_listbox.pack(pady=5, padx=20, fill=tk.BOTH, expand=True)
    
        self.images_context_menu = tk.Menu(self.images_listbox, tearoff=0)
        self.images_context_menu.add_command(label="Delete", command=self.delete_image_entry)
        self.images_context_menu.add_command(label="Rename", command=self.rename_image_entry)
  
        self.images_listbox.bind(right_click_event, self.show_images_context_menu)
        
        self.images_listbox.bind("<Double-Button-1>", self.on_image_click)

        self.metadata_label = tk.Label(self.toc_frame, text="Metadata", bg="lightgrey", fg="black")
        self.metadata_label.pack(pady=10)

        self.metadata_text = tk.Text(self.toc_frame, height=10, wrap=tk.WORD)
        self.metadata_text.pack(pady=5, padx=20, fill=tk.X)

        self.metadata_button = tk.Button(self.toc_frame, text="Edit Metadata", command=self.metadata_manager.edit_metadata)
        self.metadata_button.pack(pady=5, padx=20, fill=tk.X)

        self.fetch_metadata_button = tk.Button(self.toc_frame, text="Fetch Metadata by ISBN", command=self.metadata_manager.fetch_metadata_by_isbn)
        self.fetch_metadata_button.pack(pady=5, padx=20, fill=tk.X)

        self.left_canvas.bind("<Button-1>", lambda event: handle_click(self, event))  
        self.left_canvas.bind("<B1-Motion>", self.event_handlers.on_drag)
        self.left_canvas.bind("<ButtonRelease-1>", self.event_handlers.on_release)

        self.toc_listbox.bind("<Double-Button-1>", self.on_toc_click)
        self.bind("<Configure>", self.on_resize)

        self.selected_toc_index = None
        self.selected_image_index = None

        self.toc_data_list = []  
          
        self.populate_toc()
        self.populate_images_list()
        self.metadata_manager.display_metadata()
        self.display_page()

    def display_page(self):
        print(f"Displaying page {self.page_index + 1}")  
        self.left_canvas.delete("all")
        self.right_canvas.delete("all")

        page_data = self.data['pages'][self.page_index]
        page_num = page_data['page'] - 1  

        
        if page_num not in self.page_images:
            page = self.doc.load_page(page_num)
            pix = page.get_pixmap()
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            self.page_images[page_num] = img
            print(f"Loaded image for page {page_num + 1}")  
        else:
            img = self.page_images[page_num]
            print(f"Using cached image for page {page_num + 1}")  

        
        self.image_utils.display_image(self.right_canvas, img)
        self.right_canvas_ratio = self.image_utils.get_display_ratio(img, self.right_canvas)

        
        if self.show_text_bboxes:
            bboxes_to_draw = page_data['detections']
        else:
            bboxes_to_draw = [det for det in page_data['detections'] if det['class'] == 'Picture']

        temp_page_data = page_data.copy()
        temp_page_data['detections'] = bboxes_to_draw

        self.image_utils.draw_bounding_boxes(temp_page_data, self.right_canvas, self.right_canvas_ratio)
  
        self.left_canvas.update_idletasks()

        if page_data.get('ignore', False):
            self.ignore_page_button.config(text="Unignore This Page")      
            self.left_canvas.create_text(
                self.left_canvas.winfo_width() / 2,
                self.left_canvas.winfo_height() / 2,
                text="Page Ignored",
                font=("Helvetica", 24, "bold"),
                fill="red"
            )
            
            print(f"Page {self.page_index + 1} is ignored. Displaying 'Page Ignored' message.")
            
        else:
            self.ignore_page_button.config(text="Ignore This Page")
            
            
            if self.view_format == "Original":
                self.image_utils.display_blank_image(self.left_canvas, img.size)
            elif self.view_format == "A4":
                self.image_utils.display_blank_image(self.left_canvas, (595, 842))
            elif self.view_format == "Letter":
                self.image_utils.display_blank_image(self.left_canvas, (612, 792))

            
            font_size = int(12 * self.text_scale)
            font_weight = "normal"
            font = (self.selected_font, font_size, font_weight)

            tk_font = tkFont.Font(family=self.selected_font, size=font_size, weight=font_weight)

            y_offset = 10  

            left_margin = (self.left_canvas.winfo_width() - self.left_canvas.winfo_width() * 0.9) / 2  
            max_width = self.left_canvas.winfo_width() * 0.9  

            detections = page_data.get('detections', [])
            for idx, detection in enumerate(detections):
                detection['id'] = detection.get('id', idx)

            sorted_detections = sorted(
                [d for d in detections if d['class'] in ['Text', 'Section-header']],
                key=lambda d: (d['bbox'][1], d['bbox'][0])  
            )

            for detection in sorted_detections:
                text = detection['text']
                detection_id = detection['id']

                if detection.get('class') == 'Section-header':
                    
                    chapter_font_size = int(font_size * 1.5)
                    chapter_font = (self.selected_font, chapter_font_size, "bold")
                    tk_chapter_font = tkFont.Font(family=self.selected_font, size=chapter_font_size, weight="bold")

                    lines = self.wrap_text(text, tk_chapter_font, max_width)
                    for line in lines:
                        text_id = self.left_canvas.create_text(
                            self.left_canvas.winfo_width() / 2,
                            y_offset,
                            text=line,
                            font=chapter_font,
                            fill="black",
                            anchor="n",
                            justify="center",
                            width=max_width,
                            tags=(str(detection_id),)
                        )
                        bbox = self.left_canvas.bbox(text_id)
                        text_height = bbox[3] - bbox[1]
                        y_offset += text_height

                    y_offset += 10  
                else:
                    
                    tk_font = tkFont.Font(family=self.selected_font, size=font_size, weight=font_weight)

                    if self.edit_mode == 'block':
                        
                        lines = self.wrap_text(text, tk_font, max_width)
                        for line in lines:
                            text_id = self.left_canvas.create_text(
                                left_margin,
                                y_offset,
                                text=line,
                                font=font,
                                fill="black",
                                anchor="nw",
                                width=max_width,
                                tags=(str(detection_id),)
                            )
                            bbox = self.left_canvas.bbox(text_id)
                            text_height = bbox[3] - bbox[1]
                            y_offset += text_height
                        y_offset += 5  
                    elif self.edit_mode == 'word':
                        words = text.split()
                        x_offset = left_margin
                        line_height = None
                        for idx_w, word in enumerate(words):
                            tag = f"{detection_id}-w-{idx_w}"
                            
                            if 'chapter_words' in detection and str(idx_w) in detection['chapter_words']:
                                word_font = (self.selected_font, font_size, "bold")
                            else:
                                word_font = font
                            text_id = self.left_canvas.create_text(
                                x_offset,
                                y_offset,
                                text=word,
                                font=word_font,
                                fill="black",
                                anchor="nw",
                                tags=(tag,)
                            )
                            bbox = self.left_canvas.bbox(text_id)
                            word_width = bbox[2] - bbox[0]
                            word_height = bbox[3] - bbox[1]
                            if line_height is None:
                                line_height = word_height
                            if x_offset + word_width > left_margin + max_width:
                                
                                x_offset = left_margin
                                y_offset += line_height + 5
                                line_height = word_height
                            self.left_canvas.coords(text_id, x_offset, y_offset)
                            x_offset += word_width + 5  
                        y_offset += line_height + 5  

        
        total_pages = len(self.data['pages'])
        current_page_display = self.page_index + 1  
        self.page_counter_label.config(text=f"Page {current_page_display} of {total_pages}")
        
        self.left_canvas.update_idletasks()
        self.right_canvas.update_idletasks()

    def wrap_text(self, text, tk_font, max_width):
        words = text.split()
        lines = []
        line = ''
        for word in words:
            if tk_font.measure(line + (' ' if line else '') + word) <= max_width:
                line += (' ' if line else '') + word
            else:
                lines.append(line)
                line = word
        if line:
            lines.append(line)
        return lines

    
    def next_page(self):
        if self.page_index < len(self.data['pages']) - 1:
            self.page_index += 1
            self.display_page()

    def previous_page(self):
        if self.page_index > 0:
            self.page_index -= 1
            self.display_page()
    
    def toggle_ignore_page(self):
        page_data = self.data['pages'][self.page_index]
        page_data['ignore'] = not page_data.get('ignore', False)
        if page_data['ignore']:
            self.ignore_page_button.config(text="Unignore This Page")
        else:
            self.ignore_page_button.config(text="Ignore This Page")
        self.display_page()
        self.data_manager.save_data()

    def toggle_edit_mode(self):
        if self.edit_mode == 'block':
            self.edit_mode = 'word'
        else:
            self.edit_mode = 'block'
        self.mode_label.config(text=f"Mode: {self.edit_mode.capitalize()}")
        self.display_page()

    def update_scale(self, val):
        self.text_scale = float(val)
        self.display_page()

    def update_view_format(self, selected_format):
        self.view_format = selected_format
        self.display_page()

    def toggle_bbox_visibility(self):
        self.show_text_bboxes = not self.show_text_bboxes
        if self.show_text_bboxes:
            self.toggle_bboxes_button.config(text="Hide Text BBoxes")
        else:
            self.toggle_bboxes_button.config(text="Show Text BBoxes")
        self.display_page()
    
    def toggle_image_mode(self):
        
        self.image_bbox_mode.toggle()
        if self.image_bbox_mode.is_enabled():
            self.image_mode_button.config(text="Image Mode: ON")
            self.right_canvas.bind("<Button-1>", self.start_image_bbox)
            self.right_canvas.bind("<B1-Motion>", self.move_image_bbox)
            self.right_canvas.bind("<ButtonRelease-1>", self.release_image_bbox)
        else:
            self.image_mode_button.config(text="Image Mode: OFF")
            self.right_canvas.unbind("<Button-1>")
            self.right_canvas.unbind("<B1-Motion>")
            self.right_canvas.unbind("<ButtonRelease-1>")

    def start_image_bbox(self, event):
        self.image_bbox_mode.start_bbox(event, self.right_canvas, self.right_canvas_ratio)

    def move_image_bbox(self, event):
        self.image_bbox_mode.move_bbox(event, self.right_canvas, self.right_canvas_ratio)

    def release_image_bbox(self, event):
        result = self.image_bbox_mode.release_bbox(event, self.right_canvas, self.right_canvas_ratio)
        if result:
            bbox, rect_id = result
            print(f"New bbox: {bbox}, rect_id: {rect_id}")  
            page_data = self.data['pages'][self.page_index]
            image_name = f"image_{self.image_counter}"
            self.image_counter += 1
            image_data = {
                'bbox': bbox,
                'class': 'Picture',
                'name': image_name,
                'canvas_id': rect_id,  
                'id': max([d.get('id', 0) for d in page_data.get('detections', [])], default=0) + 1
            }
            page_data['detections'].append(image_data)
            
            if platform.system() == 'Darwin':
                right_click_event = "<Button-2>"
            else: 
                right_click_event = "<Button-3>"

            self.right_canvas.tag_bind(rect_id, right_click_event, lambda event, img_data=image_data: self.delete_image_bbox(event, img_data))
            self.populate_images_list()
            self.data_manager.save_data()
            
            self.display_page()
            print("Page displayed after adding bbox")  

    def delete_image_bbox(self, event, img_data):
        page_data = self.data['pages'][self.page_index]
        page_data['detections'] = [det for det in page_data.get('detections', []) if det != img_data]
        self.right_canvas.delete(img_data.get('canvas_id'))
        self.populate_images_list()
        self.data_manager.save_data()
        self.display_page()
        print(f"Deleted bbox: {img_data['name']}")  

    def toggle_add_text_mode(self):
        """Toggles the add text mode on or off."""
        self.add_text_mode = not self.add_text_mode
        if self.add_text_mode:
            self.add_text_button.config(relief=tk.SUNKEN, bg="lightblue")
            self.left_canvas.config(cursor="crosshair")
            
            self.disable_controls()
        else:
            self.add_text_button.config(relief=tk.RAISED, bg="SystemButtonFace")
            self.left_canvas.config(cursor="")
            self.enable_controls()

    def disable_controls(self):
        self.back_button.config(state=tk.DISABLED)
        self.next_button.config(state=tk.DISABLED)
        self.ignore_page_button.config(state=tk.DISABLED)
        self.toggle_button.config(state=tk.DISABLED)
        self.scale_slider.config(state=tk.DISABLED)
        self.view_format_menu.config(state=tk.DISABLED)
        self.image_mode_button.config(state=tk.DISABLED)
        self.export_as_button.config(state=tk.DISABLED)
        self.toggle_bboxes_button.config(state=tk.DISABLED)
        
    def enable_controls(self):
        self.back_button.config(state=tk.NORMAL)
        self.next_button.config(state=tk.NORMAL)
        self.ignore_page_button.config(state=tk.NORMAL)
        self.toggle_button.config(state=tk.NORMAL)
        self.scale_slider.config(state=tk.NORMAL)
        self.view_format_menu.config(state=tk.NORMAL)
        self.image_mode_button.config(state=tk.NORMAL)
        self.export_as_button.config(state=tk.NORMAL)
        self.toggle_bboxes_button.config(state=tk.NORMAL)
        
    def export_as(self, format_type, window):
        window.destroy()  

        if format_type == "epub":
            exporter = EPUBExporter(self.data, self.metadata, self.pdf_path)
            exporter.export_to_epub(self)
        elif format_type == "pdf":
            exporter = PDFExporter(self.data, self.metadata, self.pdf_path)
            exporter.export_to_pdf(self)
        elif format_type == "txt":
            exporter = TextExporter(self.data, self.metadata, self.pdf_path)
            exporter.export_to_txt(self)
        else:
            messagebox.showerror("Error", f"Unknown export format: {format_type}")
    
    def open_export_dialog(self):
        export_window = tk.Toplevel(self)
        export_window.title("Export As")
        export_window.geometry("300x150")
        export_window.grab_set()  

        label = tk.Label(export_window, text="Select Export Format:", font=("Helvetica", 12))
        label.pack(pady=10)

        epub_button = tk.Button(export_window, text="EPUB", width=20, command=lambda: self.export_as("epub", export_window))
        epub_button.pack(pady=5)

        pdf_button = tk.Button(export_window, text="PDF", width=20, command=lambda: self.export_as("pdf", export_window))
        pdf_button.pack(pady=5)

        txt_button = tk.Button(export_window, text="Plain Text", width=20, command=lambda: self.export_as("txt", export_window))
        txt_button.pack(pady=5)
    
    
    def populate_toc(self):
        self.toc_listbox.delete(0, tk.END)
        self.chapter_counter = 0  
        self.toc_data_list = []  
        for page_data in self.data['pages']:
            for detection in page_data.get('detections', []):
                if detection.get('class') == 'Section-header':
                    chapter_name = detection.get('name', detection['text'])
                    page_num = page_data['page']
                    text_snippet = detection['text'][:100]  
                    self.chapter_counter += 1
                    self.toc_listbox.insert(tk.END, f"(Page {page_num}): {chapter_name}")
                    self.toc_data_list.append((page_data, detection))  
                if 'chapter_words' in detection:
                    for idx_w_str, chapter_name in detection['chapter_words'].items():
                        idx_w = int(idx_w_str)  
                        words = detection['text'].split()
                        if idx_w < len(words):
                            word = words[idx_w]
                            page_num = page_data['page']
                            text_snippet = word[:30]
                            self.chapter_counter += 1
                            self.toc_listbox.insert(tk.END, f"{chapter_name} (Page {page_num}): {text_snippet}")
                            
                            
    def show_toc_context_menu(self, event):
        try:
            
            self.toc_listbox.selection_clear(0, tk.END)
            clicked_index = self.toc_listbox.nearest(event.y)
            self.toc_listbox.selection_set(clicked_index)
            self.toc_listbox.activate(clicked_index)
            self.selected_toc_index = clicked_index

            
            self.toc_context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            
            self.toc_context_menu.grab_release()

    def delete_toc_entry(self):
        index = self.selected_toc_index
        if index is not None and index < len(self.toc_data_list):
            
            page_data, detection = self.toc_data_list[index]

            detection['class'] = 'Text'  
            if 'name' in detection:
                del detection['name']
 
            self.populate_toc()

            self.data_manager.save_data()

            self.display_page()
            self.selected_toc_index = None

    def rename_toc_entry(self):
        index = self.selected_toc_index
        if index is not None and index < len(self.toc_data_list):
            
            page_data, detection = self.toc_data_list[index]
            current_name = detection.get('name', detection.get('text'))
            
            new_name = simpledialog.askstring("Rename Chapter", "Enter new chapter name:", initialvalue=current_name, parent=self)
            if new_name:
                
                detection['name'] = new_name

                self.populate_toc()

                self.data_manager.save_data()

                self.display_page()

                self.selected_toc_index = None
    

    def on_toc_click(self, event):
        selection = event.widget.curselection()
        if selection:
            index = selection[0]
            item_text = event.widget.get(index)
            try:
                if item_text.startswith("(Page "):
                    page_num = int(item_text.split('Page ')[1].split(')')[0]) - 1
                else:
                    page_num = int(item_text.split('Page ')[1].split(')')[0]) - 1
                if 0 <= page_num < len(self.data['pages']):
                    self.page_index = page_num
                    self.display_page()
                else:
                    print(f"Invalid page number extracted: {page_num + 1}")  
            except (IndexError, ValueError) as e:
                print(f"Error parsing ToC item: {item_text} - {e}")  

    
    def populate_images_list(self):
        self.images_listbox.delete(0, tk.END)
        self.images_data_list = []  
        for page_data in self.data['pages']:
            page_num = page_data['page']
            for detection in page_data.get('detections', []):
                if detection['class'] == 'Picture':
                    image_name = detection.get('name', f"image_{self.data_manager.image_counter}")
                    if image_name is None:
                        image_name = f"image_{self.data_manager.image_counter}"
                        detection['name'] = image_name
                        self.data_manager.image_counter += 1
                    self.images_listbox.insert(tk.END, f"Page {page_num}: {image_name}")
                    self.images_data_list.append((page_data, detection))

    def show_images_context_menu(self, event):
        try:
            
            self.images_listbox.selection_clear(0, tk.END)
            clicked_index = self.images_listbox.nearest(event.y)
            self.images_listbox.selection_set(clicked_index)
            self.images_listbox.activate(clicked_index)
            self.selected_image_index = clicked_index
            self.images_context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            
            self.images_context_menu.grab_release()

    def delete_image_entry(self):
        index = self.selected_image_index
        if index is not None:
            
            page_data, img_data = self.images_data_list[index]

            page_data['detections'].remove(img_data)

            self.populate_images_list()

            self.data_manager.save_data()

            if self.page_index == self.data['pages'].index(page_data):
                self.display_page()

            self.selected_image_index = None

    def rename_image_entry(self):
        index = self.selected_image_index
        if index is not None:
            
            page_data, img_data = self.images_data_list[index]

            new_name = simpledialog.askstring("Rename Image", "Enter new image name:", initialvalue=img_data['name'], parent=self)
            if new_name:
                
                img_data['name'] = new_name

                self.populate_images_list()

                self.data_manager.save_data()

                if self.page_index == self.data['pages'].index(page_data):
                    self.display_page()

                self.selected_image_index = None

    def on_image_click(self, event):
        selection = event.widget.curselection()
        if selection:
            index = selection[0]
            page_data, img_data = self.images_data_list[index]
            page_num = page_data['page'] - 1  
            if 0 <= page_num < len(self.data['pages']):
                self.page_index = page_num
                self.display_page()
            else:
                print(f"Invalid page number for image: {page_num + 1}")  

    
    def on_resize(self, event):
        self.display_page()

    
    def export_to_epub(self):
        exporter = EPUBExporter(self.data, self.metadata, self.pdf_path)
        exporter.open_export_window(self)
     
    def toggle_chapter_start(self, detection):
        if detection.get('class') != 'Section-header':
            detection['class'] = 'Section-header'
            
            chapter_name = detection['text']
            detection['name'] = chapter_name
            self.chapter_counter += 1
        else:
            detection['class'] = 'Text'
            if 'name' in detection:
                del detection['name']
        self.populate_toc()
        self.data_manager.save_data()

def main(json_path, pdf_path):
    app = PDFViewer(json_path, pdf_path)
    app.mainloop()

if __name__ == '__main__':
    json_path = 'output_data.json'  
    pdf_path = 'your_pdf_file.pdf'  
    main(json_path, pdf_path)

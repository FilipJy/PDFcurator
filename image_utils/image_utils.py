from PIL import Image, ImageTk

class ImageUtils:
    def display_image(self, canvas, img):
        canvas_width = max(canvas.winfo_width(), 1)
        canvas_height = max(canvas.winfo_height(), 1)
        img_width, img_height = img.size
        ratio = min(canvas_width / img_width, canvas_height / img_height)
        new_size = (max(int(img_width * ratio), 1), max(int(img_height * ratio), 1))
        resized_img = img.resize(new_size, Image.LANCZOS)
        tk_img = ImageTk.PhotoImage(resized_img)
        canvas.create_image(0, 0, anchor="nw", image=tk_img)
        canvas.image = tk_img  

    def get_display_ratio(self, img, canvas):
        canvas_width = max(canvas.winfo_width(), 1)
        canvas_height = max(canvas.winfo_height(), 1)
        img_width, img_height = img.size
        ratio = min(canvas_width / img_width, canvas_height / img_height)
        return ratio

    def draw_bounding_boxes(self, page_data, canvas, ratio):
        
        for detection in page_data.get('detections', []):
            bbox = detection['bbox']
            class_name = detection['class']
            name = detection.get('name', '')
            
            xmin, ymin, xmax, ymax = [coord * ratio for coord in bbox]
            
            if class_name == 'Text':
                color = 'blue'
            elif class_name == 'Picture':
                color = 'green'
            elif class_name == 'Section-header':
                color = 'purple'
            else:
                color = 'red'
            
            rect_id = canvas.create_rectangle(xmin, ymin, xmax, ymax, outline=color, width=2)
            
            if class_name == 'Picture' and name:
                canvas.create_text(xmin, ymin - 10, text=name, anchor='nw', fill=color, font=("Helvetica", 10, "bold"))
            
    def display_blank_image(self, canvas, size):
        canvas_width = max(canvas.winfo_width(), 1)
        canvas_height = max(canvas.winfo_height(), 1)
        img_width, img_height = size
        ratio = min(canvas_width / img_width, canvas_height / img_height)
        new_size = (max(int(img_width * ratio), 1), max(int(img_height * ratio), 1))
        blank_img = Image.new('RGB', new_size, color=(255, 255, 255))
        tk_blank_img = ImageTk.PhotoImage(blank_img)
        canvas.create_image(0, 0, anchor="nw", image=tk_blank_img)
        canvas.image = tk_blank_img

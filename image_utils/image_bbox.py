import tkinter as tk

class ImageBBoxMode:
    def __init__(self):
        self.enabled = False
        self.start_x = None
        self.start_y = None
        self.rect = None

    def toggle(self):
        self.enabled = not self.enabled

    def is_enabled(self):
        return self.enabled

    def start_bbox(self, event, canvas, ratio):
        if not self.enabled:
            return
        canvas_x = canvas.canvasx(event.x)
        canvas_y = canvas.canvasy(event.y)
        
        self.start_x = canvas_x / ratio
        self.start_y = canvas_y / ratio
        
        self.rect = canvas.create_rectangle(
            canvas_x, canvas_y, canvas_x, canvas_y, outline='blue', width=2
        )

    def move_bbox(self, event, canvas, ratio):
        if not self.enabled or self.rect is None:
            return
        canvas_curr_x = canvas.canvasx(event.x)
        canvas_curr_y = canvas.canvasy(event.y)
        
        canvas.coords(self.rect, self.start_x * ratio, self.start_y * ratio, canvas_curr_x, canvas_curr_y)

    def release_bbox(self, event, canvas, ratio):
        if not self.enabled or self.rect is None:
            return None
        canvas_curr_x = canvas.canvasx(event.x)
        canvas_curr_y = canvas.canvasy(event.y)
        
        end_x = canvas_curr_x / ratio
        end_y = canvas_curr_y / ratio
        bbox = [self.start_x, self.start_y, end_x, end_y]
        
        rect_id = self.rect
        
        self.start_x = None
        self.start_y = None
        self.rect = None
        return bbox, rect_id  
        self.display_page()

    def draw_existing_bboxes(self, canvas, page_data, ratio, delete_callback):
        if 'images' in page_data:
            for img_data in page_data['images']:
                bbox = img_data['bbox']
                rect = canvas.create_rectangle(
                    bbox[0] * ratio,
                    bbox[1] * ratio,
                    bbox[2] * ratio,
                    bbox[3] * ratio,
                    outline='blue',
                    width=2,
                    tags=(f"image_bbox_{img_data['name']}",)
                )
                img_data['canvas_id'] = rect
                
                canvas.tag_bind(rect, '<Button-3>', lambda event, img_data=img_data: delete_callback(event, img_data))

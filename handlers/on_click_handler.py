import tkinter as tk
from tkinter import simpledialog, messagebox

def handle_click(viewer, event):
    
    if viewer.add_text_mode:
        add_new_text(viewer, event)
    else:
        edit_existing_text(viewer, event)

def add_new_text(viewer, event):
    x, y = event.x, event.y
    
    text = simpledialog.askstring("Add New Text", "Enter the text to add:", parent=viewer)
    if text:
        
        bbox_width, bbox_height = 200, 50   
        
        canvas_width = viewer.left_canvas.winfo_width()
        canvas_height = viewer.left_canvas.winfo_height()

        x1 = x
        y1 = y
        x2 = min(x + bbox_width, canvas_width)
        y2 = min(y + bbox_height, canvas_height)
        bbox = [x1, y1, x2, y2]

        page_data = viewer.data['pages'][viewer.page_index]
        detection_id = max([d.get('id', 0) for d in page_data.get('detections', [])], default=0) + 1
        new_detection = {
            'id': detection_id,
            'class': 'Text',
            'text': text,
            'bbox': bbox
        }
        page_data['detections'].append(new_detection)
        
        try:
            viewer.data_manager.save_data()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save data: {e}")
            return
        
        viewer.display_page()

    viewer.toggle_add_text_mode()

def edit_existing_text(viewer, event):
    x, y = event.x, event.y
    item_ids = viewer.left_canvas.find_overlapping(x, y, x, y)
    for item_id in item_ids:
        item_tags = viewer.left_canvas.gettags(item_id)
        if not item_tags:
            continue
        item_tag = item_tags[0]
        
        tag_parts = item_tag.split('-')
        if len(tag_parts) == 3 and viewer.edit_mode == 'word':
            detection_id = int(tag_parts[0])
            mode = tag_parts[1]
            index = int(tag_parts[2])
        else:
            detection_id = int(item_tag)
            mode = None
            index = None
        page_data = viewer.data['pages'][viewer.page_index]
        detections = page_data.get('detections', [])
        
        detection = next((d for d in detections if d.get('id') == detection_id), None)
        if detection is None:
            continue
        
        dialog = tk.Toplevel(viewer)
        dialog.title("Edit Text")
        dialog.grab_set()  
        if mode == 'w' and viewer.edit_mode == 'word':
            
            words = detection['text'].split()
            original_text = words[index]
            tk.Label(dialog, text="Edit word:").pack(pady=10)
            text_var = tk.StringVar(value=original_text)
            entry = tk.Entry(dialog, textvariable=text_var, width=50)
            entry.pack(pady=10)
        else:
            
            original_text = detection['text']
            tk.Label(dialog, text="Edit text:").pack(pady=10)
            text_widget = tk.Text(dialog, width=80, height=20)
            text_widget.pack(pady=10)
            text_widget.insert(tk.END, original_text)
        def save_text():
            if mode == 'w' and viewer.edit_mode == 'word':
                new_text = text_var.get()
                if new_text:
                    words[index] = new_text
                    detection['text'] = ' '.join(words)
            else:
                new_text = text_widget.get("1.0", tk.END).strip()
                if new_text:
                    detection['text'] = new_text
            
            try:
                viewer.data_manager.save_data()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save data: {e}")
            viewer.display_page()
            dialog.destroy()
        def delete_text():
            if mode == 'w' and viewer.edit_mode == 'word':
                del words[index]
                detection['text'] = ' '.join(words)
            else:
                detections.remove(detection)
            
            try:
                viewer.data_manager.save_data()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save data: {e}")
            viewer.display_page()
            dialog.destroy()
        def toggle_chapter():
            str_index = str(index)  
            if detection.get('class') == 'Section-header':
                
                detection['class'] = 'Text'
                if 'name' in detection:
                    del detection['name']
            elif 'chapter_words' in detection and str_index in detection['chapter_words']:
                
                del detection['chapter_words'][str_index]
                if not detection['chapter_words']:
                    del detection['chapter_words']
            else:
                
                if mode == 'w' and viewer.edit_mode == 'word':
                    
                    chapter_name = simpledialog.askstring("Chapter Name", "Enter chapter name:", parent=dialog)
                    if chapter_name:
                        
                        if 'chapter_words' not in detection:
                            detection['chapter_words'] = {}
                        detection['chapter_words'][str_index] = chapter_name
                else:
                    
                    detection['class'] = 'Section-header'
                    detection['name'] = detection['text']
            
            viewer.populate_toc()
            viewer.display_page()
            try:
                viewer.data_manager.save_data()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save data: {e}")
            dialog.destroy()

        if detection.get('class') == 'Section-header' or ('chapter_words' in detection and (mode == 'w' and str(index) in detection['chapter_words'])):
            chapter_button_text = "Unmark Chapter Start"
        else:
            chapter_button_text = "Mark as Chapter Start"
        chapter_button = tk.Button(dialog, text=chapter_button_text, command=toggle_chapter)
        chapter_button.pack(side=tk.LEFT, padx=10, pady=10)
        save_button = tk.Button(dialog, text="Save", command=save_text)
        save_button.pack(side=tk.LEFT, padx=10, pady=10)
        delete_button = tk.Button(dialog, text="Delete", command=delete_text)
        delete_button.pack(side=tk.LEFT, padx=10, pady=10)
        
        break

import json
import fitz  
from PIL import Image
import logging
import os
import cv2
import numpy as np
from paddleocr import PaddleOCR

from data.core.parsing_utils.layout_detection import detect_layout, get_class_name, caption_image  

def extract_text_from_pdf(pdf_path, output_json, progress_queue=None, language='en', use_captioning=False):
    try:
        logging.debug(f"Starting OCR on {pdf_path}")
        doc = fitz.open(pdf_path)
        data = []
        num_pages = len(doc)
        total_tasks = num_pages  

        ocr_model = PaddleOCR(use_angle_cls=True, lang=language)

        for page_num in range(num_pages):
            page = doc.load_page(page_num)
            pix = page.get_pixmap()
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

            image = np.array(img)
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

            detections = detect_layout(image)

            if detections is None or len(detections) == 0:
                logging.warning(f"No detections for page {page_num + 1}")
                detections = sv.Detections.empty()

            page_data = {
                'page': page_num + 1,
                'detections': []
            }

            for i in range(len(detections)):
                class_id = detections.class_id[i]
                class_name = get_class_name(class_id)
                bbox = detections.xyxy[i]  
                xmin, ymin, xmax, ymax = map(int, bbox)

                xmin = max(0, xmin - 3)
                ymin = max(0, ymin - 3)
                xmax = min(image.shape[1], xmax + 3)
                ymax = min(image.shape[0], ymax + 3)

                cropped_image = image[ymin:ymax, xmin:xmax]

                if class_name.lower() in ['text', 'section-header']:
                    try:
                        result = ocr_model.ocr(cropped_image, cls=True)
                        if result and isinstance(result[0], list):
                            ocr_text_lines = []
                            for line in result[0]:
                                if len(line) > 1 and isinstance(line[1], tuple) and len(line[1]) > 0:
                                    text = line[1][0]  
                                    ocr_text_lines.append(text)
                                else:
                                    logging.warning(f"Unexpected OCR result format: {line}")
                            ocr_text = '\n'.join(ocr_text_lines)
                        else:
                            ocr_text = ""
                    except Exception as e:
                        logging.error(f"Error in PaddleOCR: {e}")
                        ocr_text = ""
                elif class_name.lower() in ['image', 'picture']:
                    if use_captioning:
                        cropped_image_pil = Image.fromarray(cv2.cvtColor(cropped_image, cv2.COLOR_BGR2RGB))
                        ocr_text = caption_image(cropped_image_pil)
                    else:
                        ocr_text = ""
                else:
                    ocr_text = ""
                detection_data = {
                    'class': class_name,
                    'bbox': [xmin, ymin, xmax, ymax],
                    'text': ocr_text
                }
                page_data['detections'].append(detection_data)

            data.append(page_data)
            if progress_queue:
                progress_queue.put((page_num + 1) / total_tasks)

        doc.close()

        
        json_output = {
            "metadata": {},
            "pages": data
        }
        with open(output_json, 'w', encoding='utf-8') as json_file:
            json.dump(json_output, json_file, indent=4, ensure_ascii=False)
        logging.debug(f"JSON saved successfully to {output_json}")

    except Exception as e:
        logging.error(f"Error in extract_text_from_pdf: {e}")
        raise  

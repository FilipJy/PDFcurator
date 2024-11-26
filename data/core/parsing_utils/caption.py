from transformers import AutoModelForCausalLM, AutoTokenizer
from PIL import Image
import logging

class CaptioningModel:
    def __init__(self):
        model_id = "vikhyatk/moondream2"
        revision = "2024-08-26"
        try:
            self.model = AutoModelForCausalLM.from_pretrained(
                model_id, trust_remote_code=True, revision=revision
            )
            self.tokenizer = AutoTokenizer.from_pretrained(model_id, revision=revision)
            logging.debug("Image captioning model initialized successfully.")
        except Exception as e:
            logging.error(f"Failed to load captioning model: {e}")
            self.model = None
            self.tokenizer = None

    def caption(self, image):
        if self.model is None or self.tokenizer is None:
            logging.error("Captioning model is not initialized.")
            return ""
        try:
            
            enc_image = self.model.encode_image(image)
            caption = self.model.answer_question(enc_image, "Describe this image.", self.tokenizer)
            return caption
        except Exception as e:
            logging.error(f"Error during image captioning: {e}")
            return ""

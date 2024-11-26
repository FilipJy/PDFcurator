import os
import requests

def download_model():
    model_url = "https://github.com/moured/YOLOv11-Document-Layout-Analysis/releases/download/doclaynet_weights/yolov11x_best.pt"
    model_dir = os.getcwd()
    model_path = os.path.join(model_dir, "yolov11x_best.pt")

    os.makedirs(model_dir, exist_ok=True)

    if os.path.exists(model_path):
        print(f"Model already exists at: {model_path}")
        return model_path

    print(f"Downloading model from {model_url} to {model_path}...")
    response = requests.get(model_url, stream=True)
    if response.status_code == 200:
        with open(model_path, "wb") as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        print("Model downloaded successfully.")
    else:
        raise Exception(f"Failed to download model. HTTP status code: {response.status_code}")

    return model_path

if __name__ == "__main__":
    model_path = download_model()
    print(f"Model is ready at: {model_path}")

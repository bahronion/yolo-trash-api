from fastapi import FastAPI, File, UploadFile
import uvicorn
import torch
import cv2
import numpy as np
from ultralytics import YOLO
from io import BytesIO
from PIL import Image

# Initialize FastAPI app
app = FastAPI()

# Load YOLOv8 model
model = YOLO("C:/CapstoneProject/yolo-api/best.pt")  # use relative path for Render or GitHub repo

@app.post("/predict/")
async def predict(file: UploadFile = File(...)):
    try:
        # Read image file
        contents = await file.read()  # ✅ fixed: .re ➜ .read()
        image = Image.open(BytesIO(contents)).convert("RGB")

        # Convert to OpenCV format
        image = np.array(image)
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)  # ✅ fixed: "ige" ➜ "image"

        # Inference
        results = model(image)

        # Extract detections
        detections = []
        for box in results[0].boxes:
            detections.append({
                "class": results[0].names[int(box.cls)],
                "confidence": float(box.conf[0]),
                "bbox": box.xyxy[0].tolist()
            })

        return {"detections": detections}

    except Exception as e:
        return {"error": str(e)}

# Run locally for testing
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
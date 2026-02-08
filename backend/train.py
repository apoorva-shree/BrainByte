from ultralytics import YOLO
import os
from pathlib import Path

dataset_path = Path("C:/Users/jasmi/Downloads/archive.zip")


data_yaml = {
    'train': str("C:/Users/jasmi/Downloads/archive.zip")/"images/train",
    'val': str(dataset_path / "images/val"),
    'names': ['healthy', 'rotten']  
}


import yaml
with open("food_data.yaml", "w") as f:
    yaml.dump(data_yaml, f)
model = YOLO("yolov8n.pt")  


results = model.train(
    data="food_data.yaml",   
    epochs=50,               
    imgsz=416,               
    batch=16,                
    lr=0.001,                
    project="food_yolov8",  
    name="healthy_rotten",   
    device=0        
)



metrics = model.val(
    data="food_data.yaml",
    imgsz=416,
    batch=16,
)

print(metrics)


test_image = str("C:/Users/jasmi/Downloads/archive.zip"/ "images/val/sample_image.jpg")
preds = model.predict(test_image, conf=0.25, save=True)
print(preds)



model.export(format="onnx")
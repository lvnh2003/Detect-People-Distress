from ultralytics import YOLO

# Load a model
model = YOLO('yolov8n.pt')  # load a pretrained model (recommended for training)

# Train the model with 2 GPUs
results = model.train(data='/home/lvnh/PycharmProjects/Detect-People-Distress/datasets/data.yaml', epochs=25, imgsz=640)
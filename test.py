from ultralytics import YOLO
model = YOLO('models/yolov8s_playing_cards.pt')
print(model.names)

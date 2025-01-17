from ultralytics import YOLO

# 1. Load a YOLO v11 model (pretrained checkpoint).
#    This is similar to "yolo11n.pt" from your example.
model = YOLO("yolo11x.pt")

# 2. Train the model on your custom dataset
#    - data="E:/Basim/Programming/Automation/2048/2048-dataset/data.yaml" for example
#    - Adjust epochs, imgsz, batch as needed
results = model.train(
    data="E:/Basim/Programming/Automation/2048/2048-dataset/data.yaml",   # path to your dataset config
    epochs=200,                  # number of training epochs
    imgsz=640,                  # image size used in training
    batch=2,                    # batch size
    name="yolo11x_custom_model_200_2"  # output folder inside 'runs/detect'
)

# 3. Evaluate the model on the validation set (defined in data.yaml)
val_results = model.val()

# 4. Perform inference on a sample image (URL or local path)
detection_results = model("board.png")

# 5. (Optional) Export the model to ONNX format
export_success = model.export(format="onnx")

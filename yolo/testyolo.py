from ultralytics import YOLO
import cv2

# Load the trained model (e.g., best.pt or last.pt)
model = YOLO("E:/Basim/Programming/Automation/2048/runs/detect/yolo11x_custom_model_200_2/weights/best.pt")

# 1) Single image
results = model("test.jpg")  # or .png, or even a URL

# results is a list of Prediction objects, one per image
for r in results:
    # r.plot() returns an annotated image (as a NumPy array)
    annotated_img = r.plot()
    # Display in a window (requires OpenCV)
    cv2.imshow("YOLO Detection", annotated_img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

import torch
import torchvision.transforms as T
from torchvision.models.detection import fasterrcnn_resnet50_fpn
import cv2

# Load the model from the checkpoint
model = fasterrcnn_resnet50_fpn(pretrained=False)
model.load_state_dict(torch.load("./detect/train/weights/best.pt"))
model.eval()

# Define the image transformations
transform = T.Compose([T.ToPILImage(), T.ToTensor()])

# Open the video capture
video_capture = cv2.VideoCapture("7.mp4")  # Replace with the path to your video

# Define the VideoWriter to save the output
output_path = "output_video.mp4"
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
output_video = cv2.VideoWriter(output_path, fourcc, 30.0, (640, 480))  # Adjust frame size and frame rate as needed

while True:
    ret, frame = video_capture.read()
    if not ret:
        break

    image = transform(frame)

    # Make the prediction
    with torch.no_grad():
        prediction = model([image])

    # Access the predicted bounding boxes, labels, and scores
    boxes = prediction[0]['boxes']
    labels = prediction[0]['labels']
    scores = prediction[0]['scores']

    for box, label, score in zip(boxes, labels, scores):
        if score > 0.7:  # Adjust the threshold as needed
            # Draw bounding box on the frame
            color = (0, 255, 0)  # BGR color code (green)
            cv2.rectangle(frame, (int(box[0]), int(box[1])), (int(box[2]), int(box[3]), color, 2))
            cv2.putText(frame, f"Label: {label}, Score: {score:.2f}", (int(box[0]), int(box[1]) - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

            # Write the frame to the output video
            output_video.write(frame)

            # Release the video capture and output video
            video_capture.release()
            output_video.release()

            # Destroy any OpenCV windows opened during processing
            cv2.destroyAllWindows()

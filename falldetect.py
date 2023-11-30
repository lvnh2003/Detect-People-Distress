import torch
import cv2
import math
from torchvision import transforms
import numpy as np
import telepot
import os
from utils.datasets import letterbox
from utils.general import non_max_suppression_kpt
from utils.plots import output_to_keypoint
import time

# Thay đổi các giá trị dưới đây để phù hợp với thông tin của bạn
token = '6118554466:AAG_fvbrs22py40Kvl8AM1Acgy2dvdYLpQU'
receiver_id = 6363898417
video_path = '5.mp4'
yolov7_weights_path = './yolov7-w6-pose.pt'

bot = telepot.Bot(token)

device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
weights = torch.load(yolov7_weights_path, map_location=torch.device('cpu'))
model = weights['model'].float().to(device)
_ = model.eval()

cap = cv2.VideoCapture(video_path)

if not cap.isOpened():
    print('Error while trying to read video. Please check the path again')

frame_width = int(cap.get(3))
frame_height = int(cap.get(4))

vid_write_image = letterbox(cap.read()[1], frame_width, stride=100, auto=True)[0]
resize_height, resize_width = vid_write_image.shape[:2]
# out_video_name = f"{video_path.split('/')[-1].split('.')[0]}"
# out = cv2.VideoWriter(f"{out_video_name}_keypoint.mp4",
#                       cv2.VideoWriter_fourcc(*'mp4v'), 30,
#                       (resize_width, resize_height))

frame_count = 0
cv2.namedWindow("Fall Detection Video", cv2.WINDOW_NORMAL)
start_time = time.time()
while cap.isOpened:
    print("Frame {} Processing".format(frame_count))
    frame_count += 1
    ret, frame = cap.read()
    if ret:
        orig_image = frame
        image = cv2.cvtColor(orig_image, cv2.COLOR_BGR2RGB)
        image = letterbox(image, frame_width, stride=64, auto=True)[0]
        image_ = image.copy()
        image = transforms.ToTensor()(image)
        image = torch.tensor(np.array([image.numpy()]))
        image = image.float().to(device)

        with torch.no_grad():
            output, _ = model(image)

        output = non_max_suppression_kpt(output, 0.25, 0.65, nc=model.yaml['nc'], nkpt=model.yaml['nkpt'],
                                         kpt_label=True)
        output = output_to_keypoint(output)
        im0 = image[0].permute(1, 2, 0) * 255
        im0 = im0.cpu().numpy().astype(np.uint8)
        im0 = cv2.cvtColor(im0, cv2.COLOR_RGB2BGR)

        for idx in range(output.shape[0]):
            xmin, ymin = (output[idx, 2] - output[idx, 4] / 2), (output[idx, 3] - output[idx, 5] / 2)
            xmax, ymax = (output[idx, 2] + output[idx, 4] / 2), (output[idx, 3] + output[idx, 5] / 2)

            left_shoulder_y = output[idx][23]
            left_shoulder_x = output[idx][22]
            right_shoulder_y = output[idx][26]

            left_body_y = output[idx][41]
            left_body_x = output[idx][40]
            right_body_y = output[idx][44]

            len_factor = math.sqrt(((left_shoulder_y - left_body_y) ** 2 + (left_shoulder_x - left_body_x) ** 2))

            left_foot_y = output[idx][53]
            right_foot_y = output[idx][56]

            if left_shoulder_y > left_foot_y - len_factor and left_body_y > left_foot_y - (
                    len_factor / 2) and left_shoulder_y > left_body_y - (len_factor / 2):
                cv2.rectangle(im0, (int(xmin), int(ymin)), (int(xmax), int(ymax)), color=(0, 0, 255),
                              thickness=5, lineType=cv2.LINE_AA)
                cv2.putText(im0, 'Person Fell down', (11, 100), 0, 1, [0, 0, 255], thickness=3, lineType=cv2.LINE_AA)
            
                bot.sendMessage(receiver_id, "Person Fall Detected")
                filename = "./savedImage.jpg"
                cv2.imwrite(filename, im0)
                bot.sendPhoto(receiver_id, photo=open(filename, 'rb'))
                os.remove(filename)

        cv2.imshow("Fall Detection Video", im0)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    else:
        break

cap.release()
cv2.destroyAllWindows()

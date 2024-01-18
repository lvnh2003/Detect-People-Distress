from roboflow import Roboflow
rf = Roboflow(api_key="ydEbRg6dO7WEXTMh1mDO")
project = rf.workspace("nguyen-ngoc-lanh").project("fall_detection_person")
dataset = project.version(1).download("yolov8")
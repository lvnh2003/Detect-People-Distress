from datetime import datetime
import telepot
import os
token = '6118554466:AAG_fvbrs22py40Kvl8AM1Acgy2dvdYLpQU'
receiver_id = 6363898417 # https://api.telegram.org/bot<TOKEN>/getUpdates
class DetectFunction:
    def __init__(self):
        self.bot = telepot.Bot(token)
    def is_Danger_Time(self,start,end):
        current_time = datetime.now().time()
        return start <= current_time <= end
    def sendMessage(self,image_path):
        with open(image_path, "rb") as image_file:
            self.bot.sendPhoto(receiver_id, image_file, caption="Object Detection")
        os.remove(image_path)
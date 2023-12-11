from datetime import datetime
import os
token = '6118554466:AAG_fvbrs22py40Kvl8AM1Acgy2dvdYLpQU'
receiver_id = 6363898417 # https://api.telegram.org/bot<TOKEN>/getUpdates
class DetectFunction:
    def is_Danger_Time(self,start,end):
        current_time = datetime.now().time()
        return start <= current_time <= end

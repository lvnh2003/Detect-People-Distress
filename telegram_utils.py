# import requests
#
#
# def send_telegram_message(api_token, chat_id, message):
#     base_url = f"https://api.telegram.org/bot{api_token}/sendMessage"
#     params = {
#         "chat_id": chat_id,
#         "text": message
#     }
#
#     response = requests.get(base_url, params=params)
#
#     if response.status_code == 200:
#         print("Message sent successfully.")
#     else:
#         print("Failed to send message.")
#
#
# # Thay thế bằng API Token và chat_id của bot và người nhận
# api_token = "6118554466:AAG_fvbrs22py40Kvl8AM1Acgy2dvdYLpQU"
# chat_id = "6363898417"
# message = "Hello from your bot!"
#
# send_telegram_message(api_token, chat_id, message)

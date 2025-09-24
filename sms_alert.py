# # sms_alert.py
# from twilio.rest import Client

# account_sid = ''
# auth_token = '' 
# twilio_number = ''  # Your Twilio phone number
# recipient_number = ''  # Your phone number

# def send_sms_alert():
#     client = Client(account_sid, auth_token)
#     message = client.messages.create(
#         body="⚠️ Fall detected! Immediate attention required.",
#         from_=twilio_number,
#         to=recipient_number
#     )
#     print(f"SMS sent! SID: {message.sid}")

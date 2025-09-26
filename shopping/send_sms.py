import africastalking
from decouple import config

# Initialize SDK
username = config("AT_USERNAME")
api_key = config("AT_KEY")
africastalking.initialize(username, api_key)


def format_phone_number(phone_number):
    """Format phone number to +254 format"""
    if not phone_number or not isinstance(phone_number, str):
        return None

    new_phone = phone_number.replace(" ", "")

    if new_phone.startswith("0"):
        return "+254" + new_phone[1:]
    elif new_phone.startswith("+254"):
        return new_phone

    return phone_number


def send_sms(phone_number, message):
    sms = africastalking.SMS
    response = sms.send(message, [format_phone_number(phone_number)])

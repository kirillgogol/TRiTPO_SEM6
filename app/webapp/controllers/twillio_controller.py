from twilio.rest import Client
from app.settings import settings


def send_sms(to_number, body):
    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    return client.messages.create(from_=settings.TWILIO_PHONE_NUMBER,
                                  to=to_number, body=body)
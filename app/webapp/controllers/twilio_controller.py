from twilio.rest import Client
from app.settings import settings
from app.exceptions import *
from twilio.base.exceptions import TwilioRestException

def verify_twilio():
    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    return client.verify.services(settings.TWILIO_SID_SERVICE)


def sms_verification(phone):
    verifying_service = verify_twilio()
    try:
        verifying_service.verifications.create(to=phone, channel='sms')
    except TwilioRestException as e:
        raise TwilioError


def sms_verification_check(data):
    verifying_sevice = verify_twilio()
    try:
        result = verifying_sevice.verification_checks.create(to=data['phone'], code=data['code'])
        if result.status == 'approved':
            return True
        return False
    except TwilioRestException as e:
        raise TwilioError

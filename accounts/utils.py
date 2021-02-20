import logging
import random

from twilio.rest import Client

from django.conf import settings

logger = logging.getLogger(__name__)


def send_sms_code(user_phone):
    """
    Generate 4-digit passcode and send it to user
    """
    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    code = str(random.randint(0, 9999)).rjust(4, '0')

    try:
        _ = client.messages.create(
            to=str(user_phone),
            from_=settings.TWILIO_NUMBER,
            body=f"Your Turbo verification code is: {code}"
        )
    except Exception as e:
        # print(f"\n--- Can't send SMS to {user_phone}")
        logger.error(f"Can't send SMS to {user_phone}\n{e}")
        # logger.error(e)
        return None
    else:
        logger.info(f"Phone verification message has been sent to {user_phone}")
        return code

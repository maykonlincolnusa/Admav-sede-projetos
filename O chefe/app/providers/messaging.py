from abc import ABC, abstractmethod

from twilio.rest import Client

from app.config import settings
from app.secrets import resolve_secret


class MessagingProvider(ABC):
    @abstractmethod
    def send_message(self, phone: str, body: str, channel: str = "sms") -> str:
        raise NotImplementedError


class ConsoleMessagingProvider(MessagingProvider):
    def send_message(self, phone: str, body: str, channel: str = "sms") -> str:
        print(f"[CONSOLE MESSAGE] channel={channel} to={phone} body={body}")
        return "console-message"


class TwilioMessagingProvider(MessagingProvider):
    def __init__(self):
        self.account_sid = resolve_secret("TWILIO_ACCOUNT_SID", settings.twilio_account_sid)
        self.auth_token = resolve_secret("TWILIO_AUTH_TOKEN", settings.twilio_auth_token)
        self.messaging_from = resolve_secret("TWILIO_MESSAGING_FROM", settings.twilio_messaging_from)
        self.whatsapp_from = resolve_secret("TWILIO_WHATSAPP_FROM", settings.twilio_whatsapp_from)

        if not self.account_sid or not self.auth_token:
            raise ValueError("Twilio nao configurado no .env (account sid/auth token).")
        self.client = Client(self.account_sid, self.auth_token)

    def _resolve_from(self, channel: str) -> str:
        if channel == "whatsapp":
            if not self.whatsapp_from:
                raise ValueError("TWILIO_WHATSAPP_FROM nao configurado no .env")
            return self.whatsapp_from
        if not self.messaging_from:
            raise ValueError("TWILIO_MESSAGING_FROM nao configurado no .env")
        return self.messaging_from

    def _resolve_to(self, phone: str, channel: str) -> str:
        if channel == "whatsapp":
            if phone.startswith("whatsapp:"):
                return phone
            return f"whatsapp:{phone}"
        return phone

    def send_message(self, phone: str, body: str, channel: str = "sms") -> str:
        from_value = self._resolve_from(channel)
        to_value = self._resolve_to(phone, channel)
        msg = self.client.messages.create(
            body=body,
            from_=from_value,
            to=to_value,
        )
        return msg.sid


def get_messaging_provider() -> MessagingProvider:
    if settings.channel_provider.lower() == "twilio":
        return TwilioMessagingProvider()
    return ConsoleMessagingProvider()

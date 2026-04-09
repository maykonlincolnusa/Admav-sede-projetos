from abc import ABC, abstractmethod
from html import escape

from twilio.rest import Client

from app.config import settings
from app.secrets import resolve_secret


class CallingProvider(ABC):
    @abstractmethod
    def make_call(self, phone: str, spoken_text: str) -> str:
        raise NotImplementedError


class ConsoleCallingProvider(CallingProvider):
    def make_call(self, phone: str, spoken_text: str) -> str:
        print(f"[CONSOLE CALL] to={phone} text={spoken_text}")
        return "console-call"


class TwilioCallingProvider(CallingProvider):
    def __init__(self):
        self.account_sid = resolve_secret("TWILIO_ACCOUNT_SID", settings.twilio_account_sid)
        self.auth_token = resolve_secret("TWILIO_AUTH_TOKEN", settings.twilio_auth_token)
        self.calling_from = resolve_secret("TWILIO_CALLING_FROM", settings.twilio_calling_from)
        if not self.account_sid or not self.auth_token or not self.calling_from:
            raise ValueError("Twilio de ligacoes nao configurado no .env")
        self.client = Client(self.account_sid, self.auth_token)

    def make_call(self, phone: str, spoken_text: str) -> str:
        safe_text = escape(spoken_text, quote=False)
        twiml = f"<Response><Say language='pt-BR'>{safe_text}</Say></Response>"
        call = self.client.calls.create(
            twiml=twiml,
            from_=self.calling_from,
            to=phone,
        )
        return call.sid


def get_calling_provider() -> CallingProvider:
    if settings.channel_provider.lower() == "twilio":
        return TwilioCallingProvider()
    return ConsoleCallingProvider()

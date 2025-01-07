from pydantic import BaseModel


class BrokerEmailMessage(BaseModel):
    emails: list[str]
    text_audio: str

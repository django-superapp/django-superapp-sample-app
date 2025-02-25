from typing import Optional, List

import ding
from ding.models import components
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from sms import Message
from sms.backends.base import BaseSmsBackend


class PreludeSmsBackend(BaseSmsBackend):
    def __init__(self, fail_silently: bool = False, **kwargs) -> None:
        super().__init__(fail_silently=fail_silently, **kwargs)

        api_key: Optional[str] = getattr(settings, 'PRELUDE_API_TOKEN')
        if not api_key and not self.fail_silently:
            raise ImproperlyConfigured(
                "You're using the Prelude SMS backend "
                "without having the setting 'PRELUDE_API_TOKEN' set"
            )

        self.client = ding.Ding(
            api_key=api_key,
        ) if api_key else None

    def send_messages(self, messages: List[Message]) -> int:
        if not self.client:
            return 0

        msg_count: int = 0
        for message in messages:
            for recipient in message.recipients:
                try:
                    self.client.messages.create(
                        to=recipient,
                        from_=message.originator,
                        body=message.body
                    )
                except Exception as exc:
                    if not self.fail_silently:
                        raise exc
                msg_count += 1
        return msg_count
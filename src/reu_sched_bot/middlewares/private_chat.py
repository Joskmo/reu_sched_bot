from typing import Any, Awaitable, Callable, Dict, Optional

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject


class PrivateChatMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        chat_type = self._extract_chat_type(event)
        if chat_type is not None and chat_type != "private":
            return None
        return await handler(event, data)

    @staticmethod
    def _extract_chat_type(event: TelegramObject) -> Optional[str]:
        chat = getattr(event, "chat", None)
        if chat is not None:
            return getattr(chat, "type", None)

        message = getattr(event, "message", None)
        if message is not None:
            chat = getattr(message, "chat", None)
            if chat is not None:
                return getattr(chat, "type", None)

        return None

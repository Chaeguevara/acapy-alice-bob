from abc import ABC, abstractmethod
import logging

from ..error import BaseError
from .responder import BaseResponder
from .request_context import RequestContext


class HandlerException(BaseError):
    """Exception base class for generic handler errors"""


class BaseHandler(ABC):
    """Abstract base class for handlers."""
    def __init__(self) -> None:
        self._logger = logging.getLogger(__name__)

    @abstractmethod
    async def handle(self, context: RequestContext, responder: BaseResponder):
        pass

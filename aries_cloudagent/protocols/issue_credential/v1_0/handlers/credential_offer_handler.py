"""Credential offer message handler."""

import time

from .....messaging.base_handler import (
    BaseHandler,
    BaseResponder,
    HandlerException,
    RequestContext,
)

from ..manager import CredentialManager
from ..messages.credential_offer import CredentialOffer

from .....utils.tracing import trace_event


class CredentialOfferHandler(BaseHandler):
    """Message handler class for credential offers."""

    async def handle(self, context: RequestContext, responder: BaseResponder):
        """
        Message handler logic for credential offers.

        Args:
            context: request context
            responder: responder callback

        """
        r_time = time.perf_counter()

        self._logger.debug("CredentialOfferHandler called with context %s", context)
        assert isinstance(context.message, CredentialOffer)
        self._logger.info(
            "Received credential offer message: %s",
            context.message.serialize(as_string=True),
        )

        if not context.connection_ready:
            raise HandlerException("No connection established for credential offer")

        credential_manager = CredentialManager(context)

        credential_exchange_record = await credential_manager.receive_offer()

        r_time = trace_event(
            context.settings,
            context.message,
            handler=context.settings.get("trace.label")
            if context and context.settings and context.settings.get("trace.label")
            else "aca-py.agent",
            outcome="CredentialOfferHandler.handle.END",
            perf_counter=r_time
        )

        # If auto respond is turned on, automatically reply with credential request
        if context.settings.get("debug.auto_respond_credential_offer"):
            (_, credential_request_message) = await credential_manager.create_request(
                credential_exchange_record=credential_exchange_record,
                holder_did=context.connection_record.my_did,
            )
            await responder.send_reply(credential_request_message)

            trace_event(
                context.settings,
                credential_request_message,
                handler=context.settings.get("trace.label")
                if context.settings and context.settings.get("trace.label")
                else "aca-py.agent",
                outcome="CredentialOfferHandler.handle.REQUEST",
                perf_counter=r_time
            )

from handlers.base import WidgetDataHandler
from handlers.issue_trend_handler import IssueTrendHandler
from handlers.member_summary_handler import MemberMonthlySummaryHandler

_HANDLERS: dict[str, WidgetDataHandler] = {}


def _register(handler: WidgetDataHandler):
    _HANDLERS[handler.source_key] = handler


# Register all handlers here
_register(IssueTrendHandler())
_register(MemberMonthlySummaryHandler())


def get_handler(source_key: str) -> WidgetDataHandler:
    handler = _HANDLERS.get(source_key)
    if not handler:
        raise ValueError(f"No handler registered for source_key='{source_key}'")
    return handler

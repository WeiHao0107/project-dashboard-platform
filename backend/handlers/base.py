from abc import ABC, abstractmethod
from schemas import WidgetQueryRequest, WidgetDataResponse


class WidgetDataHandler(ABC):
    @property
    @abstractmethod
    def source_key(self) -> str:
        """Matches widget_data_source_registry.source_key"""

    @abstractmethod
    def query(self, request: WidgetQueryRequest, db) -> WidgetDataResponse:
        """Execute the data query and return a WidgetDataResponse."""

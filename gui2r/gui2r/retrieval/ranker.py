from abc import ABC, abstractmethod
from typing import Any, Optional, Text, Dict, List

from sentence_transformers import SentenceTransformer

from gui2r.documents import Document, RankedDocument

class Ranker(ABC):

    @abstractmethod
    def initialize(self, documents: List[Document], path: Optional[Text]) -> None:
        raise NotImplementedError

    @abstractmethod
    def rank(self, query: Text) -> List[RankedDocument]:
        raise NotImplementedError

    @abstractmethod
    def rank(self, query: Text, rank_threshold: float) -> List[RankedDocument]:
        raise NotImplementedError

    @classmethod
    def persist(self, path: Optional[Text]) -> None:
        raise NotImplementedError

    @classmethod
    def load(
        cls,
        meta: Dict[Text, Any],
        model_dir: Optional[Text] = None,
        model_metadata: Optional["Metadata"] = None,
        cached_component: Optional["Component"] = None,
        **kwargs: Any
    ) -> "Ranker":
        """Load this component from file."""

        if cached_component:
            return cached_component
        else:
            return cls(meta)

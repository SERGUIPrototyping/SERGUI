from abc import ABC, abstractmethod
from typing import Optional, Text, List, Tuple, Set

from sentence_transformers import SentenceTransformer

from gui2r.retrieval.configuration.conf import Configuration


class Ranker(ABC):

    R_SENTBERT = 'sent-bert'
    R_META = 'meta'
    R_S2W = 's2w'
    R_S2W_MAX = 's2w-max'

    SBERT_MODEL = SentenceTransformer('all-mpnet-base-v2')


    @abstractmethod
    def rank(self, query: Text, rank_threshold: Optional[float] = 0.0,
             rank_cutoff: Optional[int] = 100) -> List[Tuple[int, float]]:
        raise NotImplementedError

    @abstractmethod
    def rank_gs(self, query: Text, goldstandard: Set[int], rank_threshold: Optional[float] = 0.0,
             rank_cutoff: Optional[int] = 100) -> List[Tuple[int, float]]:
        raise NotImplementedError

    @abstractmethod
    def persist(self, path: Optional[Text]) -> None:
        raise NotImplementedError

    @staticmethod
    def load(conf: Configuration, force: Optional[bool] = False,
             persist: Optional[bool] = True) -> "Ranker":
        raise NotImplementedError

    @abstractmethod
    def get_name(self):
        raise NotImplementedError

    @staticmethod
    def get_text(conf: Configuration, data) -> List[Text]:
        text = []
        for text_segment in conf.text_segments_used:
            text.extend(data[text_segment])
        return text
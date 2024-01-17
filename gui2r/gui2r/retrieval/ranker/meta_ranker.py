from typing import Text, List, Optional, Tuple, Set
from gui2r.retrieval.ranker.ranker_v2 import Ranker
from gui2r.retrieval.configuration.conf import Configuration
from gui2r.retrieval.ranker.s2w_ranker import S2WRanker
from gui2r.retrieval.ranker.sentence_bert_ranker import SentenceBERTRanker
from gui2r.retrieval.ranker.vsm_lda_ranker import LDARanker
from gui2r.retrieval.ranker.vsm_lsi_ranker import LSIRanker
from gui2r.retrieval.ranker.bm25okapi_ranker import BM25OkapiRanker
from gui2r.retrieval.ranker.vsm_tfidf_ranker import TFIDFRanker
import numpy as np

import logging

logging.getLogger().setLevel(logging.INFO)


class MetaRanker2(Ranker):


    def __init__(self, conf: Configuration, rankers: List[Ranker]):
        self.conf = conf
        self.rankers = rankers

    def rank(self, query: Text, rank_threshold: Optional[float] = 0.0,
             rank_cutoff: Optional[int] = 100) -> List[Tuple[int, float]]:
        rank_map = {}
        for ranker in self.rankers:
            ranking = ranker.rank(query, rank_cutoff=rank_cutoff)
            for (index, conf) in ranking:
                if rank_map.get(index): rank_map[index].append(conf)
                else: rank_map[index] = [conf]
        rank_map_flat = {index: np.mean(confs) for (index, confs) in rank_map.items()}
        ranking_sorted = [(index, conf) for (index, conf) in
                sorted(rank_map_flat.items(), key=lambda item: item[1],
                       reverse=True)][:rank_cutoff]
        return ranking_sorted

    def rank_gs(self, query: Text, goldstandard: Set[int], rank_threshold: Optional[float] = 0.0,
                rank_cutoff: Optional[int] = 100) -> List[Tuple[int, float]]:
        rank_map = {}
        for ranker in self.rankers:
            ranking = ranker.rank_gs(query, goldstandard=goldstandard, rank_cutoff=rank_cutoff)
            for (index, conf) in ranking:
                if rank_map.get(index): rank_map[index].append(conf)
                else: rank_map[index] = [conf]
        results = [(index, float(np.mean(confs))) for (index, confs) in rank_map.items()]
        results_sorted = sorted(results, key=lambda x: x[1], reverse=True)
        print(results_sorted)
        return results_sorted

    def persist(self, path: Optional[Text]) -> None:
        pass

    @staticmethod
    def load(conf: Configuration, force: Optional[bool] = False,
             persist: Optional[bool] = True) -> "MetaRanker2":
        rankers = [SentenceBERTRanker.load(conf, persist=persist), S2WRanker.load(conf, persist=persist)]
        return MetaRanker2(conf=conf, rankers=rankers)

    def get_name(self):
        return Ranker.R_META

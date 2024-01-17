import copy
from typing import Text, List, Optional, Dict, Tuple, Set
from gui2r.documents import Document, RankedDocument
from gui2r.retrieval.configuration.conf import Configuration
from gui2r.preprocessing.preprocess import Preprocessor
from gui2r.retrieval.ranker.ranker_v2 import Ranker
from gui2r.retrieval.ranker.s2w_ranker import S2WRanker
#from gui2r.retrieval.ranker.meta_ranker import MetaRanker
from gui2r.retrieval.ranker.sentence_bert_ranker import SentenceBERTRanker
from gui2r.preprocessing.extraction import Extractor

import logging

logging.getLogger().setLevel(logging.INFO)


class Retriever(object):

    def __init__(self, conf: Configuration, ranker: Optional[Dict[Text, Ranker]] = None):
        self.conf = conf
        if ranker:
            self.ranker = ranker
        else:
            self.ranker = {
                Ranker.R_S2W : S2WRanker.load(conf),
                Ranker.R_SENTBERT : SentenceBERTRanker.load(conf)}
        self.preprocessor = Preprocessor()
        self.expander = {}

    def rank(self, query: Text, method: Optional[Text] =
             Ranker.R_BOOL, qe_method: Optional[Text] = None,
             max_results: Optional[int] = 100) -> List[RankedDocument]:
        ranker = self.ranker[method]
        result = ranker.rank(query, rank_cutoff=max_results)
        ranked_docs = self.construct_ranked_docs(result)
        return ranked_docs

    def rank_gs(self, query: Text, goldstandard: Set[int], method: Optional[Text] =
             Ranker.R_BOOL, qe_method: Optional[Text] = None,
             max_results: Optional[int] = 100) -> List[RankedDocument]:
        ranker = self.ranker[method]
        result = ranker.rank_gs(query, goldstandard, rank_cutoff=max_results)
        ranked_docs = self.construct_ranked_docs(result)
        return ranked_docs

    def construct_ranked_docs(self, results: List[Tuple[int, float]]):
        ranked_docs = [RankedDocument(document=
            Document(index, self.conf.path_guis+str(index)+'.jpg', str(index)+'.jpg'), rank=rank, conf=conf)
                       for (rank, (index, conf)) in enumerate(results, start=1)]
        return ranked_docs
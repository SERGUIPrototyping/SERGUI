from typing import Text, List, Optional, Dict, Tuple, Set

import torch

from gui2r.retrieval.ranker.ranker_v2 import Ranker
from gui2r.retrieval.configuration.conf import Configuration
from gui2r.preprocessing.preprocess import Preprocessor
from gui2r.preprocessing.extraction import Extractor
import gui2r.utils as utils
import os, pickle
import numpy as np
from sentence_transformers import SentenceTransformer, util
import scipy.spatial as spatial

import logging

logging.getLogger().setLevel(logging.INFO)


class S2WRanker(Ranker):

    preprocessor = Preprocessor()
    extractor = Extractor(preprocessor)

    def __init__(self, conf: Configuration,
                 model: SentenceTransformer,
                 doc_embeddings: List[np.array],
                 index_mapping: Dict[int, int],
                 agg_method: Text):
        self.conf = conf
        self.model = model
        self.doc_embeddings = doc_embeddings
        self.index_mapping = index_mapping
        self.num_docs = len(self.index_mapping)
        self.agg_method = agg_method

    def rank(self, query: Text, rank_threshold: Optional[float] = 0.0,
             rank_cutoff: Optional[int] = 100) -> List[Tuple[int, float]]:
        preproc_query = S2WRanker.preprocessor.\
            preprocess_text(query, tokenized=False, remove_stopwords=self.conf.preprocesing_rm_stopwords,
                            stemmed=self.conf.preprocesing_stemmed,
                            stemming=self.conf.preprocessing_stemmer)
        preproc_query_norm = preproc_query[0]
        top_k = self.compute_ranking(preproc_query_norm, rank_cutoff)
        return top_k

    def rank_gs(self, query: Text, goldstandard: Set[int], rank_threshold: Optional[float] = 0.0,
             rank_cutoff: Optional[int] = 100) -> List[Tuple[int, float]]:
        preproc_query = S2WRanker.preprocessor.\
            preprocess_text(query, tokenized=False, remove_stopwords=self.conf.preprocesing_rm_stopwords,
                            stemmed=self.conf.preprocesing_stemmed,
                            stemming=self.conf.preprocessing_stemmer)
        top_n = self.compute_ranking(preproc_query[0], rank_cutoff=57764)
        results =  []
        found_idxs = set()
        for rico_index, conf in top_n:
            if rico_index in goldstandard:
                results.append((rico_index, conf))
                found_idxs.add(rico_index)
        missing_idxs = set(goldstandard).difference(found_idxs)
        for miss_idx in missing_idxs:
            results.append((miss_idx, 0.))
        results_sorted = sorted(results, key=lambda x: x[1], reverse=True)
        return results_sorted

    def compute_ranking(self, query: Text, rank_cutoff: int):
        query_embedding = self.model.encode([query])[0]
        # Initialize cosine scores with zeros
        if not self.agg_method == 'max':
            cos_scores = torch.zeros(self.num_docs)
        # Compute cosine scores for each embedding matrix and compute averge
        for idd, embed in enumerate(self.doc_embeddings):
            curr_cos_scores = util.pytorch_cos_sim(query_embedding, embed)[0]
            if self.agg_method == 'max':
                if idd == 0:
                    cos_scores = curr_cos_scores.resize_((1,len(curr_cos_scores)))
                else:
                    cos_scores = torch.cat((cos_scores, curr_cos_scores.resize_((1,len(curr_cos_scores)))), dim=0)
            else:
                cos_scores = curr_cos_scores + cos_scores
        if self.agg_method == 'max':
            cos_scores = torch.amax(cos_scores, dim=(0))
        else:
            cos_scores = cos_scores / len(self.doc_embeddings)
        top_k = torch.topk(cos_scores, k=self.num_docs)
        top_k_results = [self.index_mapping[elem] for elem in list(np.array(top_k[1]))]
        top_k_confs = [float(elem) for elem in list(np.array(top_k[0]))]
        return list(zip(top_k_results, top_k_confs))[:rank_cutoff]

    def persist(self, path: Optional[Text]) -> None:
        pass


    @staticmethod
    def load(conf: Configuration, force: Optional[bool] = False,
             persist: Optional[bool] = True) -> "S2WRanker":
        model_path = conf.path_models + 's2w_ranker/'
        with open(model_path + 'index_mapping.pickle', mode='rb') as file:
            index_mapping = pickle.load(file)
        doc_embeddings = [np.load(model_path + 'embed_s2w_' + str(i) + '.npy') for i in range(0,5)]
        model = Ranker.SBERT_MODEL
        if conf.extras:
            if conf.extras.get('agg_method') == 'max':
                return S2WRanker(conf, model, doc_embeddings, index_mapping, 'max')
        return S2WRanker(conf, model, doc_embeddings, index_mapping, '')

    def get_name(self):
        return Ranker.R_S2W

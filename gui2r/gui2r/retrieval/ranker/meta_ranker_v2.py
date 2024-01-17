from typing import Text, List, Optional, Dict, Tuple

import numpy as np
from mergedeep import merge


class MetaRanker ():

    # Score methods for NLR query-related scores
    SCORE_NLR_NAME = 'score_nlr'
    SCORE_NLR_BM25 = 'score_nlr_bm25'
    SCORE_NLR_SENTBERT = 'score_nlr_sentbert'
    SCORE_NLR_S2W = 'score_nlr_s2w'
    SCORE_NLR_S2W_MAX = 'score_nlr_s2w_max'
    # Score methods for the detailed feedback on GUI features
    SCORE_FFB_NAME = 'score_ffb'
    SCORE_FFB_DFB_FEAT = 'score_ffb_dfb_feat'
    SCORE_FFB_AFB_FEAT = 'score_ffb_afb_feat'

    # All score categories names together
    ALL_SCORE_NAMES = (SCORE_CTX_NAME, SCORE_NLR_NAME, SCORE_GFB_NAME, SCORE_FFB_NAME)

    # Available aggregation methods to aggregate scores from above score categories
    AGG_MEAN = 'agg_mean'
    AGG_WEIGHTED_MEAN = 'agg_weighted_mean'

    def __init__(self, scores: Optional[Dict[Text, Dict[Text, float]]] = None,
                       score_names: Optional[Dict[Text, List[Text]]] = None,
                       filter_gui_idxs: Optional[List[int]] = None,
                       round_scores: Optional[int] = 3):
        self.scores = scores if scores else {}
        self.score_names = score_names if score_names else {}
        self.filter_gui_idxs = filter_gui_idxs if filter_gui_idxs else []
        self.round_scores = round_scores

    def get_ranking(self, agg_method: Optional[Text] = AGG_MEAN) -> List[Tuple[Text, float]]:
        ranking = [(gui_index, self.compute_score(scores, agg_method))
                   for gui_index, scores in self.scores.items() if gui_index not in self.filter_gui_idxs]
        ranking_sorted = sorted(ranking, key=lambda x: x[1], reverse=True)
        return ranking_sorted

    def compute_score(self, scores: Dict[Text, float], agg_method: Text) -> float:
        agg_scores = []
        print(self.score_names)
        for score_name in MetaRanker.ALL_SCORE_NAMES:
            if score_name in self.score_names:
                agg_scores.append(
                    np.mean([scores[sn] if sn in scores else 0
                    for sn in self.score_names[score_name]]))
        return round(float(np.mean(np.array(agg_scores))), self.round_scores)

    def add_results(self, results: List[Tuple[Text, float]], score_name: Text, append: Optional[bool] = True) -> None:
        # Create method name and add suffix to allow to add multiple scores of the same type
        score_name_cat = '_'.join(score_name.split('_')[:2])
        if append and score_name_cat in self.score_names:
            score_name = score_name + '_' + self.get_next_score_index(score_name, score_name_cat)
        # Transform the results to the initial score dictionary for merging
        scores = {str(gui_index): {score_name: score} for gui_index, score in results}
        merged_scores = merge({}, self.scores, scores)
        # Filter scores using the filter gui idxs
        print(len(merged_scores))
        self.scores = merged_scores
        if score_name_cat in self.score_names:
            curr_score_names = self.score_names[score_name_cat]
            curr_score_names.append(score_name)
            self.score_names[score_name_cat] = curr_score_names
        else:
            self.score_names[score_name_cat] = [score_name]

    def get_scores(self) -> Dict[Text, Dict[Text, float]]:
        return self.scores

    def get_score_names(self) -> Dict[Text, List[Text]]:
        return self.score_names

    def get_next_score_index(self, score_name: Text, score_name_cat: Text) -> Text:
        score_index = len([score_name for sn in self.score_names[score_name_cat] if score_name in sn])
        return str(score_index) if score_index > 0 else ''

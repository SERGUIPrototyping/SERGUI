import copy
import pickle
from typing import Text, List, Optional, Dict, Tuple
import pandas as pd
import numpy as np
import re, random
from ast import literal_eval
from sentence_transformers import SentenceTransformer, util
from sklearn.cluster import DBSCAN
from collections import Counter
import torch

import logging

from gui2r.feature_ranking.feature_ranker_gpt import FeatureRankerGPTModel
from gui2r.retrieval.ranker.ranker_v2 import Ranker

logging.getLogger().setLevel(logging.INFO)

class FeatureRanker():

    # Feature sources available to extract feature descriptions from
    FEAT_SOURCE_TEXT_BUTTON = "button_text"
    FEAT_SOURCE_BUTTON_CLASS = "text_button_class"
    FEAT_SOURCE_ICON_CLASSES = "icon_class"
    FEAT_SOURCE_RESOURCE_IDS = "res_id"
    FEAT_SOURCE_INPUT_TEXT = "input_text_updated"
    FEAT_SOURCE_TEXT_LABELS = "label"

    # Icon class filter set of meaningless icon class feature descriptions
    ICON_CLASS_FILTER_SET = set(['arrow_backward', 'menu', 'more', 'arrow_forward', 'emoji'])

    # Icon class filter set of meaningless icon class feature descriptions
    BUTTON_CLASS_FILTER_SET = set(['back', 'menu'])

    # Aggregation methods for aggregating feature scores for a GUI
    AGG_FEAT_MEAN = 'agg_feat_mean'
    AGG_FEAT_MAX = 'agg_feat_max'
    AGG_FEAT_MIN = 'agg_feat_min'

    # Aggregation methods for aggregating the GUI scores for features from gpt
    AGG_GPT_FEAT_MEAN = 'agg_gpt_feat_mean'
    AGG_GPT_FEAT_THRESHOLD = 'agg_gpt_feat_threshold'

    # Reranking methods for the afb-based feature scores
    RERANK_ALL = 'rerank_all'
    RERANK_REL_ONLY = 'rerank_rel_only'
    RERANK_REL_ALL = 'rereank_rel_all'

    def __init__(self, abs_path_ui_data, max_num_tokens_feat_buttons=6, max_num_tokens_feat_rid=3,
                 max_num_tokens_feat_label=6, max_num_tokens_input=3,
                 sent_transformers_model='all-mpnet-base-v2', cluster_eps=0.3, cluster_min_samples=1,
                 cluster_metric="cosine", feat_unique_per_gui=False, shorter_text_top_k_perc=0.2):
        # Load dataset with precomputed embeddings for extracting gui features later on
        logging.info('Loading precomputed GUI feature data from "{}"'.format(abs_path_ui_data))
        self.feat_embeddings = np.load(abs_path_ui_data + "embeddings.npy")
        with open(abs_path_ui_data + 'gui2feat_ids.pickle', mode='rb') as file:
            self.gui2feat = pickle.load(file)
        with open(abs_path_ui_data + 'feat2comp.pickle', mode='rb') as file:
            self.feat2comp = pickle.load(file)
        with open(abs_path_ui_data + 'index2row.pickle', mode='rb') as file:
            self.index2row = pickle.load(file)
        with open(abs_path_ui_data + 'row2index.pickle', mode='rb') as file:
            self.row2index = pickle.load(file)
        # Restriction of number of tokens allowed per feature source
        self.max_num_tokens_feat_button = max_num_tokens_feat_buttons
        self.max_num_tokens_feat_rid = max_num_tokens_feat_rid
        self.max_num_tokens_feat_label = max_num_tokens_feat_label
        self.max_num_tokens_input = max_num_tokens_input
        self.shorter_text_top_k_perc = shorter_text_top_k_perc
        # Load the sentence transformer model used for embedding the feature texts
        logging.info('Loading Sentence Embedding model: "{}"'.format(sent_transformers_model))
        self.model = Ranker.SBERT_MODEL
        # Initialize the DBSCAN clustering model
        self.dbscan = DBSCAN(eps=cluster_eps, min_samples=cluster_min_samples, metric=cluster_metric)
        # Initialize further relevant feature ranking parameters
        self.feat_unique_per_gui = feat_unique_per_gui
        # Settings for the gpt model
        api_organization = ""
        api_key = ""
        self.feature_ranker_gpt_model = FeatureRankerGPTModel(api_organization, api_key)

    def gui_feature_extraction_precomputed(self, gui_index, sources, filter_query: Optional[Text] = None):
        features_ext = []
        if self.gui2feat.get(int(gui_index)):
            for feat in self.gui2feat.get(int(gui_index)):
                feat_id, embed_type = feat.split('-')
                if embed_type in sources:
                    ui_comp_data = self.feat2comp[feat]
                    embedding = self.feat_embeddings[self.index2row[feat]]
                    ui_comp_data_ext = copy.deepcopy(ui_comp_data)
                    ui_comp_data_ext['embedding'] = embedding
                    features_ext.append(ui_comp_data_ext)
            if filter_query:
                features_ext = [feature for feature in features_ext if feature.get('text') not in filter_query]
            return features_ext
        return []

    def generate_feature_ranking_precomputed(self, top_k_guis_idx, sources=(FEAT_SOURCE_TEXT_BUTTON,
                                 FEAT_SOURCE_ICON_CLASSES), cutoff_n=20, cutoff_score=1,
                                 filter_query=None, filter_features=(), filter_treshold=0.8,
                                 full_cluster=False):
        features_ext = [{'gui_id': gui_index, 'ui_comp_id': feature.get('ui_comp_id'), 'comp_type': feature.get('comp_type'),
                        'text': feature.get('text'), 'embedding': feature.get('embedding'),
                         'bounds': feature.get('bounds')} for gui_index in top_k_guis_idx
                        for feature in self.gui_feature_extraction_precomputed(gui_index, sources, filter_query)]
        feature_embeddings = np.array([feature.get("embedding") for feature in features_ext])
        clustering = self.dbscan.fit(feature_embeddings)
        feature_clusters = self.merge_feature_clusters_coherent(features_ext, clustering, filter_features,
                                                                filter_treshold, full_cluster)
        return [fc for fc in feature_clusters if fc.get('score') >= cutoff_score][:cutoff_n]

    def gui_feature_extraction(self, gui_doc, sources, filter_query: Optional[Text] = None):
        ui_comps = gui_doc['ui_comps']
        features_ext = []
        # Extract features from text button component type and restrict to maximum length of 6 tokens
        for ui_comp in ui_comps:
            if (FeatureRanker.FEAT_SOURCE_TEXT_BUTTON in sources) and (ui_comp.get('componentLabel') == 'Text Button'
                    and ui_comp.get('text') and len(ui_comp.get('text').split(' ')) <= self.max_num_tokens_feat_button):
                features_ext.append({'ui_comp_id': ui_comp.get('id'),
                                     'comp_type': ui_comp.get('componentLabel'),
                                     'text': self.preprocess_gui_feature(ui_comp.get('text')),
                                     'bounds': ui_comp.get('bounds')})
            if (FeatureRanker.FEAT_SOURCE_ICON_CLASSES in sources) and ((ui_comp.get('componentLabel') == 'Icon')
                        and not (ui_comp.get('iconClass') in FeatureRanker.ICON_CLASS_FILTER_SET)):
                features_ext.append({'ui_comp_id': ui_comp.get('id'),
                                     'comp_type': ui_comp.get('componentLabel'),
                                     'text': ' '.join(ui_comp.get('iconClass').split('_')),
                                     'bounds': ui_comp.get('bounds')})
            if (FeatureRanker.FEAT_SOURCE_BUTTON_CLASS in sources) and ui_comp.get('textButtonClass') \
                        and not (ui_comp.get('textButtonClass') in FeatureRanker.BUTTON_CLASS_FILTER_SET):
                features_ext.append({'ui_comp_id': ui_comp.get('id'),
                                     'comp_type': ui_comp.get('componentLabel'),
                                     'text': self.preprocess_gui_feature(ui_comp.get('textButtonClass')),
                                     'bounds': ui_comp.get('bounds')})
            if (FeatureRanker.FEAT_SOURCE_INPUT_TEXT in sources) and ui_comp.get('componentLabel')=='Input' \
                        and ui_comp.get('text_updated'):
                feature_text = self.preprocess_gui_feature(ui_comp.get('text_updated'))
                if feature_text and len(feature_text.split(' ')) <= self.max_num_tokens_input:
                    features_ext.append({'ui_comp_id': ui_comp.get('id'),
                                         'comp_type': ui_comp.get('componentLabel'),
                                         'text': feature_text,
                                         'bounds': ui_comp.get('bounds')})
            if (FeatureRanker.FEAT_SOURCE_RESOURCE_IDS in sources) and ui_comp.get('resource-id'):
                feature_text = FeatureRanker.normalize_resource_id(ui_comp.get('resource-id'))
                if len(feature_text.split(' ')) <= self.max_num_tokens_feat_rid:
                    features_ext.append({'ui_comp_id': ui_comp.get('id'),
                                         'comp_type': ui_comp.get('componentLabel'),
                                         'text': feature_text,
                                         'bounds': ui_comp.get('bounds')})
            if (FeatureRanker.FEAT_SOURCE_TEXT_LABELS in sources) and ui_comp.get('componentLabel')=='Text' \
                        and ui_comp.get('text'):
                feature_text = self.preprocess_gui_feature(ui_comp.get('text'))
                if feature_text and len(feature_text.split(' ')) <= self.max_num_tokens_feat_label:
                    features_ext.append({'ui_comp_id': ui_comp.get('id'),
                                         'comp_type': ui_comp.get('componentLabel'),
                                         'text': feature_text,
                                         'bounds': ui_comp.get('bounds')})
        # Create unique set of features based on text representation
        if self.feat_unique_per_gui:
            feats_observed = set()
            features_ext = [feats_observed.add(feature.get('text')) or feature for feature in features_ext
                            if feature.get('text') not in feats_observed]
        if filter_query:
            features_ext = [feature for feature in features_ext if feature.get('text') not in filter_query]
        return features_ext

    def generate_feature_ranking(self, top_k_guis_idx, sources=(FEAT_SOURCE_TEXT_BUTTON,
                                    FEAT_SOURCE_ICON_CLASSES), cutoff_n=20, cutoff_score=1,
                                    filter_query=None, filter_features=(), filter_treshold=0.8,
                                    full_cluster=False):
        features_ext = [{'gui_id': gui_index, 'ui_comp_id': feature.get('ui_comp_id'), 'comp_type': feature.get('comp_type'),
                        'text': feature.get('text'), 'embedding': self.gui_feature_embedding(feature.get('text')),
                         'bounds': feature.get('bounds')}
                        for gui_index in top_k_guis_idx
                        for feature in self.gui_feature_extraction(self.get_gui_doc(gui_index), sources, filter_query)]
        feature_embeddings = np.array([feature.get("embedding") for feature in features_ext])
        clustering = self.dbscan.fit(feature_embeddings)
        feature_clusters = self.merge_feature_clusters_coherent(features_ext, clustering, filter_features, filter_treshold, full_cluster)
        return [fc for fc in feature_clusters if fc.get('score') >= cutoff_score][:cutoff_n]

    def merge_feature_clusters_coherent(self, features_ext, clustering, filter_features, filter_treshold, full_cluster, prefer_short_text=True):
        cluster_mapping = {}
        for feature, cluster_id in zip(features_ext, clustering.labels_):
            if cluster_mapping.get(cluster_id):
                cluster_mapping[cluster_id]['features'].append(feature)
            else:
                cluster_mapping[cluster_id] = {'id': cluster_id, 'features': [feature]}
        feature_clusters = []
        filter_feature_embeddings = []
        for filter_feature in filter_features:
            filter_feature_embeddings.append(self.gui_feature_embedding(filter_feature))
        for index, value in cluster_mapping.items():
            # Check against all filter features if the feature cluster matches
            if not self.feature_cluster_filter_by_features(value.get('features'),
                                list(zip(filter_features, filter_feature_embeddings)), filter_treshold):
                if full_cluster:
                    feature_clusters.append({
                        'cluster_id': int(value.get('id')),
                        'gui_id': [int(feature.get('gui_id')) for feature in value.get('features')],
                        'feature_id': [feature.get('ui_comp_id') for feature in value.get('features')],
                        'text': [feature.get('text') for feature in value.get('features')],
                        'comp_type': [feature.get('comp_type') for feature in value.get('features')],
                        'bounds': [feature.get('bounds') for feature in value.get('features')],
                        'gui_idxs': list(set([feature.get('gui_id') for feature in value.get('features')])),
                        'score': self.compute_feature_cluster_score(value.get('features'))
                    })
                else:
                    if prefer_short_text:
                        features = sorted(value.get('features'), key=lambda x:len(x['text']), reverse=False)
                        index = int(len(features) * self.shorter_text_top_k_perc)
                        index = index if index >= 1 else 1
                        rand_selected_feature = random.choice(features[:index])
                    else:
                        rand_selected_feature = random.choice(value.get('features'))
                    feature_clusters.append({
                        'cluster_id': int(value.get('id')),
                        'gui_id': int(rand_selected_feature.get('gui_id')),
                        'feature_id': rand_selected_feature.get('ui_comp_id'),
                        'text': rand_selected_feature.get('text'),
                        'comp_type': rand_selected_feature.get('comp_type'),
                        'bounds': rand_selected_feature.get('bounds'),
                        'gui_idxs': list(set([feature.get('gui_id') for feature in value.get('features')])),
                        'score': self.compute_feature_cluster_score(value.get('features'))
                    })
            else:
                pass
        feature_clusters_sorted = sorted(feature_clusters, key=lambda x: x.get('score'), reverse=True)
        feature_clusters_sorted_rank = []
        for rank, feature_cluster in enumerate(feature_clusters_sorted, 1):
            feature_cluster['rank'] = rank
            feature_clusters_sorted_rank.append(feature_cluster)
        return feature_clusters_sorted_rank

    def feature_cluster_filter_by_features(self, features_in_cluster: List[Dict], filter_features: List[Tuple],
                                           filter_treshold: float, agg_method: Optional[Text] = AGG_FEAT_MEAN) -> bool:
        embeddings = np.array([f.get('embedding') for f in features_in_cluster])
        for ftrl_feature, feat_embedding in filter_features:
            cos_sims = np.array(util.pytorch_cos_sim(feat_embedding, embeddings)[0])
            agg_cos_sim = 0
            if agg_method == FeatureRanker.AGG_FEAT_MEAN:
                agg_cos_sim = np.mean(cos_sims)
            elif agg_method == FeatureRanker.AGG_FEAT_MAX:
                agg_cos_sim = np.max(cos_sims)
            elif agg_method == FeatureRanker.AGG_FEAT_MIN:
                agg_cos_sim = np.min(cos_sims)
            if agg_cos_sim >= filter_treshold:
                # We found at least one feature matching with at least filter threshold confidence
                return True
        return False

    def merge_feature_clusters(self, features_ext, clustering):
        cluster_mapping = {}
        for feature, cluster_id in zip(features_ext, clustering.labels_):
            if cluster_mapping.get(cluster_id):
                cluster_mapping[cluster_id]['features'].append(feature)
            else:
                cluster_mapping[cluster_id] = {'id': cluster_id, 'features': [feature]}
        feature_clusters = []
        for index, value in cluster_mapping.items():
            feature_clusters.append({
                'id': int(value.get('id')),
                'text': self.extract_feature_text([feature.get('text') for feature in value.get('features')]),
                'comp_type': self.extract_feature_comp_type([feature.get('comp_type') for feature in value.get('features')]),
                'gui_idxs': list(set([feature.get('gui_id') for feature in value.get('features')])),
                'score': self.compute_feature_cluster_score(value.get('features'))
            })
        feature_clusters_sorted = sorted(feature_clusters, key=lambda x: x.get('score'), reverse=True)
        feature_clusters_sorted_rank = []
        for rank, feature_cluster in enumerate(feature_clusters_sorted, 1):
            feature_cluster['rank'] = rank
            feature_clusters_sorted_rank.append(feature_cluster)
        return feature_clusters_sorted_rank

    def rank_gui_features(self, top_k_guis_idx: List[Text], query_feature: Text, sources=(FEAT_SOURCE_TEXT_BUTTON,
                                    FEAT_SOURCE_ICON_CLASSES)) -> Tuple[List[Dict], Dict]:
        k = len(top_k_guis_idx)
        features_ext = [
            {'gui_id': gui_index, 'ui_comp_id': feature.get('ui_comp_id'), 'comp_type': feature.get('comp_type'),
             'text': feature.get('text'), 'embedding': self.gui_feature_embedding(feature.get('text')),
             'bounds': feature.get('bounds')}
            for gui_index in top_k_guis_idx
            for feature in self.gui_feature_extraction(self.get_gui_doc(gui_index), sources)]
        feature_embeddings = np.array([feature.get("embedding") for feature in features_ext])
        cos_scores = self.compute_cos_similarity(query_feature, feature_embeddings)
        for feature, score in zip(features_ext, cos_scores):
            feature['score'] = float(score)
            feature.pop('embedding')
        features_unique = []
        feature_map = set()
        gui_scores = {}
        for feature in features_ext:
            if not feature.get('ui_comp_id') in feature_map:
                feature_map.add(feature.get('ui_comp_id'))
                features_unique.append(feature)
                if feature.get('gui_id') in gui_scores:
                    scores = gui_scores.get(feature.get('gui_id'))
                    gui_scores[feature.get('gui_id')] = scores + (feature.get('score'),)
                else:
                    gui_scores[feature.get('gui_id')] = (feature.get('score'),)
        features_sorted = sorted(features_unique, key=lambda x: x.get('score'), reverse=True)
        return features_sorted, gui_scores

    def rank_gui_features_precomputed(self, top_k_guis_idx: List[Text], query_feature: Text, sources=(FEAT_SOURCE_TEXT_BUTTON,
                                    FEAT_SOURCE_ICON_CLASSES)) -> Tuple[List[Dict], Dict]:
        k = len(top_k_guis_idx)
        features_ext = [
            {'gui_id': gui_index, 'ui_comp_id': feature.get('ui_comp_id'), 'comp_type': feature.get('comp_type'),
             'text': feature.get('text'), 'embedding': feature.get('embedding'),
             'bounds': feature.get('bounds')} for gui_index in top_k_guis_idx
            for feature in self.gui_feature_extraction_precomputed(gui_index, sources)]
        feature_embeddings = np.array([feature.get("embedding") for feature in features_ext])
        cos_scores = self.compute_cos_similarity(query_feature, feature_embeddings)
        for feature, score in zip(features_ext, cos_scores):
            feature['score'] = float(score)
            feature.pop('embedding')
        features_unique = []
        feature_map = set()
        gui_scores = {}
        for feature in features_ext:
            if not feature.get('ui_comp_id') in feature_map:
                feature_map.add(feature.get('ui_comp_id'))
                features_unique.append(feature)
                if feature.get('gui_id') in gui_scores:
                    scores = gui_scores.get(feature.get('gui_id'))
                    gui_scores[feature.get('gui_id')] = scores + (feature.get('score'),)
                else:
                    gui_scores[feature.get('gui_id')] = (feature.get('score'),)
        features_sorted = sorted(features_unique, key=lambda x: x.get('score'), reverse=True)
        return features_sorted, gui_scores


    def generate_feature_ranking_gpt(self, top_k_guis_idx: List[Text], query: Text, sources:
                Optional[Tuple]=(FEAT_SOURCE_TEXT_BUTTON, FEAT_SOURCE_ICON_CLASSES,),
                agg_method: Optional[Text] = AGG_GPT_FEAT_MEAN, threshold: Optional[float] = None,
                                     debug: Optional[bool] = True) -> List[Dict]:
        feature_results = []
        # Get the feature predictions from gpt
        feature_predictions = self.get_feature_predictions_gpt(query=query, debug=debug)
        # Obtain all features within the top-k GUIs to compare the feature predictions against and embed them
        features_ext = [
                {'gui_id': gui_index, 'ui_comp_id': feature.get('ui_comp_id'), 'comp_type': feature.get('comp_type'),
                 'text': feature.get('text'), 'embedding': self.gui_feature_embedding(feature.get('text')),
                 'bounds': feature.get('bounds')}
                for gui_index in top_k_guis_idx
                for feature in self.gui_feature_extraction(self.get_gui_doc(gui_index), sources)]
        feature_embeddings = np.array([feature.get("embedding") for feature in features_ext])
        # For each of the predicted features compute a feature score and feature object
        for predicted_feature in feature_predictions:
            # Compute cosine similarity of the predicted features to all top-k GUI features
            cos_scores = self.compute_cos_similarity(predicted_feature, feature_embeddings)
            # Feature list to collect all the features and scores
            scored_features = []
            for feature, score in zip(features_ext, cos_scores):
                curr_feature = feature.copy()
                curr_feature['score'] = float(score)
                curr_feature.pop('embedding')
                scored_features.append(curr_feature)
            # Compute only the unique features and the collect all the scores for one GUI
            features_unique = []
            feature_map = set()
            gui_scores = {}
            for feature in scored_features:
                if not feature.get('ui_comp_id') in feature_map:
                    feature_map.add(feature.get('ui_comp_id'))
                    features_unique.append(feature)
                    if feature.get('gui_id') in gui_scores:
                        scores = gui_scores.get(feature.get('gui_id'))
                        gui_scores[feature.get('gui_id')] = scores + (feature.get('score'),)
                    else:
                        gui_scores[feature.get('gui_id')] = (feature.get('score'),)
            features_sorted = sorted(features_unique, key=lambda x: x.get('score'), reverse=True)
            agg_gui_scores = self.compute_gui_ranking(gui_scores=gui_scores, agg_method=FeatureRanker.AGG_FEAT_MAX)
            ranked_feature_score = FeatureRanker.agg_gpt_feat_scores(
                                    scores=[score for gui_id, score in agg_gui_scores],
                                    agg_method=agg_method, threshold=threshold)
            feature_results.append({
                'gui_id': int(features_sorted[0].get('gui_id')),
                'feature_id': features_sorted[0].get('ui_comp_id'),
                'comp_text': features_sorted[0].get('text'),
                'text': predicted_feature,
                'comp_type': features_sorted[0].get('comp_type'),
                'bounds': features_sorted[0].get('bounds'),
                'gui_ranking': agg_gui_scores,
                'score': ranked_feature_score
            })
        feature_results_sorted = sorted(feature_results, key=lambda x: x.get('score'), reverse=True)
        return feature_results_sorted

    def generate_feature_ranking_gpt_precomputed(self, top_k_guis_idx: List[Text], query: Text, sources:
                Optional[Tuple]=(FEAT_SOURCE_TEXT_BUTTON, FEAT_SOURCE_ICON_CLASSES,),
                agg_method: Optional[Text] = AGG_GPT_FEAT_MEAN, threshold: Optional[float] = None,
                                     debug: Optional[bool] = True, prompt_template: Optional[Text] = None,
                                    gui_bounds_as_list : Optional[bool] = False,
                                    explanation : Optional[bool] = False) -> List[Dict]:
        feature_results = []
        # Get the feature predictions from gpt
        feature_predictions = self.get_feature_predictions_gpt(query=query, debug=debug, prompt_template=prompt_template)
        feature_expl_mapping = {}
        if explanation:
            feature_expl_mapping = self.feature_ranker_gpt_model.get_feature_explanations(query, feature_predictions)
        # Obtain all features within the top-k GUIs to compare the feature predictions against and embed them
        features_ext = [
            {'gui_id': gui_index, 'ui_comp_id': feature.get('ui_comp_id'), 'comp_type': feature.get('comp_type'),
             'text': feature.get('text'), 'embedding': feature.get('embedding'),
             'bounds': feature.get('bounds')} for gui_index in top_k_guis_idx
            for feature in self.gui_feature_extraction_precomputed(gui_index, sources)]
        feature_embeddings = np.array([feature.get("embedding") for feature in features_ext])
        # For each of the predicted features compute a feature score and feature object
        for predicted_feature in feature_predictions:
            # Compute cosine similarity of the predicted features to all top-k GUI features
            cos_scores = self.compute_cos_similarity(predicted_feature, feature_embeddings)
            # Feature list to collect all the features and scores
            scored_features = []
            for feature, score in zip(features_ext, cos_scores):
                curr_feature = feature.copy()
                curr_feature['score'] = float(score)
                curr_feature.pop('embedding')
                scored_features.append(curr_feature)
            # Compute only the unique features and the collect all the scores for one GUI
            features_unique = []
            feature_map = set()
            gui_scores = {}
            for feature in scored_features:
                if not feature.get('ui_comp_id') in feature_map:
                    feature_map.add(feature.get('ui_comp_id'))
                    features_unique.append(feature)
                    if feature.get('gui_id') in gui_scores:
                        scores = gui_scores.get(feature.get('gui_id'))
                        gui_scores[feature.get('gui_id')] = scores + (feature.get('score'),)
                    else:
                        gui_scores[feature.get('gui_id')] = (feature.get('score'),)
            features_sorted = sorted(features_unique, key=lambda x: x.get('score'), reverse=True)
            agg_gui_scores = self.compute_gui_ranking(gui_scores=gui_scores, agg_method=FeatureRanker.AGG_FEAT_MAX)
            ranked_feature_score = FeatureRanker.agg_gpt_feat_scores(
                                    scores=[score for gui_id, score in agg_gui_scores],
                                    agg_method=agg_method, threshold=threshold)
            if gui_bounds_as_list:
                feature_results.append({
                    'gui_id': [feat.get('gui_id' )for feat in features_sorted],
                    'feature_id': features_sorted[0].get('ui_comp_id'),
                    'comp_text': features_sorted[0].get('text'),
                    'text': predicted_feature,
                    'explanation': feature_expl_mapping.get(predicted_feature),
                    'comp_type': features_sorted[0].get('comp_type'),
                    'bounds': [feat.get('bounds' )for feat in features_sorted],
                    'gui_ranking': agg_gui_scores,
                    'score': ranked_feature_score
                })
            else:
                feature_results.append({
                    'gui_id': int(features_sorted[0].get('gui_id')),
                    'feature_id': features_sorted[0].get('ui_comp_id'),
                    'comp_text': features_sorted[0].get('text'),
                    'text': predicted_feature,
                    'explanation': feature_expl_mapping.get(predicted_feature),
                    'comp_type': features_sorted[0].get('comp_type'),
                    'bounds': features_sorted[0].get('bounds'),
                    'gui_ranking': agg_gui_scores,
                    'score': ranked_feature_score
                })
        feature_results_sorted = sorted(feature_results, key=lambda x: x.get('score'), reverse=True)
        return feature_results_sorted


    def generate_feature_recommendation_ranking_gpt_precomputed(self, top_k_guis_idx: List[Text], query: Text,
                                feature_queries : List[Dict], selected_gui: Text, sources:
                Optional[Tuple]=(FEAT_SOURCE_TEXT_BUTTON, FEAT_SOURCE_ICON_CLASSES,),
                agg_method: Optional[Text] = AGG_GPT_FEAT_MEAN, threshold: Optional[float] = None,
                                     debug: Optional[bool] = True, prompt_template: Optional[Text] = None,
                                    gui_bounds_as_list : Optional[bool] = False,
                                    explanation : Optional[bool] = False, top_k_features: Optional[int] = 1000,
                                    ) -> List[Dict]:
        feature_results = []
        # Get the feature predictions from gpt
        feature_predictions = self.get_feature_recommendations_predictions_gpt(query=query, feature_queries=feature_queries,
                                                    selected_gui=selected_gui,
                                                    debug=debug, prompt_template=prompt_template)
        if len(feature_predictions) == 0:
            return []
        feature_expl_mapping = {}
        if explanation:
            feature_expl_mapping = self.feature_ranker_gpt_model.get_feature_explanations(query, feature_predictions)
        # Obtain all features within the top-k GUIs to compare the feature predictions against and embed them
        features_ext = [
            {'gui_id': gui_index, 'ui_comp_id': feature.get('ui_comp_id'), 'comp_type': feature.get('comp_type'),
             'text': feature.get('text'), 'embedding': feature.get('embedding'),
             'bounds': feature.get('bounds')} for gui_index in top_k_guis_idx
            for feature in self.gui_feature_extraction_precomputed(gui_index, sources)]
        feature_embeddings = np.array([feature.get("embedding") for feature in features_ext])
        # For each of the predicted features compute a feature score and feature object
        for predicted_feature in feature_predictions:
            # Compute cosine similarity of the predicted features to all top-k GUI features
            cos_scores = self.compute_cos_similarity(predicted_feature, feature_embeddings)
            # Feature list to collect all the features and scores
            scored_features = []
            for feature, score in zip(features_ext, cos_scores):
                curr_feature = feature.copy()
                curr_feature['score'] = float(score)
                curr_feature.pop('embedding')
                scored_features.append(curr_feature)
            # Compute only the unique features and the collect all the scores for one GUI
            features_unique = []
            feature_map = set()
            gui_scores = {}
            for feature in scored_features:
                if not feature.get('ui_comp_id') in feature_map:
                    feature_map.add(feature.get('ui_comp_id'))
                    features_unique.append(feature)
                    if feature.get('gui_id') in gui_scores:
                        scores = gui_scores.get(feature.get('gui_id'))
                        gui_scores[feature.get('gui_id')] = scores + (feature.get('score'),)
                    else:
                        gui_scores[feature.get('gui_id')] = (feature.get('score'),)
            features_sorted = sorted(features_unique, key=lambda x: x.get('score'), reverse=True)
            agg_gui_scores = self.compute_gui_ranking(gui_scores=gui_scores, agg_method=FeatureRanker.AGG_FEAT_MAX)
            ranked_feature_score = FeatureRanker.agg_gpt_feat_scores(
                                    scores=[score for gui_id, score in agg_gui_scores],
                                    agg_method=agg_method, threshold=threshold)
            if gui_bounds_as_list:
                explanation = feature_expl_mapping.get(predicted_feature)
                explanation = explanation if explanation else ''
                feature_results.append({
                    'gui_id': [feat.get('gui_id' )for feat in features_sorted][:top_k_features],
                    'feature_id': [feat.get('ui_comp_id') for feat in features_sorted][:top_k_features],
                    'comp_text': features_sorted[0].get('text'),
                    'text': predicted_feature,
                    'explanation': explanation,
                    'comp_type': features_sorted[0].get('comp_type'),
                    'bounds': [feat.get('bounds' ) for feat in features_sorted][:top_k_features],
                    'gui_ranking': agg_gui_scores,
                    'score': ranked_feature_score
                })
            else:
                explanation = feature_expl_mapping.get(predicted_feature)
                explanation = explanation if explanation else ''
                feature_results.append({
                    'gui_id': int(features_sorted[0].get('gui_id')),
                    'feature_id': features_sorted[0].get('ui_comp_id'),
                    'comp_text': features_sorted[0].get('text'),
                    'text': predicted_feature,
                    'explanation': explanation,
                    'comp_type': features_sorted[0].get('comp_type'),
                    'bounds': features_sorted[0].get('bounds'),
                    'gui_ranking': agg_gui_scores,
                    'score': ranked_feature_score
                })
        feature_results_sorted = sorted(feature_results, key=lambda x: x.get('score'), reverse=True)
        return feature_results_sorted

    def agg_gpt_feat_scores(scores: List[float], agg_method: Text, threshold: Optional[float]) -> float:
        if agg_method == FeatureRanker.AGG_GPT_FEAT_MEAN:
            return float(np.mean([scores]))
        elif agg_method == FeatureRanker.AGG_GPT_FEAT_THRESHOLD:
            return float(np.sum(list(map(lambda x: 1 if x >= threshold else 0, scores))))

    def get_feature_predictions_gpt(self, query: Text, domain: Optional[Text] = None,
                                    debug: Optional[bool] = True, prompt_template: Optional[Text] = None) -> List[Text]:
        if debug:
            return ['remember me', 'username', 'register']
        else:
            return self.feature_ranker_gpt_model.get_top_feature_for_query(query=query, domain=domain, prompt_template=prompt_template)

    def get_feature_recommendations_predictions_gpt(self, query: Text, feature_queries: List[Dict], selected_gui: Text,
                                            domain: Optional[Text] = None,
                                    debug: Optional[bool] = True, prompt_template: Optional[Text] = None) -> List[Text]:
        if debug:
            return ['remember me', 'username', 'register']
        else:
            return self.feature_ranker_gpt_model.get_top_feature_recommendations_for_query(query=query,feature_queries=feature_queries,
                                                                    selected_gui=selected_gui,
                                                                    prompt_template=prompt_template)

    def compute_cos_similarity(self, query: Text, embeddings_matrix: np.array) -> List[float]:
        query_embedding = self.gui_feature_embedding(query)
        return list(np.array(util.pytorch_cos_sim(query_embedding, embeddings_matrix)[0]))

    def compute_feature_cluster_score(self, features):
        return len(features)

    def extract_feature_text(self, feature_texts):
        return feature_texts[0]

    def extract_feature_comp_type(self, feature_comp_types):
        return feature_comp_types[0]

    def get_gui_doc(self, gui_index):
        return self.all_guis[self.all_guis['id'] == int(gui_index)]['data'].values.tolist()[0]

    def get_gui_doc_precomputed(self, gui_index):
        return self.all_guis_embeds[self.all_guis_embeds['id'] == int(gui_index)]['data'].values.tolist()[0]

    def preprocess_gui_feature(self, feature_text):
        return feature_text.lower().strip()

    def gui_feature_embedding(self, feature_text):
        return self.model.encode([self.preprocess_gui_feature(feature_text)])[0]

    @staticmethod
    def camel_case_split(identifier):
        matches = re.finditer('.+?(?:(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])|$)', identifier)
        return [m.group(0) for m in matches]

    @staticmethod
    def snake_case_split(identifier):
        return identifier.split('_')

    @staticmethod
    def snake_camel_case_split(identifier):
        snake_cases = FeatureRanker.snake_case_split(identifier)
        splits = [cc for sc in snake_cases
                  for cc in FeatureRanker.camel_case_split(sc)]
        return splits

    @staticmethod
    def normalize_resource_id(resource_id, filter_tokens=None):
        stopwords = []
        name_split = resource_id.split('/')
        name = name_split[len(name_split) - 1]
        norm_name = [token for token in FeatureRanker.snake_camel_case_split(name) if token.lower() not in stopwords]
        return ' '.join(norm_name)

    @staticmethod
    def compute_ranking(top_k_guis_idx: List[Text], matches: List[Text], weight: float) \
            -> List[Tuple[Text, float]]:
        results = []
        for gui_id in top_k_guis_idx:
            results.append((gui_id, (weight if gui_id in matches else 0)))
        results = sorted(results, key=lambda x: x[1], reverse=True)
        return results

    @staticmethod
    def compute_gui_ranking(gui_scores: Dict[Text, List], agg_method: Optional[Text] = AGG_FEAT_MEAN) \
            -> List[Tuple[Text, float]]:
        results = []
        for gui_id, scores in gui_scores.items():
            if agg_method == FeatureRanker.AGG_FEAT_MEAN:
                results.append((gui_id, float(np.mean(scores))))
            elif agg_method == FeatureRanker.AGG_FEAT_MAX:
                results.append((gui_id, float(np.max(scores))))
            elif agg_method == FeatureRanker.AGG_FEAT_MIN:
                results.append((gui_id, float(np.min(scores))))
        results = sorted(results, key=lambda x: x[1], reverse=True)
        return results


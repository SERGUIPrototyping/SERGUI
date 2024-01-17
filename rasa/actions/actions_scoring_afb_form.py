import random
from typing import Any, Text, Dict, List, Tuple

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict

import os

from gui2r.feature_ranking.feature_ranker import FeatureRanker
from gui2r.preprocessing.extraction import Extractor
from gui2r.q_generator.q_generator import QGenerator
from gui2r.retrieval.configuration.conf import Configuration
from gui2r.retrieval.ranker.meta_ranker_v2 import MetaRanker
from gui2r.retrieval.retriever import Retriever

from rasa_sdk.forms import FormValidationAction
from rasa_sdk.events import EventType, SlotSet

from . import config
from .actions_utils import ranking_to_json, feature_ranking_to_json
from .interaction_tracking import session, FeatureRetrievalRelevanceAnnotation

abs_path_sergui = config.ABS_PATH_SERGUI
feature_ranker = FeatureRanker(abs_path_ui_data=abs_path_sergui+'all_guis/')
q_generator = QGenerator()


class ValidateScoringAFBForm(FormValidationAction):

    def name(self) -> Text:
        return "validate_scoring_afb_form"

    async def extract_scoring_afb_feature_query(
            self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> Dict[Text, Any]:
        text_of_last_user_message = tracker.latest_message.get("text")
        text_of_last_user_message = tracker.latest_message.get("text")
        if tracker.slots.get('requested_slot') == 'scoring_afb_feature_query' and \
            tracker.get_intent_of_latest_message() != 'intent_start' and \
            tracker.get_intent_of_latest_message() != 'gui_selected':
                return {"scoring_afb_feature_query": text_of_last_user_message}

    def validate_scoring_afb_feature_query(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        if slot_value:
            return {"scoring_afb_feature_query": slot_value}

    async def extract_scoring_afb_placeholder(
            self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> Dict[Text, Any]:
        text_of_last_user_message = tracker.latest_message.get("text")
        if tracker.slots.get('requested_slot') == 'scoring_afb_placeholder' and \
            tracker.get_intent_of_latest_message() != 'intent_start' and \
            tracker.get_intent_of_latest_message() != 'gui_selected':
                return {"scoring_afb_placeholder": tracker.get_intent_of_latest_message()}

    def validate_scoring_afb_placeholder(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        # Initialize the meta ranker
        scores = tracker.get_slot('scores')
        score_names = tracker.get_slot('score_names')
        meta_ranker = MetaRanker(scores=scores, score_names=score_names)
        curr_feature = tracker.get_slot('scoring_afb_curr_feature')
        feature_query = tracker.get_slot('scoring_afb_feature_query')
        curr_idx = tracker.get_slot('scoring_afb_curr_idx')
        collected_feature_descs = tracker.get_slot('collected_feature_descs')
        # We showed the top-k ranking of the GUIs containing the feature to the user and collect the feedback here
        if config.SCORING_AFB_SHOW_RANKING:
            gui_scores = tracker.get_slot('scoring_afb_gui_scores')
            aspect_guis = tracker.get_slot('aspect_guis')
            ranked_gui_features = tracker.get_slot('scoring_afb_ranked_gui_features')
            if slot_value == "select_feature":
                collected_feature_descs.append(feature_query)
                current_selected_gui_id = next(tracker.get_latest_entity_values('current_selected_gui_id'), None)
                sel_gui_id = str(current_selected_gui_id.split('_')[1])
                rank = next((i for i, rf in enumerate(ranked_gui_features, 0) if rf['gui_id'] == sel_gui_id), -1)
                if config.INTERACTION_DB_ENABLED:
                    curr_annotation_gui_id = tracker.get_slot('curr_annotation_gui_id')
                    simplified_ranked_gui_features = [{'ui_comp_id': feat['ui_comp_id'],
                                                       'text': feat['text'],
                                                       'score': feat['score'],
                                                       'rank': rank}
                                                      for rank, feat in enumerate(ranked_gui_features[:config.SCORING_AFB_TOP_K])]
                    if config.USER_STUDY_TASK_AND_GUI_ENABLED:
                        gui_uuid_mapping = tracker.get_slot('gui_uuid_mapping')
                        feat_rel_anno = FeatureRetrievalRelevanceAnnotation(user_id=tracker.sender_id,
                                                                   gui_id=curr_annotation_gui_id,
                                                                   task_number=gui_uuid_mapping[curr_annotation_gui_id][
                                                                       'task'],
                                                                   gui_number=gui_uuid_mapping[curr_annotation_gui_id][
                                                                       'gui'],
                                                                   nlr_query=tracker.get_slot(
                                                                       'scoring_nlr_placeholder'),
                                                                   feature_query=feature_query,
                                                                   ranking=simplified_ranked_gui_features,
                                                                   annotation=rank)
                        session.add(feat_rel_anno)
                        session.commit()
                    else:
                        feat_rel_anno = FeatureRetrievalRelevanceAnnotation(user_id=tracker.sender_id,
                                                                            gui_id=curr_annotation_gui_id,
                                                                            task_number=0,
                                                                            gui_number=0,
                                                                            nlr_query=tracker.get_slot(
                                                                                'scoring_nlr_placeholder'),
                                                                            feature_query=feature_query,
                                                                            ranking=simplified_ranked_gui_features,
                                                                            annotation=rank)
                        session.add(feat_rel_anno)
                        session.commit()
                # Compute the results for the feature and set the selected GUI score to 1
                gui_results = feature_ranker.compute_gui_ranking(gui_scores=gui_scores,
                                                                 agg_method=FeatureRanker.AGG_FEAT_MAX)
                gui_results = [(gui_id, ValidateScoringAFBForm.compute_ranking_from_relevance_feedback(rank, curr_rank, score))
                               for curr_rank, (gui_id, score) in enumerate(gui_results)]
                meta_ranker.add_results(gui_results, MetaRanker.SCORE_FFB_AFB_FEAT)
                ranking = meta_ranker.get_ranking(MetaRanker.AGG_MEAN)
                # Add to ranking history
                ranking_history = tracker.get_slot('ranking_history')
                curr_annotation_gui_id = tracker.get_slot('curr_annotation_gui_id')
                nlr_query = tracker.get_slot('scoring_nlr_placeholder')
                ranking_history[curr_annotation_gui_id].append({
                    'id': len(ranking_history[curr_annotation_gui_id])+1,
                    'name': 'AFB' + str(len(ranking_history[curr_annotation_gui_id])+1),
                    'query': nlr_query,
                    'ranking': [idd for idd, conf in meta_ranker.get_ranking()]})
                sel_feature = next((x for x in ranked_gui_features if str(x['gui_id']) == sel_gui_id), None)
                aspect_feature_gui = ValidateScoringAFBForm. \
                    create_aspect_feature_gui(sel_feature, gui_results, feature_query)
                aspect_guis.append(aspect_feature_gui)
                return {"scoring_afb_placeholder": True,
                        "scores": meta_ranker.get_scores(),
                        "score_names": meta_ranker.get_score_names(),
                        "aspect_guis": aspect_guis,
                        "collected_feature_descs": collected_feature_descs,
                        "ranking_history": ranking_history}
            elif slot_value == config.DIALOG_INTENT_CONFIRM:
                if config.INTERACTION_DB_ENABLED:
                    pass
                collected_feature_descs.append(feature_query)
                gui_results = feature_ranker.compute_gui_ranking(gui_scores=gui_scores,
                                                                 agg_method=FeatureRanker.AGG_FEAT_MAX)
                meta_ranker.add_results(gui_results, MetaRanker.SCORE_FFB_AFB_FEAT)
                ranking = meta_ranker.get_ranking(MetaRanker.AGG_MEAN)
                aspect_feature_gui = ValidateScoringAFBForm. \
                    create_aspect_feature_gui(curr_feature, gui_results, feature_query)
                aspect_guis.append(aspect_feature_gui)
                return {"scoring_afb_placeholder": True,
                        "scores": meta_ranker.get_scores(),
                        "score_names": meta_ranker.get_score_names(),
                        "aspect_guis": aspect_guis,
                        "collected_feature_descs": collected_feature_descs}
            elif slot_value == config.DIALOG_INTENT_DENY or slot_value == config.DIALOG_INTENT_DONTKNOW:
                dispatcher.utter_message('Sorry that we could not find a good match for your feature. However, the feature will be saved as a textual requirements in the prototype.')
                additional_requirements = tracker.get_slot('additional_textual_requirements')
                feature_query = tracker.get_slot('scoring_afb_feature_query')
                additional_requirements.append(feature_query)
                if config.INTERACTION_DB_ENABLED:
                    curr_annotation_gui_id = tracker.get_slot('curr_annotation_gui_id')
                    simplified_ranked_gui_features = [{'ui_comp_id': feat['ui_comp_id'],
                                                       'text': feat['text'],
                                                       'score': feat['score'],
                                                       'rank': rank}
                                                      for rank, feat in enumerate(ranked_gui_features[:config.SCORING_AFB_TOP_K])]
                    if config.USER_STUDY_TASK_AND_GUI_ENABLED:
                        gui_uuid_mapping = tracker.get_slot('gui_uuid_mapping')
                        feat_rel_anno = FeatureRetrievalRelevanceAnnotation(user_id=tracker.sender_id,
                                                                            gui_id=curr_annotation_gui_id,
                                                                            task_number=
                                                                            gui_uuid_mapping[curr_annotation_gui_id][
                                                                                'task'],
                                                                            gui_number=
                                                                            gui_uuid_mapping[curr_annotation_gui_id][
                                                                                'gui'],
                                                                            nlr_query=tracker.get_slot(
                                                                                'scoring_nlr_placeholder'),
                                                                            feature_query=feature_query,
                                                                            ranking=simplified_ranked_gui_features,
                                                                            annotation=-1)
                        session.add(feat_rel_anno)
                        session.commit()
                    else:
                        feat_rel_anno = FeatureRetrievalRelevanceAnnotation(user_id=tracker.sender_id,
                                                                            gui_id=curr_annotation_gui_id,
                                                                            task_number=0,
                                                                            gui_number=0,
                                                                            nlr_query=tracker.get_slot(
                                                                                'scoring_nlr_placeholder'),
                                                                            feature_query=feature_query,
                                                                            ranking=simplified_ranked_gui_features,
                                                                            annotation=-1)
                        session.add(feat_rel_anno)
                        session.commit()
                return {"scoring_afb_placeholder": True,
                        "additional_textual_requirements": additional_requirements}
        else:
            if slot_value == config.DIALOG_INTENT_CONFIRM:
                collected_feature_descs.append(curr_feature.get('text'))
                gui_scores = tracker.get_slot('scoring_afb_gui_scores')
                aspect_guis = tracker.get_slot('aspect_guis')
                # Add the current feature to the list of aspect guis
                if config.SCORING_AFB_RERANK_METHOD == FeatureRanker.RERANK_REL_ONLY:
                    gui_results = feature_ranker.compute_gui_ranking(gui_scores=gui_scores,
                                                                     agg_method=FeatureRanker.AGG_FEAT_MAX)
                    gui_results = [(gui_id, float(1)) if gui_id == curr_feature.get('gui_id') else (gui_id, float(0))
                                   for gui_id, score in gui_results]
                    meta_ranker.add_results(gui_results, MetaRanker.SCORE_FFB_AFB_FEAT)
                    ranking = meta_ranker.get_ranking(MetaRanker.AGG_MEAN)
                    aspect_feature_gui = ValidateScoringAFBForm.\
                        create_aspect_feature_gui(curr_feature, gui_results, feature_query)
                    aspect_guis.append(aspect_feature_gui)
                elif config.SCORING_AFB_RERANK_METHOD == FeatureRanker.RERANK_REL_ALL:
                    gui_results = feature_ranker.compute_gui_ranking(gui_scores=gui_scores,
                                                                     agg_method=FeatureRanker.AGG_FEAT_MAX)
                    nr_gui_idxs = tracker.get_slot('scoring_afb_nr_gui_idxs')
                    gui_results_trans = []
                    for gui_id, score in gui_results:
                        if gui_id == curr_feature.get('gui_id'): gui_results_trans.append((gui_id, float(1)))
                        elif gui_id in nr_gui_idxs: gui_results_trans.append((gui_id, float(0)))
                        else: gui_results_trans.append((gui_id, score))
                    aspect_feature_gui = ValidateScoringAFBForm.\
                        create_aspect_feature_gui(curr_feature, gui_results_trans, feature_query)
                    aspect_guis.append(aspect_feature_gui)
                    meta_ranker.add_results(gui_results_trans, MetaRanker.SCORE_FFB_AFB_FEAT)
                    ranking = meta_ranker.get_ranking(MetaRanker.AGG_MEAN)
                return {"scoring_afb_placeholder": True,
                        "scores": meta_ranker.get_scores(),
                        "score_names": meta_ranker.get_score_names(),
                        "aspect_guis": aspect_guis,
                        "collected_feature_descs": collected_feature_descs}
            elif slot_value == config.DIALOG_INTENT_DENY:
                if config.INTERACTION_DB_ENABLED:
                nr_gui_idxs = tracker.get_slot('scoring_afb_nr_gui_idxs')
                nr_gui_idxs = nr_gui_idxs + [curr_feature.get('gui_id')]
                curr_idx = tracker.get_slot('scoring_afb_curr_idx')
                if curr_idx >= config.SCORING_AFB_MAX_NR:
                    return {"scoring_afb_placeholder": True}
                curr_idx = curr_idx + 1
                return {"scoring_afb_placeholder": None,
                        "scoring_afb_curr_idx": curr_idx,
                        "scoring_afb_nr_gui_idxs": nr_gui_idxs}
            elif slot_value == config.DIALOG_INTENT_DONTKNOW:
                curr_idx = tracker.get_slot('scoring_afb_curr_idx')
                if curr_idx >= config.SCORING_AFB_MAX_NR:
                    return {"scoring_afb_placeholder": True}
                curr_idx = curr_idx + 1
                return {"scoring_afb_placeholder": None,
                        "scoring_afb_curr_idx": curr_idx}

    @staticmethod
    def compute_ranking_from_relevance_feedback(selected_rank, curr_rank, score):
        if curr_rank < selected_rank:
            return 0
        elif curr_rank == selected_rank:
            return 1
        return score

    @staticmethod
    def create_aspect_feature_gui(curr_feature: Dict, gui_ranking: List[Tuple[Text, float]],
                                  feature_query: Text) -> Dict:
        return {'aspect_type': 'afb', 'gui_id': curr_feature.get('gui_id'),
                'feature_id': curr_feature.get('ui_comp_id'),
                'text': curr_feature.get('text'),
                'comp_type': curr_feature.get('comp_type'),
                'bounds': curr_feature.get('bounds'),
                'score': curr_feature.get('score'),
                'feature_query': feature_query,
                'gui_ranking': gui_ranking}

    @staticmethod
    def create_feature_questions(ranked_features: List[Dict]) -> List[Dict]:
        return [{'feature': rf, 'question': q_generator.generate_question(rf.get('text')),
                'gui_id': rf.get('gui_id'), 'bounds': rf.get('bounds')}
                 for rf in ranked_features]

    @staticmethod
    def show_all_gui_features(ranked_gui_features: List[Dict]) -> None:
        for rf in ranked_gui_features[:100]:
            print('Feature Ranking - gui_id: {}, id: {}, score: {}, text: {}, comp-type: {}'.
                  format(rf.get('gui_id'), rf.get('ui_comp_id'), rf.get('score'), rf.get('text'),
                         rf.get('comp_type'), ))

class AskForScoringAFBPlaceholder(Action):
    def name(self) -> Text:
        return "action_ask_scoring_afb_placeholder"

    def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        # Get ranked gui features and initialize if empty
        ranked_gui_features = tracker.get_slot('scoring_afb_ranked_gui_features')
        gui_scores = tracker.get_slot('scoring_afb_gui_scores')
        if not ranked_gui_features:
            scores = tracker.get_slot('scores')
            score_names = tracker.get_slot('score_names')
            filter_gui_idxs = tracker.get_slot('filter_gui_idxs')
            meta_ranker = MetaRanker(scores=scores, score_names=score_names, filter_gui_idxs=filter_gui_idxs)
            feature_query = tracker.get_slot('scoring_afb_feature_query')
            ranking = meta_ranker.get_ranking()
            ranked_gui_features, gui_scores = feature_ranker. \
                rank_gui_features_precomputed(top_k_guis_idx=[gui_id for gui_id, score in ranking],
                    query_feature=feature_query, sources=config.SCORING_DFB_FEAT_SOURCES_LARGE)
            if config.DEBUG:
                ValidateScoringAFBForm.show_all_gui_features(ranked_gui_features=ranked_gui_features)
        if config.SCORING_AFB_SHOW_RANKING:
            quick_replies_message = {"payload": "quickReplies", "data": config.FQ_QUICK_REPLY_NR}
            dispatcher.utter_message(response="utter_ask_for_feature_relevance_top_k", json_message=quick_replies_message)
            data_message = {"payload": "dfb-top-k", "data": feature_ranking_to_json(ranked_gui_features[:config.SCORING_AFB_TOP_K])}
            dispatcher.utter_message(json_message=data_message)
            nr_gui_idxs = tracker.get_slot('scoring_afb_nr_gui_idxs')
            nr_gui_idxs = nr_gui_idxs if nr_gui_idxs else []
            return [SlotSet("scoring_afb_ranked_gui_features", ranked_gui_features),
                    SlotSet("scoring_afb_gui_scores", gui_scores),
                    SlotSet("scoring_afb_curr_feature", ranked_gui_features[0]),
                    SlotSet("scoring_afb_nr_gui_idxs", nr_gui_idxs)]
        else:
            curr_index = tracker.get_slot('scoring_afb_curr_idx')
            curr_feature = ranked_gui_features[curr_index]
            quick_replies_message = {"payload": "quickReplies", "data": config.FQ_QUICK_REPLY_RNR}
            dispatcher.utter_message(response="utter_ask_for_feature_relevance", json_message=quick_replies_message)
            data_message = {"payload": "dfb", "data": {"gui_id": curr_feature.get('gui_id'),
                                                        "bounds": curr_feature.get('bounds')}}
            dispatcher.utter_message(json_message=data_message)
            nr_gui_idxs = tracker.get_slot('scoring_afb_nr_gui_idxs')
            nr_gui_idxs = nr_gui_idxs if nr_gui_idxs else []
            return [SlotSet("scoring_afb_ranked_gui_features", ranked_gui_features),
                    SlotSet("scoring_afb_gui_scores", gui_scores),
                    SlotSet("scoring_afb_curr_feature", curr_feature),
                    SlotSet("scoring_afb_nr_gui_idxs", nr_gui_idxs)]


class ActionScoringAFBFormSubmit(Action):

     def name(self) -> Text:
         return "scoring_afb_form_submit"

     def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
         # Init meta ranker and compute current ranking
         scores = tracker.get_slot('scores')
         score_names = tracker.get_slot('score_names')
         filter_gui_idxs = tracker.get_slot('filter_gui_idxs')
         meta_ranker = MetaRanker(scores=scores, score_names=score_names, filter_gui_idxs=filter_gui_idxs)
         ranking = meta_ranker.get_ranking()
         # Create custom message with the gui ranking data
         message_data = {"payload": "gui-ranking", "data": ranking_to_json(ranking[:config.TOP_K_UI])}
         dispatcher.utter_message(text="Please take a look at the best GUIs matching your requirements so far.",
                                  json_message=message_data)
         quick_replies_message = {"payload": "quickReplies", "data": config.FQ_QUICK_REPLY_OPTIONS_SIMPLIFIED}
         dispatcher.utter_message(json_message=quick_replies_message)
         return []


class ActionScoringAFBResetForm(Action):

    def name(self) -> Text:
        return "scoring_afb_form_reset"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        print("ScoringAFBForm: Reset")
        return [SlotSet("scoring_afb_feature_query", None),
                SlotSet("scoring_afb_placeholder", None),
                SlotSet("scoring_afb_curr_idx", 0),
                SlotSet("scoring_afb_curr_feature", None),
                SlotSet("scoring_afb_ranked_gui_features", None),
                SlotSet("scoring_afb_gui_scores", None),
                SlotSet("scoring_afb_nr_gui_idxs", None)]
from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict

import os

from gui2r.feature_ranking.feature_ranker import FeatureRanker
from gui2r.preprocessing.extraction import Extractor
from gui2r.q_generator.q_generator import QGenerator
from gui2r.retrieval.app_ranker.app_ranker import AppNLRanker
from gui2r.retrieval.configuration.conf import Configuration
from gui2r.retrieval.context_ranker.domain_ranker import DomainRanker
from gui2r.retrieval.ranker.meta_ranker_v2 import MetaRanker
from gui2r.retrieval.ranker.ranker_v2 import Ranker
from gui2r.retrieval.retriever import Retriever
import uuid
from .actions_utils import ranking_to_json

import time

from rasa_sdk.forms import FormValidationAction
from rasa_sdk.events import EventType, SlotSet

from . import config
from .interaction_tracking import session

abs_path =config.ABS_PATH_GUI2R

vis_segments = [Extractor.DATA_ACTIVITY_NAME, Extractor.DATA_TEXT_VISIBLE, Extractor.DATA_RES_IDS_VISIBLE,
                Extractor.DATA_ICON_IDS]
vis_conf_full_new_filter = Configuration(path_guis=abs_path + 'combined/',
                                         path_dsls=abs_path + 'combined/',
                                         path_semantic=abs_path + 'semantic_annotations/',
                                         path_preproc_text=abs_path + 'preproc_text/',
                                         path_app_details=abs_path + 'app_details.csv',
                                         path_ui_details=abs_path + 'ui_details.csv',
                                         path_models=abs_path + 'models/new/',
                                         path_ui_comp_data=abs_path + '/ui_comps_text/all_ui_comps.csv',
                                         path_ui_comp_models=abs_path + '/models/ui_comps/',
                                         dir_name_prefix='new',
                                         filter_guis=True,
                                         text_segments_used=vis_segments)

retriever = Retriever(vis_conf_full_new_filter)
abs_path_sergui = config.ABS_PATH_SERGUI

class ValidateScoringNLRForm(FormValidationAction):

    def name(self) -> Text:
        return "validate_scoring_nlr_form"

    async def extract_scoring_nlr_placeholder(
            self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> Dict[Text, Any]:
        text_of_last_user_message = tracker.latest_message.get("text")
        if tracker.slots.get('requested_slot') == 'scoring_nlr_placeholder' and \
            text_of_last_user_message != '/intent_start' and \
            tracker.get_intent_of_latest_message() != 'gui_selected' and \
            tracker.get_intent_of_latest_message() != 'gui_selected_confirm' and \
            tracker.get_intent_of_latest_message() != 'gui_selected_cancel':
            return {"scoring_nlr_placeholder": text_of_last_user_message}

    def validate_scoring_nlr_placeholder(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        if slot_value:
            return {"scoring_nlr_placeholder": slot_value}

    async def extract_user_study_gui_number_placeholder(
            self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
        ) -> Dict[Text, Any]:
        if not config.USER_STUDY_TASK_AND_GUI_ENABLED:
            return {"user_study_gui_number_placeholder": True}
        text_of_last_user_message = tracker.latest_message.get("text")
        if tracker.slots.get('requested_slot') == 'user_study_gui_number_placeholder' and \
                text_of_last_user_message != '/intent_start' and tracker.get_intent_of_latest_message() == 'gui_number_selection':
            gui_number = next(tracker.get_latest_entity_values('gui_number'), None)
            return {"user_study_gui_number_placeholder": gui_number}

    def validate_user_study_gui_number_placeholder(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
        ) -> Dict[Text, Any]:
        return {"user_study_gui_number_placeholder": slot_value}


class ActionScoringNLRFormSubmit(Action):

    def name(self) -> Text:
        return "scoring_nlr_form_submit"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        nlr_query = tracker.get_slot('scoring_nlr_placeholder')
        curr_annotation_gui_id = str(uuid.uuid4())
        # Init ranking history if empty else
        ranking_history = tracker.get_slot('ranking_history')
        ranking_history = ranking_history if ranking_history else {}
        additional_requirements = []
        # 1. Ranker: SentenceBERT
        results = [(ranked_document.document.index, ranked_document.conf) for ranked_document in
                    retriever.rank(query=nlr_query, method=Ranker.R_SENTBERT,
                                    qe_method=config.RANKER_QE_METHOD, max_results=config.RANKER_TOP_K)]
        # Create new meta ranker and add the initial nlr query results
        meta_ranker = MetaRanker()
        meta_ranker.add_results(results, MetaRanker.SCORE_NLR_SENTBERT)
        ranking_history[curr_annotation_gui_id] = [{
                'id': 1,
                'name': 'NLR_SBERT',
                'query': nlr_query,
                'ranking': [idd for idd, conf in meta_ranker.get_ranking()]}]
        # 2. Ranker: SentenceBERT + S2W
        results = [(ranked_document.document.index, ranked_document.conf) for ranked_document in
                    retriever.rank(query=nlr_query, method=Ranker.R_S2W,
                                   qe_method=config.RANKER_QE_METHOD, max_results=config.RANKER_TOP_K)]

        meta_ranker_s2w = MetaRanker()
        meta_ranker_s2w.add_results(results, MetaRanker.SCORE_NLR_S2W)
        ranking_history[curr_annotation_gui_id].append({
            'id': len(ranking_history[curr_annotation_gui_id]) + 1,
            'name': 'NLR_S2W',
            'query': nlr_query,
            'ranking': [idd for idd, conf in meta_ranker_s2w.get_ranking()]})

        # 3. Create new meta ranker and add the initial nlr query results
        meta_ranker.add_results(results, MetaRanker.SCORE_NLR_S2W)
            # Init ranking history and add first ranking
        ranking_history[curr_annotation_gui_id].append({
                    'id': len(ranking_history[curr_annotation_gui_id]) + 1,
                   'name': 'NLR_SBERT_S2W',
                    'query': nlr_query,
                   'ranking': [idd for idd, conf in meta_ranker.get_ranking()]})    
        filter_gui_idxs = []
        aspect_guis = []
        if not config.FEATURE_RECOMMENDATION_ENABLED:
            ranking = meta_ranker.get_ranking()
            message_data = {"payload": "gui-ranking", "data": ranking_to_json(ranking[:config.TOP_K_UI])}
            dispatcher.utter_message(text="Please take a look at the best GUIs matching your requirements so far.",
                                     json_message=message_data)
            quick_replies_message = {"payload": "quickReplies", "data": config.FQ_QUICK_REPLY_OPTIONS_SIMPLIFIED}
            dispatcher.utter_message(json_message=quick_replies_message)
        gui_uuid_mapping = None
        if config.USER_STUDY_TASK_AND_GUI_ENABLED:
            gui_uuid_mapping = tracker.get_slot('gui_uuid_mapping')
            gui_uuid_mapping = gui_uuid_mapping if gui_uuid_mapping else {}
            user_study_task_placeholder = tracker.get_slot('user_study_task_placeholder')
            user_study_gui_number_placeholder = tracker.get_slot('user_study_gui_number_placeholder')
            gui_uuid_mapping[curr_annotation_gui_id] = {'task': user_study_task_placeholder,
                                                        'gui': user_study_gui_number_placeholder,
                                                        'query': nlr_query}
        return [SlotSet("scores", meta_ranker.get_scores()),
                SlotSet("score_names", meta_ranker.get_score_names()),
                SlotSet("filter_gui_idxs", filter_gui_idxs),
                SlotSet("aspect_guis", aspect_guis),
                SlotSet("collected_feature_descs", []),
                SlotSet("curr_annotation_gui_id", curr_annotation_gui_id),
                SlotSet("ranking_history", ranking_history),
                SlotSet("gui_uuid_mapping", gui_uuid_mapping),
                SlotSet('additional_textual_requirements', additional_requirements)]


class AskForUserStudyGUINumberPlaceholder(Action):
    def name(self) -> Text:
        return "action_ask_user_study_gui_number_placeholder"

    def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        quick_replies_message = {"payload": "quickReplies", "data": config.USER_STUDY_GUI_NUMBER_QUICK_REPLY}
        dispatcher.utter_message("<b>User Study Note:</b> Please select the <b><i>GUI number</i></b> you are working on now.", json_message=quick_replies_message)
        return [SlotSet('scoring_ctx_domain_ranking', [])]


class ActionScoringNLRResetForm(Action):

    def name(self) -> Text:
        return "scoring_nlr_form_reset"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        return [SlotSet("scoring_nlr_placeholder", None),
                SlotSet("user_study_gui_number_placeholder", None)]


class ActionMetaRankerScoresReset(Action):

    def name(self) -> Text:
        return "meta_ranker_scores_reset"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        return [SlotSet("scores", None),
                SlotSet("score_names", None),
                SlotSet("filter_gui_idxs", []),
                SlotSet("aspect_guis", []),
                SlotSet("curr_annotation_gui_id", None)]


class ActionAskScoringType(Action):

    def name(self) -> Text:
        return "ask_scoring_type"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[
            Dict[Text, Any]]:
        quick_replies_message = {"payload": "quickReplies", "data": config.FQ_QUICK_REPLY_OPTIONS_SIMPLIFIED}
        dispatcher.utter_message(json_message=quick_replies_message)
        return []
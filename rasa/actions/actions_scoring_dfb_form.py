import random
from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict
import copy
import os

from toolz import curry

from gui2r.feature_ranking.feature_ranker import FeatureRanker
from gui2r.preprocessing.extraction import Extractor
from gui2r.q_generator.q_generator import QGenerator
from gui2r.retrieval.configuration.conf import Configuration
from gui2r.retrieval.ranker.meta_ranker_v2 import MetaRanker
from gui2r.retrieval.retriever import Retriever

from rasa_sdk.forms import FormValidationAction
from rasa_sdk.events import EventType, SlotSet

from . import config
from .actions_utils import ranking_to_json, feature_ranking_to_json, feature_question_ranking_to_json
from .interaction_tracking import session, FeatureRecommendedRelevanceAnnotation

abs_path_sergui = config.ABS_PATH_SERGUI
feature_ranker = FeatureRanker(abs_path_ui_data=abs_path_sergui+'all_guis/')
q_generator = QGenerator()


class ValidateScoringDFBForm(FormValidationAction):

    def name(self) -> Text:
        return "validate_scoring_dfb_form"

    async def extract_scoring_dfb_placeholder(
            self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> Dict[Text, Any]:
        text_of_last_user_message = tracker.latest_message.get("text")
        if tracker.slots.get('requested_slot') == 'scoring_dfb_placeholder' and \
            text_of_last_user_message != '\intent_start' and \
            text_of_last_user_message != '\gui_selected':
                return {"scoring_dfb_placeholder": tracker.get_intent_of_latest_message()}
        current_selected_gui_id = next(tracker.get_latest_entity_values('current_selected_gui_id'))
        return {"curr_selected_gui_id": current_selected_gui_id}

    def validate_scoring_dfb_placeholder(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        scores = tracker.get_slot('scores')
        score_names = tracker.get_slot('score_names')
        meta_ranker = MetaRanker(scores=scores, score_names=score_names)
        if tracker.get_intent_of_latest_message() == 'okay':
            ranking = meta_ranker.get_ranking()
            message_data = {"payload": "gui-ranking", "data": ranking_to_json(ranking[:config.TOP_K_UI])}
            print(ranking)
            dispatcher.utter_message(text="Please take a look at the best GUIs matching your requirements so far.",
                                     json_message=message_data)
            quick_replies_message = {"payload": "quickReplies", "data": config.FQ_QUICK_REPLY_OPTIONS_SIMPLIFIED}
            dispatcher.utter_message(json_message=quick_replies_message)
            return {"scoring_dfb_placeholder": True,
                    "scoring_dfb_feature_questions": True,
                    "scoring_dfb_curr_feature_question": True,
                    "scoring_dfb_curr_idx": 0,
                    "scoring_dfb_iteration_idx": 0}
        if not slot_value:
            return {"scoring_dfb_placeholder": None}
        # Initialize the meta ranker
        curr_feature_question = tracker.get_slot('scoring_dfb_curr_feature_question')
        if config.FEATURE_RECOMMENDATION_METHOD == config.FEATURE_RECOMMENDATION_METHOD_TOP_DOWN:
            if (type(curr_feature_question) is bool):
                return {"scoring_dfb_placeholder": None}
            feature_annotation = None
            matching_annotation = -1
            selected_gui_id = None
            if slot_value == config.DIALOG_INTENT_CONFIRM or slot_value == "select_feature":
                if slot_value == config.DIALOG_INTENT_CONFIRM:
                    feature_annotation = 1
                    # User did not select specfic GUI hence we add it to the additional requirements
                    additional_requirements.append(curr_feature_question['feature'].get('text'))
                if slot_value == "select_feature":
                    feature_annotation = 1
                    # Append to aspect guis
                    current_selected_gui_id = next(tracker.get_latest_entity_values('current_selected_gui_id'), None)
                    if current_selected_gui_id:
                        sel_gui_id = str(current_selected_gui_id.split('_')[1])
                        selected_gui_id = sel_gui_id
                        feature_idx = curr_feature_question['feature']['gui_id'].index(str(sel_gui_id))
                        matching_annotation = feature_idx
                        aspect_feature_gui = ValidateScoringDFBForm. \
                            create_aspect_feature_gui_full(curr_feature_question, feature_idx)
                        aspect_guis.append(aspect_feature_gui)
                        gui_results = curr_feature_question['feature'].get('gui_ranking')
                        gui_results = [(gui_id, ValidateScoringDFBForm.compute_ranking_from_relevance_feedback(feature_idx, curr_rank, score))
                                       for curr_rank, (gui_id, score) in enumerate(gui_results)]
                        meta_ranker.add_results(gui_results, MetaRanker.SCORE_FFB_DFB_FEAT)
                        # Add to ranking history
                        curr_annotation_gui_id = tracker.get_slot('curr_annotation_gui_id')
                        nlr_query = tracker.get_slot('scoring_nlr_placeholder')
                        ranking_history[curr_annotation_gui_id].append({
                            'id': len(ranking_history[curr_annotation_gui_id]) + 1,
                            'name': 'DFB' + str(len(ranking_history[curr_annotation_gui_id]) + 1),
                            'query': nlr_query,
                            'ranking': [idd for idd, conf in meta_ranker.get_ranking()]})
            elif slot_value == config.DIALOG_INTENT_DENY:
                feature_annotation = 0
            elif slot_value == config.DIALOG_INTENT_DONTKNOW:
                feature_annotation = 0
            elif slot_value == 'already_specified':
                feature_annotation = 3
            if config.USER_STUDY_TASK_AND_GUI_ENABLED:
                curr_annotation_gui_id = tracker.get_slot('curr_annotation_gui_id')
                gui_uuid_mapping = tracker.get_slot('gui_uuid_mapping')
                ranking = [{'gui_id': elem[0],
                            'ui_comp_id': curr_feature_question.get('feature').get('feature_id')[idd],
                            'score': elem[1]}
                           for idd, elem in enumerate(curr_feature_question.get('feature').get('gui_ranking')[:config.SCORING_DFB_TOP_K_FEATURES])]
                feat_rel_anno = FeatureRecommendedRelevanceAnnotation(user_id=tracker.sender_id,
                                                           gui_id=curr_annotation_gui_id,
                                                           task_number=gui_uuid_mapping[curr_annotation_gui_id][
                                                               'task'],
                                                           gui_number=gui_uuid_mapping[curr_annotation_gui_id][
                                                               'gui'],
                                                           nlr_query=tracker.get_slot(
                                                               'scoring_nlr_placeholder'),
                                                           feature_text=curr_feature_question['feature'].get('text'),
                                                           feature_question=curr_feature_question.get('question'),
                                                           ranking=ranking,
                                                           selected_gui_id=selected_gui_id,
                                                           feature_annotation=feature_annotation,
                                                           matching_annotation=matching_annotation)
                session.add(feat_rel_anno)
                session.commit()
        # Update the current feature question to the next one
        curr_idx = tracker.get_slot('scoring_dfb_curr_idx')
        feature_questions = tracker.get_slot('scoring_dfb_feature_questions')
        iteration_idx = tracker.get_slot('scoring_dfb_iteration_idx')
        curr_idx = curr_idx + 1
        if iteration_idx >= min(config.SCORING_DFB_MAX_NUM_QUESTIONS-1, len(feature_questions)-1):
            if config.SCORING_DFB_RECOMPUTE:
                return {"scoring_dfb_placeholder": True,
                        "scores": meta_ranker.get_scores(),
                        "score_names": meta_ranker.get_score_names(),
                        "aspect_guis": aspect_guis,
                        "collected_feature_descs": collected_feature_descs,
                        "scoring_dfb_feature_questions": [],
                        "scoring_dfb_curr_idx": 0,
                        "ranking_history": ranking_history,
                        "additional_textual_requirements": additional_requirements}
            else:
                return {"scoring_dfb_placeholder": True,
                        "scores": meta_ranker.get_scores(),
                        "scoring_dfb_curr_idx": curr_idx,
                        "score_names": meta_ranker.get_score_names(),
                        "aspect_guis": aspect_guis,
                        "collected_feature_descs": collected_feature_descs,
                        "ranking_history": ranking_history,
                        "additional_textual_requirements": additional_requirements}
        iteration_idx = iteration_idx + 1
        curr_feature_question = feature_questions[curr_idx]
        return {"scoring_dfb_placeholder": None,
                "scoring_dfb_curr_feature_question": curr_feature_question,
                "scoring_dfb_curr_idx": curr_idx,
                "scoring_dfb_iteration_idx": iteration_idx,
                "scores": meta_ranker.get_scores(),
                "score_names": meta_ranker.get_score_names(),
                "aspect_guis": aspect_guis,
                "collected_feature_descs": collected_feature_descs,
                "ranking_history": ranking_history,
                "additional_textual_requirements": additional_requirements}

    @staticmethod
    def compute_ranking_from_relevance_feedback(selected_rank, curr_rank, score):
        if curr_rank < selected_rank:
            return 0
        elif curr_rank == selected_rank:
            return 1
        return score

    @staticmethod
    def create_aspect_feature_gui(curr_feature: Dict) -> Dict:
        return {'aspect_type': 'dfb', 'gui_id': curr_feature.get('gui_id'),
                'feature_id': curr_feature.get('feature_id'),
                'text': curr_feature.get('text'),
                'comp_type': curr_feature.get('comp_type'),
                'bounds': curr_feature.get('bounds'),
                'gui_idxs': curr_feature.get('gui_idxs')}

    @staticmethod
    def minify_feature_question_from_ranking(curr_feature: Dict, rank: int) -> Dict:
        return {'cluster_id': curr_feature.get('feature').get('cluster_id'),
                'gui_id': curr_feature.get('feature').get('gui_id')[rank],
                'feature_id': curr_feature.get('feature').get('feature_id')[rank],
                'text': curr_feature.get('feature').get('text')[rank],
                'comp_type': curr_feature.get('feature').get('comp_type')[rank],
                'bounds': curr_feature.get('feature').get('bounds')[rank],
                }

    @staticmethod
    def create_aspect_feature_gui_full(curr_feature: Dict, index: int) -> Dict:
        return {'aspect_type': 'llm-dfb', 'gui_id': curr_feature['feature'].get('gui_id')[index],
                'feature_id': curr_feature['feature'].get('feature_id')[index],
                'text': curr_feature['feature'].get('text'),
                'bounds': curr_feature['feature'].get('bounds')[index],
                'gui_idxs': curr_feature['feature'].get('gui_id'),
                'gui_ranking': curr_feature['feature'].get('gui_ranking')}

    @staticmethod
    def create_feature_questions(ranked_features: List[Dict]) -> List[Dict]:
        return [{'feature': rf, 'question': q_generator.generate_question(rf.get('text')),
                'gui_id': rf.get('gui_id'), 'bounds': rf.get('bounds')}
                 for rf in ranked_features]

    @staticmethod
    def create_feature_questions_full_ranking(ranked_features: List[Dict]) -> List[Dict]:
        return [{'feature': rf, 'question': q_generator.generate_question(random.choice(rf.get('text'))),
                'gui_id': rf.get('gui_id'), 'bounds': rf.get('bounds')}
                 for rf in ranked_features]

    @staticmethod
    def create_feature_questions_full_ranking_gpt(ranked_features: List[Dict]) -> List[Dict]:
            return [{'feature': rf, 'question': q_generator.generate_question_expl(rf.get('text'), rf.get('explanation')),
                     'gui_id': rf.get('gui_id'), 'bounds': rf.get('bounds')}
                    for rf in ranked_features]

    @staticmethod
    def show_all_feature_questions(feature_questions: List[Dict]) -> None:
        for fq in feature_questions:
            print('Feature Ranking - id: {}, score: {}, text: {}, comp-type: {}, question: {}'.
                  format(fq.get('feature').get('id'), fq.get('feature').get('score'),
                  fq.get('feature').get('text'), fq.get('feature').get('comp_type'), fq.get('question')))


class AskForScoringDFBPlaceholder(Action):
    def name(self) -> Text:
        return "action_ask_scoring_dfb_placeholder"

    def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        # Get feature questions and initialize if empty
        feature_questions = tracker.get_slot('scoring_dfb_feature_questions')
        collected_feature_descs = tracker.get_slot('collected_feature_descs')
        if not feature_questions or type(feature_questions) is bool:
            scores = tracker.get_slot('scores')
            score_names = tracker.get_slot('score_names')
            filter_gui_idxs = tracker.get_slot('filter_gui_idxs')
            meta_ranker = MetaRanker(scores=scores, score_names=score_names, filter_gui_idxs=filter_gui_idxs)
            nlr_query = tracker.get_slot('scoring_nlr_placeholder')
            ranking = meta_ranker.get_ranking()
            if config.FEATURE_RECOMMENDATION_METHOD == config.FEATURE_RECOMMENDATION_METHOD_TOP_DOWN:
                current_selected_gui_id = tracker.get_slot("curr_selected_gui_id")
                aspect_guis = tracker.get_slot("aspect_guis")
                ranked_features = feature_ranker.generate_feature_recommendation_ranking_gpt_precomputed(
                     top_k_guis_idx=[gui_id for gui_id, score in ranking[:config.FEATURE_RECOMMENDATION_TOP_k]],
                     query=nlr_query, feature_queries=[{'text': ag.get('text'),
                                                        'comp_type': ag.get('comp_type')}
                                                       for ag in aspect_guis],
                     selected_gui=current_selected_gui_id.split('_')[1],
                     sources=config.FEATURE_RECOMMENDATION_TOP_k_FEAT_SOURCES_LARGE,
                     debug=config.FEATURE_RECOMMENDATION_METHOD_DEBUG_GPT,
                     prompt_template=config.FEATURE_RECOMMENDATION_PROMPT_TEMPLATE,
                     gui_bounds_as_list=True,
                     explanation=True,
                     top_k_features=config.SCORING_DFB_TOP_K_FEATURES)
                if len(ranked_features)==0:
                    quick_replies_message = {"payload": "quickReplies", "data": config.FQ_QUICK_REPLY_OK}
                    dispatcher.utter_message(text='Sorry, something went wrong. Please try again.',
                                             json_message=quick_replies_message)
                    return []
                feature_questions = ValidateScoringDFBForm. \
                        create_feature_questions_full_ranking_gpt(ranked_features=ranked_features)
        curr_idx = tracker.get_slot('scoring_dfb_curr_idx')
        curr_feature_question = feature_questions[curr_idx]
        quick_replies_message = {"payload": "quickReplies", "data": config.FQ_QUICK_REPLY_RNR_SIMPLIFIED_PLUS}
        dispatcher.utter_message(text=curr_feature_question.get('question'), json_message=quick_replies_message)
        if config.SCORING_DFB_SHOW_RANKING:
            data_message = {"payload": "dfb-top-k", "data": feature_question_ranking_to_json(curr_feature_question,
                                                                            config.SCORING_DFB_TOP_K_FEATURES)}
        else:
            data_message = {"payload": "dfb", "data": {"gui_id": curr_feature_question.get('gui_id'),
                                                       "bounds": curr_feature_question.get('bounds')}}
        dispatcher.utter_message(json_message=data_message)
        return [SlotSet("scoring_dfb_feature_questions", feature_questions),
                SlotSet("scoring_dfb_curr_feature_question", curr_feature_question)]


class ActionScoringDFBFormSubmit(Action):

     def name(self) -> Text:
         return "scoring_dfb_form_submit"

     def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
         if tracker.get_intent_of_latest_message() == 'okay':
             return []
         # Init meta ranker and compute current ranking
         scores = tracker.get_slot('scores')
         score_names = tracker.get_slot('score_names')
         filter_gui_idxs = tracker.get_slot('filter_gui_idxs')
         meta_ranker = MetaRanker(scores=scores, score_names=score_names, filter_gui_idxs=filter_gui_idxs)
         ranking = meta_ranker.get_ranking()
         # Create custom message with the gui ranking data
         message_data = {"payload": "gui-ranking-reselect", "data": ranking_to_json(ranking[:config.TOP_K_UI])}
         dispatcher.utter_message(text="Based on the discussed requirements, we updated the GUI ranking for you. You can either select " + \
                                       "a new final GUI or keep your previous choice.",
                                  json_message=message_data)
         quick_replies_message = {"payload": "quickReplies", "data": config.FQ_QUICK_REPLY_OPTIONS_KEEP_GUI}
         dispatcher.utter_message(json_message=quick_replies_message)
         return []


class ActionScoringDFBResetForm(Action):

    def name(self) -> Text:
        return "scoring_dfb_form_reset"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        print("ScoringDFBForm: Reset")
        return [SlotSet("scoring_dfb_placeholder", None),
                SlotSet("scoring_dfb_feature_questions", None),
                SlotSet("scoring_dfb_curr_feature_question", None),
                SlotSet("scoring_dfb_curr_idx", 0),
                SlotSet("scoring_dfb_iteration_idx", 0)]


class ActionScoringDFBIterationResetForm(Action):

    def name(self) -> Text:
        return "scoring_dfb_form_iteration_reset"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        print("ScoringDFBForm: Reset")
        return [SlotSet("scoring_dfb_placeholder", None),
                SlotSet("scoring_dfb_iteration_idx", 0)]
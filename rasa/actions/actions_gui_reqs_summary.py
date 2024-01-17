
from typing import Any, Text, Dict, List

from rasa_sdk import Tracker, Action
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet

from . import config
from .interaction_tracking import session, GUIRankingAnnotation


class ActionGUIReqsSummary(Action):

    def name(self) -> Text:
        return "gui_reqs_summary"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
            if tracker.get_intent_of_latest_message() == 'keep_previous_gui':
                current_selected_gui_id = tracker.get_slot("curr_selected_gui_id")
            elif tracker.get_intent_of_latest_message() == 'gui_reselected':
                current_selected_gui_id = next(tracker.get_latest_entity_values('current_selected_gui_id'), None)
            else:
                current_selected_gui_id = tracker.get_slot("curr_selected_gui_id")
            nlr_query = tracker.get_slot('scoring_nlr_placeholder')
            aspect_guis = tracker.get_slot('aspect_guis')
            # Add rankings of selected gui to database
            curr_annotation_gui_id = tracker.get_slot('curr_annotation_gui_id')
            gui_uuid_mapping = tracker.get_slot('gui_uuid_mapping')
            ranking_history = tracker.get_slot('ranking_history')
            rankings_for_gui = ranking_history[curr_annotation_gui_id]
            # get inital gui id and its reranks
            sel_gui_id_initial = str(tracker.get_slot("curr_selected_gui_id").split('_')[1])
            rank_methods, ranks_initial = zip(*[(elem['name'],[new_elem for new_elem in elem['ranking']].index(str(sel_gui_id_initial))) 
                if sel_gui_id_initial in [new_elem for new_elem in elem['ranking']] else (elem['name'],-1)
                                                for elem in rankings_for_gui])
            # get reselect gui id and its reranks
            sel_gui_id_reselected = str(current_selected_gui_id.split('_')[1])
            for elem in rankings_for_gui:
                val = sel_gui_id_reselected in elem['ranking']
            rank_methods, ranks_reselected = zip(*[(elem['name'],[new_elem for new_elem in elem['ranking']].index(str(sel_gui_id_reselected))) 
                if sel_gui_id_reselected in [new_elem for new_elem in elem['ranking']] else (elem['name'],-1)
                                                   for elem in rankings_for_gui])
            if config.USER_STUDY_TASK_AND_GUI_ENABLED:
                feat_rel_anno = GUIRankingAnnotation(user_id=tracker.sender_id, gui_id=curr_annotation_gui_id,
                                                           task_number=gui_uuid_mapping[curr_annotation_gui_id]['task'],
                                                           gui_number=gui_uuid_mapping[curr_annotation_gui_id]['gui'],
                                                           nlr_query=tracker.get_slot('scoring_nlr_placeholder'),
                                                           selected_gui_id_initial=tracker.get_slot("curr_selected_gui_id"),
                                                           selected_gui_id_reselected=current_selected_gui_id,
                                                           rank_methods=rank_methods,
                                                           ranks_initial=ranks_initial,
                                                           ranks_reselected=ranks_reselected)
            else:
                feat_rel_anno = GUIRankingAnnotation(user_id=tracker.sender_id, gui_id=curr_annotation_gui_id,
                                                     task_number=0,
                                                     gui_number=0,
                                                     nlr_query=tracker.get_slot('scoring_nlr_placeholder'),
                                                     selected_gui_id_initial=tracker.get_slot("curr_selected_gui_id"),
                                                     selected_gui_id_reselected=current_selected_gui_id,
                                                     rank_methods=rank_methods,
                                                     ranks_initial=ranks_initial,
                                                     ranks_reselected=ranks_reselected)
            session.add(feat_rel_anno)
            session.commit()
            filtered_aspect_guis = []
            for aspect_gui in aspect_guis:
                if aspect_gui.get('aspect_type') == 'dfb' and aspect_gui.get('gui_idxs'):
                    if str(current_selected_gui_id.split('_')[1]) not in aspect_gui.get('gui_idxs'):
                        filtered_aspect_guis.append(aspect_gui)
                elif aspect_gui.get('aspect_type') == 'afb' or aspect_gui.get('aspect_type') == 'llm-dfb':
                    score_curr_gui = [gui_res[1] for gui_res in aspect_gui.get('gui_ranking')
                                      if gui_res[0] == str(current_selected_gui_id.split('_')[1])][0]
                    if score_curr_gui < config.REQ_SUMMARY_MIN_AFB_CONF:
                        filtered_aspect_guis.append(aspect_gui)
                else:
                    filtered_aspect_guis.append(aspect_gui)
            ctx_domain = tracker.get_slot('scoring_ctx_domain')
            ctx_app = tracker.get_slot('scoring_ctx_app_desc')
            additional_requirements = tracker.get_slot('additional_textual_requirements')
            req_summary = ActionGUIReqsSummary.create_gui_req_summary(current_selected_gui_id, nlr_query, ctx_domain, ctx_app, 
                filtered_aspect_guis, additional_requirements)
            message_data = {"payload": "gui-req-summary",
                            "data": req_summary}
            filtered_feature_text = [f.get('text') for f in filtered_aspect_guis]
            additional_requirements = tracker.get_slot('additional_textual_requirements')
            if len(additional_requirements) > 0:
                filtered_feature_text.extend(additional_requirements)
            filtered_features_text_merged = ', '.join(['"'+f+'"' for f in filtered_feature_text])
            summary = ""
            if config.REQ_SUMMARY_SHOW_UI:
                summary = "Here is the summary of your requirements for this GUI. In the selected GUI, features "
                summary = summary + filtered_features_text_merged + " are missing, but they have been noted down."
            else:
                summary = "Okay, the GUI has been added to the preview and all missing features in the selected GUI, "
                summary = summary + filtered_features_text_merged + " have been noted down."
            dispatcher.utter_message(text=summary,  json_message=message_data)
            return [SlotSet('curr_selected_gui_id', current_selected_gui_id.split('_')[1])]

    @staticmethod
    def create_gui_req_summary(gui_id: Text, nlr_query: Text, ctx_domain: Text, ctx_app: Text, aspect_guis: List[Dict],
                               additional_requirements: List[Text]) -> Dict:
        return {'selected_gui_id': gui_id.split('_')[1],
                'nlr_query': nlr_query,
                'ctx_domain': ctx_domain,
                'ctx_app': ctx_app,
                'additional_requirements': additional_requirements,
                'aspect_guis': [{
                    'aspect_type': ag.get('aspect_type'),
                    'gui_id': ag.get('gui_id'),
                    'feature_id': ag.get('feature_id'),
                    'text': ag.get('text'),
                    'comp_type': ag.get('comp_type'),
                    'bounds': ag.get('bounds'),
                    'feature_query': ag.get('feature_query')
                } for ag in aspect_guis]}


class ActionAskFinishedPrototype(Action):

    def name(self) -> Text:
        return "ask_finish_prototype"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[
            Dict[Text, Any]]:
        quick_replies_message = {"payload": "quickReplies", "data": config.FQ_QUICK_REPLY_FINISH}
        if config.SHOW_EXPLANATION_OF_SCORING and not tracker.get_slot('showed_explanation_editing'):
            dispatcher.utter_message(response='utter_explain_editing')
            dispatcher.utter_message(response="utter_ask_finish_prototype", json_message=quick_replies_message)
            return [SlotSet('showed_explanation_gfb', True)]
        curr_selected_gui_id = tracker.get_slot('curr_selected_gui_id')
        ranking_history = tracker.get_slot('ranking_history')
        curr_annotation_gui_id = tracker.get_slot('curr_annotation_gui_id')
        dispatcher.utter_message(response="utter_ask_finish_prototype", json_message=quick_replies_message)
        return []


class ActionFinishedUtterance(Action):

    def name(self) -> Text:
        return "finished_prototype"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[
            Dict[Text, Any]]:
        dispatcher.utter_message(response="utter_finished_prototype")
        return []


class ActionShowExplanationDFB(Action):

    def name(self) -> Text:
        return "show_explanation_dfb"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[
            Dict[Text, Any]]:
        print('explanation dfb')
        if config.SHOW_EXPLANATION_OF_SCORING and not tracker.get_slot('showed_explanation_dfb'):
            dispatcher.utter_message(response='utter_explain_dfb')
            return [SlotSet('showed_explanation_dfb', True)]
        return []

class ActionShowExplainShortWaitTime(Action):

    def name(self) -> Text:
        return "action_explain_short_wait_time"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[
            Dict[Text, Any]]:
        dispatcher.utter_message(response='explain_short_wait_time')
        return []


class ActionShowExplanationAFB(Action):

    def name(self) -> Text:
        return "show_explanation_afb"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[
            Dict[Text, Any]]:
        if config.SHOW_EXPLANATION_OF_SCORING and not tracker.get_slot('showed_explanation_afb'):
            dispatcher.utter_message(response='utter_explain_afb')
            return [SlotSet('showed_explanation_afb', True)]
        return []
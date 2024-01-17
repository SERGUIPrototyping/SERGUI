
from typing import Any, Text, Dict, List

from rasa_sdk import Tracker, Action
from rasa_sdk.events import EventType, SlotSet
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict

from rasa_sdk.forms import FormValidationAction

from gui2r.retrieval.context_ranker.domain_ranker import DomainRanker
from . import config

from gui2r.retrieval.ranker.meta_ranker_v2 import MetaRanker
from .interaction_tracking import session

abs_path_sergui = config.ABS_PATH_SERGUI


class ValidateUserStudyTaskForm(FormValidationAction):

    def name(self) -> Text:
        return "validate_user_study_task_form"

    async def extract_user_study_task_placeholder(
            self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> Dict[Text, Any]:
        if not config.USER_STUDY_TASK_AND_GUI_ENABLED:
            return {"user_study_task_placeholder": True}
        text_of_last_user_message = tracker.latest_message.get("text")
        if tracker.slots.get('requested_slot') == 'user_study_task_placeholder' and \
            text_of_last_user_message != '/intent_start' and tracker.get_intent_of_latest_message() == 'task_selection':
            task_id = next(tracker.get_latest_entity_values('task_id'), None)
            return {"user_study_task_placeholder": task_id}

    def validate_user_study_task_placeholder(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        return {"user_study_task_placeholder": slot_value}


class AskForUserStudyTaskPlaceholder(Action):
    def name(self) -> Text:
        return "action_ask_user_study_task_placeholder"

    def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        quick_replies_message = {"payload": "quickReplies", "data": config.USER_STUDY_TASK_QUICK_REPLY}
        print(quick_replies_message)
        dispatcher.utter_message("<b>User Study Note:</b> Please select the <b><i>task number</i></b> you are working on now.", json_message=quick_replies_message)
        return []
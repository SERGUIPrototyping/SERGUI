from gui2r.retrieval.ranker.ranker_v2 import Ranker
from gui2r.feature_ranking.feature_ranker import FeatureRanker
import os
from gui2r.feature_ranking.feature_ranker_gpt import FeatureRankerGPTModel

# General Configuration Settings
DEBUG = True
ABS_PATH_SERGUI = '/webapp/gui2rapp/staticfiles/resources/'
ABS_PATH_GUI2R = '/webapp/gui2rapp/staticfiles/resources/'

# GUI related configuration settings
TOP_K_UI = 100
SHOW_EXPLANATION_OF_SCORING = True
USER_STUDY_TASK_AND_GUI_ENABLED = False
USER_STUDY_TASK_QUICK_REPLY = [{"title": "1", "payload": '/task_selection{"task_id": "1"}'},
                               {"title": "2", "payload": '/task_selection{"task_id": "2"}'},
                               {"title": "3", "payload": '/task_selection{"task_id": "3"}'}]

USER_STUDY_GUI_NUMBER_QUICK_REPLY = [{"title": "1", "payload": '/gui_number_selection{"gui_number": "1"}'},
                                     {"title": "2", "payload": '/gui_number_selection{"gui_number": "2"}'},
                                     {"title": "3", "payload": '/gui_number_selection{"gui_number": "3"}'}]
                                  
# Dialog Configuration
DIALOG_INTENT_CONFIRM = 'confirm'
DIALOG_INTENT_DENY = 'deny'
DIALOG_INTENT_DONTKNOW = 'dontknow'

# GUI nlr-based reanking methods configuration
RANKER_TOP_K = 1000

# Feature Question Generation Configuration
SCORING_DFB_FEATURE_SCORE_WEIGHT = 1
SCORING_DFB_CUTOFF_QUESTIONS = 70
SCORING_DFB_MAX_NUM_QUESTIONS = 10
SCORING_DFB_TOP_K = 100
SCORING_DFB_TOP_K_FEATURES = 15
SCORING_DFB_FILTER_FEAT_THRESHOLD = 0.7
SCORING_DFB_SHOW_RANKING = True
SCORING_DFB_FEAT_SOURCES_SMALL = [FeatureRanker.FEAT_SOURCE_TEXT_BUTTON, FeatureRanker.FEAT_SOURCE_ICON_CLASSES,
                         FeatureRanker.FEAT_SOURCE_BUTTON_CLASS]
SCORING_DFB_FEAT_SOURCES_LARGE = [FeatureRanker.FEAT_SOURCE_TEXT_BUTTON, FeatureRanker.FEAT_SOURCE_ICON_CLASSES,
                         FeatureRanker.FEAT_SOURCE_BUTTON_CLASS, FeatureRanker.FEAT_SOURCE_INPUT_TEXT,
                         FeatureRanker.FEAT_SOURCE_RESOURCE_IDS, FeatureRanker.FEAT_SOURCE_TEXT_LABELS]

# AFB method related configuration
SCORING_AFB_RERANK_METHOD = FeatureRanker.RERANK_REL_ALL
SCORING_AFB_SHOW_RANKING = True
SCORING_AFB_TOP_K = 15

FEATURE_RECOMMENDATION_TOP_k = 300
FEATURE_RECOMMENDATION_TOP_k_FEAT_SOURCES_SMALL = [FeatureRanker.FEAT_SOURCE_TEXT_BUTTON, FeatureRanker.FEAT_SOURCE_ICON_CLASSES,
                         FeatureRanker.FEAT_SOURCE_BUTTON_CLASS]
FEATURE_RECOMMENDATION_TOP_k_FEAT_SOURCES_LARGE = [FeatureRanker.FEAT_SOURCE_TEXT_BUTTON, FeatureRanker.FEAT_SOURCE_ICON_CLASSES,
                         FeatureRanker.FEAT_SOURCE_BUTTON_CLASS, FeatureRanker.FEAT_SOURCE_INPUT_TEXT,
                         FeatureRanker.FEAT_SOURCE_RESOURCE_IDS, FeatureRanker.FEAT_SOURCE_TEXT_LABELS]
FEATURE_RECOMMENDATION_CUTOFF_N = 20
FEATURE_RECOMMENDATION_FILTER_FEAT_THRESHOLD = 0.7
FEATURE_RECOMMENDATION_FULL_CLUSTER = False
FEATURE_RECOMMENDATION_R = 'R'
FEATURE_RECOMMENDATION_NR = 'NR'
FEATURE_RECOMMENDATION_RERANK = True
FEATURE_RECOMMENDATION_FEATURE_SCORE_WEIGHT = 1
FEATURE_RECOMMENDATION_METHOD_TOP_DOWN = 'top-down'
FEATURE_RECOMMENDATION_METHOD = FEATURE_RECOMMENDATION_METHOD_TOP_DOWN
FEATURE_RECOMMENDATION_METHOD_DEBUG_GPT = False
FEATURE_RECOMMENDATION_ENABLED = False
FEATURE_RECOMMENDATION_PROMPT_TEMPLATE = FeatureRankerGPTModel.PROMPT_TEMPLATE_RECOMMENDATIONS_FS_NEW_ADD_INSTR_PLUS_EXAMPLE_NEWEST

# Requirements summary configuration
REQ_SUMMARY_MIN_AFB_CONF = 0.85
REQ_SUMMARY_SHOW_UI = True

# Feature Question Frontend Configuration
FQ_QUICK_REPLY_RNR = [{"title": "Yes", "payload": "/confirm"}, {"title": "No", "payload": "/deny"},
        {"title": "Don't Know", "payload": "/dontknow"}]
FQ_QUICK_REPLY_RNR_SIMPLIFIED = [{"title": "Yes", "payload": "/confirm"}, {"title": "No", "payload": "/deny"}]
FQ_QUICK_REPLY_RNR_SIMPLIFIED_PLUS = [{"title": "Yes", "payload": "/confirm"}, {"title": "No", "payload": "/deny"}, {"title": "Already specified", "payload": "/already_specified"}]
FQ_QUICK_REPLY_NR = [{"title": "Not relevant", "payload": "/deny"}]
FQ_QUICK_REPLY_OK = [{"title": "Okay", "payload": "/okay"}]
FQ_QUICK_REPLY_OPTIONS_SIMPLIFIED = [{"title": "Search feature", "payload": "/activate_afb"},
                  {"title": "Start new GUI", "payload": "/restart_gui"}]
FQ_QUICK_REPLY_OPTIONS_KEEP_GUI = [{"title": "Keep previous GUI", "payload": "/keep_previous_gui"}]
FQ_QUICK_REPLY_FINISH= [{"title": "Start new GUI", "payload": "/restart_gui"}, {"title": "Finish Prototype", "payload": "/finish_prototype"}]
FQ_QUICK_FINSIH_GFB_FEEDBACK= [{"title": "Finish feedback", "payload": "/finish_gfb_feedback"}]

# Configuration for interactions database
INTERACTION_DB_ENABLED = True
INTERACTION_DB_USER = ''
INTERACTION_DB_PW = ''
INTERACTION_DB_HOST = 'localhost'
INTERACTION_DB_PORT = '3306'
INTERACTION_DB_NAME = 'interaction_tracking'

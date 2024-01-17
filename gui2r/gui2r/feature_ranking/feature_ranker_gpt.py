import ast
from typing import Text, List, Optional, Dict, Tuple
import openai

from gui2r.feature_ranking.gui_2_str import GUI2Str


class FeatureRankerGPTModel():

    PLACEHOLDER_NLR_QUERY = 'placeholder_nlr_query'
    PLACEHOLDER_DOMAIN = 'placeholder_domain'
    PLACEHOLDER_FEATURES = 'placeholder_features'
    PLACEHOLDER_SELECTED_GUI = 'placeholder_selected_gui'


    PROMPT_TEMPLATE_FEATURE_EXPL = '''You are given a user interface description of a mobile app and a list of short user interface feature descriptions that may be contained in the user interface. Your task is to write a explanation of each feature and return it as a dictionary mapping the original description to your explanation.

user interface description: "login"
user interface features:

- login
- username 
- password 
- authentication 
- credentials 
- log in 
- remember me
- forgot password
- security warning 
- captcha 
- password strength indicator
- facebook
- social media
- terms & conditions
- create new account
- twitter
- google 
- e-Mail
- privacy and legal statements
- logo

result:
{
  "login": "This feature allows users to enter their credentials (username and password) to gain access to their account.",
  "username": "This feature is where users can enter their unique username, which is used to identify their account.",
  "password": "This feature is where users can enter their password, which is used to secure their account.",
  "authentication": "This feature verifies the user's identity and ensures they are authorized to access the account.",
  "credentials": "This feature refers to the combination of a username and password required for authentication and account access.",
  "log in": "This feature allows users to submit their entered username and password for authentication and account access.",
  "remember me": "This feature gives users the option to remember their login credentials, so they don't have to enter them every time they access the app.",
  "forgot password": "This feature provides a way for users to reset their password if they forget it, usually by sending an email with a password reset link.",
  "security warning": "This feature displays a warning message to users when there is a potential security risk or suspicious activity detected.",
  "captcha": "This feature is a security measure that requires users to complete a visual or audio challenge to prove they are human, typically to prevent automated bot attacks.",
  "password Strength Indicator": "This feature visually indicates the strength of the entered password, usually displayed as a progress bar or color-coded scale.",
  "facebook": "This feature allows users to log in or sign up using their Facebook account credentials.",
  "social media": "This feature refers to integration with various social media platforms, such as Facebook, Twitter, or Google, allowing users to share content or login with their social media accounts.",
  "terms & conditions": "This feature provides a link or access to the terms and conditions document that outlines the rules, guidelines, and privacy policies governing the use of the app.",
  "create new account": "This feature allows users to create a new account with their desired set of login credentials.",
  "twitter": "This feature allows users to log in or sign up using their Twitter account credentials.",
  "google": "This feature allows users to log in or sign up using their Google account credentials.",
  "e-Mail": "This feature refers to using an email address as part of the login or registration process.",
  "privacy and legal statements": "This feature provides access to the app's privacy policy and legal statements, which inform users about how their data is collected, used, and protected.",
  "logo": "This feature displays the app's logo, providing a visual representation that helps users identify the app."
}

You are given a user interface description of a mobile app and a list of short user interface feature descriptions that may be contained in the user interface. Your task is to write a explanation of each feature and return it as a dictionary mapping the original description to your explanation.

user interface description: "placeholder_nlr_query"
user interface features:

placeholder_features

result:'''

    PROMPT_TEMPLATE_RECOMMENDATIONS = '''You are given a short description of graphical user interface of a mobile app, an user interface that the has already been selected (as a list of ui components) and a list of features the user already selected.
Your task is to recommend the top 10 additional features (as keywords) that are relevant for the user. The result should be in the format of a python list of strings.

user interface description: "placeholder_nlr_query"

already selected user interface: 
placeholder_selected_gui

already found features: 
placeholder_features

recommended features:'''

    PROMPT_TEMPLATE_RECOMMENDATIONS_FS = '''You are given a short description of graphical user interface of a mobile app, an user interface that the has already been selected (as a list of ui components) and a list of features the user already selected.
Your task is to recommend the top 20 additional user interface features (as keywords) that are relevant for the user. A features should be a single user interface component. The result should be in the format of a python list of strings.

user interface description: "login"

already selected user interface: 
- Layout
	- (Image)
- Layout
	- "" (Text Input) (login username edit)
- Layout
	- "Humana Password" (Text Input) (login password edit)
- Layout
	- "Remember my username" (Button) (login remember username switch)
- Layout
	- "login" (Button) (login)
- Layout
	- "Forgot" (Label)
	- "USERNAME" (Button) (login recover username)
	- "or" (Label)
	- "PASSWORD" (Button) (login recover password)
	- "?" (Label)
- Layout
	- "register" (Button) (login register)


already found features: 
- facebook (button)
- remember me (checkbox)

recommended features:["google", "twitter", "logo", "password strength", "privacy and legal statements", "skip", "terms & conditions"]

You are given a short description of graphical user interface of a mobile app, an user interface that the has already been selected (as a list of ui components) and a list of features the user already selected.
Your task is to recommend the top 20 additional features (as keywords) that are relevant for the user. The result should be in the format of a python list of strings.

user interface description: "placeholder_nlr_query"

already selected user interface: 
placeholder_selected_gui

already found features: 
placeholder_features

recommended features:'''

    PROMPT_TEMPLATE_RECOMMENDATIONS_FS_NEW = '''You are given a short description of graphical user interface of a mobile app, an user interface that the has already been selected (as a list of ui components) and a list of features the user already selected.
    Your task is to recommend the top 30 additional user interface features (as keywords) that are relevant for the user. A features should be a single user interface component. The result should be in the format of a python list of strings.

    user interface description: "login"

    already selected user interface: 
    - Layout
    	- (Image)
    - Layout
    	- "" (Text Input) (login username edit)
    - Layout
    	- "Humana Password" (Text Input) (login password edit)
    - Layout
    	- "Remember my username" (Button) (login remember username switch)
    - Layout
    	- "login" (Button) (login)
    - Layout
    	- "Forgot" (Label)
    	- "USERNAME" (Button) (login recover username)
    	- "or" (Label)
    	- "PASSWORD" (Button) (login recover password)
    	- "?" (Label)
    - Layout
    	- "register" (Button) (login register)


    already found features: 
    - facebook (button)
    - remember me (checkbox)

    recommended features:["google", "twitter", "logo", "password strength", "privacy and legal statements", "skip", "terms & conditions"]

    You are given a short description of graphical user interface of a mobile app, an user interface that the has already been selected (as a list of ui components) and a list of features the user already selected.
    Your task is to recommend the top 30 additional features (as keywords) that are relevant for the user. The result should be in the format of a python list of strings.

    user interface description: "placeholder_nlr_query"

    already selected user interface: 
    placeholder_selected_gui

    already found features: 
    placeholder_features

    recommended features:'''

    PROMPT_TEMPLATE_RECOMMENDATIONS_FS_NEW_ADD_INSTR = '''You are given a short description of graphical user interface of a mobile app, an user interface that the has already been selected (as a list of ui components) and a list of features the user already selected.
    Your task is to recommend the top 30 additional user interface features (as keywords) that are relevant for the user. Please thorougly check the features contained in the already selected user interface and the already found features to avoid repeating features in your recommendation. 
    For your feature recommendations, focus on the specific user interface given to you and do not recommend features that are too general to the entire app (e.g. FAQs, customer support or help). A features should be a single user interface component. The result should be in the format of a python list of strings.

    user interface description: "login"

    already selected user interface:
    - Layout
        - (Image)
    - Layout
        - "" (Text Input) (login username edit)
    - Layout
        - "Humana Password" (Text Input) (login password edit)
    - Layout
        - "Remember my username" (Button) (login remember username switch)
    - Layout
        - "login" (Button) (login)
    - Layout
        - "Forgot" (Label)
        - "USERNAME" (Button) (login recover username)
        - "or" (Label)
        - "PASSWORD" (Button) (login recover password)
        - "?" (Label)
    - Layout
        - "register" (Button) (login register)


    already found features:
    - facebook (button)
    - remember me (checkbox)

    recommended features:["google", "twitter", "logo", "password strength", "privacy and legal statements", "skip", "terms & conditions"]

You are given a short description of graphical user interface of a mobile app, an user interface that the has already been selected (as a list of ui components) and a list of features the user already selected.
    Your task is to recommend the top 30 additional user interface features (as keywords) that are relevant for the user. Please thorougly check the features contained in the already selected user interface and the already found features to avoid repeating features in your recommendation. 
    For your feature recommendations, focus on the specific user interface given to you and do not recommend features that are too general to the entire app (e.g. FAQs, customer support or help). A features should be a single user interface component. The result should be in the format of a python list of strings.
    
    user interface description: "placeholder_nlr_query"

    already selected user interface: 
    placeholder_selected_gui

    already found features: 
    placeholder_features

    recommended features:'''

    PROMPT_TEMPLATE_RECOMMENDATIONS_FS_NEW_ADD_INSTR_PLUS_EXAMPLE = '''You are given a short description of graphical user interface of a mobile app, an user interface that the has already been selected (as a list of ui components) and a list of features the user already selected.
    Your task is to recommend the top 30 additional user interface features (as keywords) that are relevant for the user. Please thorougly check the features contained in the already selected user interface and the already found features to avoid repeating features in your recommendation. 
    For your feature recommendations, focus on the specific user interface given to you and do not recommend features that are too general to the entire app (e.g. FAQs, customer support or help). A features should be a single user interface component. The result should be in the format of a python list of strings.

    user interface description: "login"

    already selected user interface:
    - Layout
        - (Image)
    - Layout
        - "" (Text Input) (login username edit)
    - Layout
        - "Humana Password" (Text Input) (login password edit)
    - Layout
        - "Remember my username" (Button) (login remember username switch)
    - Layout
        - "login" (Button) (login)
    - Layout
        - "Forgot" (Label)
        - "USERNAME" (Button) (login recover username)
        - "or" (Label)
        - "PASSWORD" (Button) (login recover password)
        - "?" (Label)
    - Layout
        - "register" (Button) (login register)


    already found features:
    - facebook (button)
    - remember me (checkbox)

    recommended features:["google", "twitter", "logo", "password strength", "privacy and legal statements", "skip", "terms & conditions"]

You are given a short description of graphical user interface of a mobile app, an user interface that the has already been selected (as a list of ui components) and a list of features the user already selected.
    Your task is to recommend the top 30 additional user interface features (as keywords) that are relevant for the user. Please thorougly check the features contained in the already selected user interface and the already found features to avoid repeating features in your recommendation.
    For your feature recommendations, focus on the specific user interface given to you and do not recommend features that are too general to the entire app (e.g. FAQs, customer support or help). A features should be a single user interface component. The result should be in the format of a python list of strings.

    user interface description: "music player with list of songs"

    already selected user interface:
    - Layout
        - "close" (Icon) (switch)
        - "Queue" (Button) (playlist Info)
        - "more" (Icon) (ics)
    - Layout
        - (Image)
    - Layout
        - (Image) (art list)
    - List Item
        - "1." (Label) (number)
        - "2017_01_18 07:02" (Label) (title)
        - "0:05" (Label) (duration)
        - "NRJ Hits 128mp3" (Label) (artist)
        - (Image) (rating)
    - List Item
        - "2." (Label) (number)
        - "AstonMartinDBS" (Label) (title)
        - "0:03" (Label) (duration)
        - (Image) (rating)
    - List Item
        - "3." (Label) (number)
        - "Dont Give Up (Anthem) (Prod. Sinima Beats)" (Label) (title)
        - "4:43" (Label) (duration)
        - "Ms. White" (Label) (artist)
        - (Image) (rating)
    - List Item
        - "4." (Label) (number)
        - "newAccompaniment" (Label) (title)
        - "0:33" (Label) (duration)
        - "<unknown>" (Label) (artist)
        - (Image) (rating)
    - List Item
        - "5." (Label) (number)
        - "voice" (Label) (title)
        - "0:33" (Label) (duration)
        - "<unknown>" (Label) (artist)
        - (Image) (rating)
    - Layout
        - "repeat" (Icon) (repeat)
        - (Image) (shuffle)
        - "av rewind" (Icon) (previous)
        - (Image) (play)
        - "skip next" (Icon) (next)
        - "1:49" (Button) (current time)
        - "4:43" (Label) (total time)
    - Layout
        - "more" (Icon) (add)
        - "more" (Icon) (del)
        - (Image) (playlists)
        - "sliders" (Icon) (equalizer)


    already found features:
     - "share" (Icon) (share song ic)

    recommended features:["volume control", "search bar", "song thumbnail", "download button", "like", "add to playlist", "song lyrics", "artist info", "album info", "genre tag", "play speed control", "audio quality option", "offline mode", "cast button", "radio mode", "podcast mode", "personalized recommendations", "new releases", "trending songs", "user profile", "notifications", "music categories", "song comments", "song reviews", "music visualizer", "history", "queue list"]

You are given a short description of graphical user interface of a mobile app, an user interface that the has already been selected (as a list of ui components) and a list of features the user already selected.
    Your task is to recommend the top 30 additional user interface features (as keywords) that are relevant for the user. Please thorougly check the features contained in the already selected user interface and the already found features to avoid repeating features in your recommendation. 
    For your feature recommendations, focus on the specific user interface given to you and do not recommend features that are too general to the entire app (e.g. FAQs, customer support or help). A features should be a single user interface component. The result should be in the format of a python list of strings.    
    
    user interface description: "placeholder_nlr_query"

    already selected user interface: 
    placeholder_selected_gui

    already found features: 
    placeholder_features

    recommended features:'''

    PROMPT_TEMPLATE_RECOMMENDATIONS_FS_NEW_ADD_INSTR_PLUS_EXAMPLE_NEWEST='''You are given a short description of graphical user interface of a mobile app, an user interface that the has already been selected (as a list of ui components) and a list of features the user already selected.
    Your task is to recommend the top 30 additional user interface features (as keywords) that are relevant for the user. Please thorougly check the features contained in the already selected user interface and the already found features to avoid repeating features in your recommendation.
    For your feature recommendations, focus on the specific user interface given to you and do not recommend features that are too general to the entire app (e.g. FAQs, customer support or help). A features should be a single user interface component. The result should be in the format of a python list of strings. 
    Make the feature descriptions as general as possible (e.g. instead of "report comment" just "report" or instead of "product ratings" just "ratings"). If possible use only a single word to name the feature.

    user interface description: "login"

    already selected user interface:
    - Layout
        - (Image)
    - Layout
        - "" (Text Input) (login username edit)
    - Layout
        - "Humana Password" (Text Input) (login password edit)
    - Layout
        - "Remember my username" (Button) (login remember username switch)
    - Layout
        - "login" (Button) (login)
    - Layout
        - "Forgot" (Label)
        - "USERNAME" (Button) (login recover username)
        - "or" (Label)
        - "PASSWORD" (Button) (login recover password)
        - "?" (Label)
    - Layout
        - "register" (Button) (login register)


    already found features:
    - facebook (button)
    - remember me (checkbox)

    recommended features:["google", "twitter", "logo", "password strength", "privacy and legal statements", "skip", "terms & conditions"]

You are given a short description of graphical user interface of a mobile app, an user interface that the has already been selected (as a list of ui components) and a list of features the user already selected.
    Your task is to recommend the top 30 additional user interface features (as keywords) that are relevant for the user. Please thorougly check the features contained in the already selected user interface and the already found features to avoid repeating features in your recommendation.
    For your feature recommendations, focus on the specific user interface given to you and do not recommend features that are too general to the entire app (e.g. FAQs, customer support or help). A features should be a single user interface component. The result should be in the format of a python list of strings. 
    Make the feature descriptions as general as possible (e.g. instead of "report comment" just "report" or instead of "product ratings" just "ratings"). If possible use only a single word to name the feature.

    user interface description: "music player with list of songs"

    already selected user interface:
    - Layout
        - "close" (Icon) (switch)
        - "Queue" (Button) (playlist Info)
        - "more" (Icon) (ics)
    - Layout
        - (Image)
    - Layout
        - (Image) (art list)
    - List Item
        - "1." (Label) (number)
        - "2017_01_18 07:02" (Label) (title)
        - "0:05" (Label) (duration)
        - "NRJ Hits 128mp3" (Label) (artist)
        - (Image) (rating)
    - List Item
        - "2." (Label) (number)
        - "AstonMartinDBS" (Label) (title)
        - "0:03" (Label) (duration)
        - (Image) (rating)
    - List Item
        - "3." (Label) (number)
        - "Dont Give Up (Anthem) (Prod. Sinima Beats)" (Label) (title)
        - "4:43" (Label) (duration)
        - "Ms. White" (Label) (artist)
        - (Image) (rating)
    - List Item
        - "4." (Label) (number)
        - "newAccompaniment" (Label) (title)
        - "0:33" (Label) (duration)
        - "<unknown>" (Label) (artist)
        - (Image) (rating)
    - List Item
        - "5." (Label) (number)
        - "voice" (Label) (title)
        - "0:33" (Label) (duration)
        - "<unknown>" (Label) (artist)
        - (Image) (rating)
    - Layout
        - "repeat" (Icon) (repeat)
        - (Image) (shuffle)
        - "av rewind" (Icon) (previous)
        - (Image) (play)
        - "skip next" (Icon) (next)
        - "1:49" (Button) (current time)
        - "4:43" (Label) (total time)
    - Layout
        - "more" (Icon) (add)
        - "more" (Icon) (del)
        - (Image) (playlists)
        - "sliders" (Icon) (equalizer)


    already found features:
     - "share" (Icon) (share song ic)

    recommended features:["volume control", "search bar", "song thumbnail", "download button", "like", "add to playlist", "song lyrics", "artist info", "album info", "genre tag", "play speed control", "audio quality option", "offline mode", "cast button", "radio mode", "podcast mode", "personalized recommendations", "new releases", "trending songs", "user profile", "notifications", "music categories", "song comments", "song reviews", "music visualizer", "history", "queue list"]

You are given a short description of graphical user interface of a mobile app, an user interface that the has already been selected (as a list of ui components) and a list of features the user already selected.
    Your task is to recommend the top 30 additional user interface features (as keywords) that are relevant for the user. Please thorougly check the features contained in the already selected user interface and the already found features to avoid repeating features in your recommendation.
    For your feature recommendations, focus on the specific user interface given to you and do not recommend features that are too general to the entire app (e.g. FAQs, customer support or help). A features should be a single user interface component. The result should be in the format of a python list of strings. 
    Make the feature descriptions as general as possible (e.g. instead of "report comment" just "report" or instead of "product ratings" just "ratings"). If possible use only a single word to name the feature.
        
    user interface description: "placeholder_nlr_query"

    already selected user interface: 
    placeholder_selected_gui

    already found features: 
    placeholder_features

    recommended features:'''

    def __init__(self, api_organization: Text, api_key: Text, model: Optional[Text] = 'gpt-4'):
        openai.organization = api_organization
        openai.api_key = api_key
        self.model = model
        abs_path_gui2r = '/webapp/gui2rapp/staticfiles/resources/'
        self.gui2str = GUI2Str(abs_path_gui2r)

    def get_top_feature_for_query(self, query: Text, domain: Optional[Text] = None,
                                  prompt_template: Optional[Text] = PROMPT_TEMPLATE,
                                  max_tokens: Optional[int] = 256, temperature: Optional[float] = 0) -> List[Text]:
        prompt = prompt_template.replace(FeatureRankerGPTModel.PLACEHOLDER_NLR_QUERY, query)
        answer = openai.Completion.create(
            model=self.model,
            prompt=prompt,
            max_tokens=max_tokens,
            temperature=temperature
        )
        features = [feature.replace('-', '').strip().lower()
                    for feature in answer['choices'][0]['text'].split('\n') if feature]
        features_filtered = [feature for feature in features if feature and feature != query]
        return features_filtered

    def get_top_feature_recommendations_for_query(self, query: Text, feature_queries: List[Dict], selected_gui: Text,
                                  prompt_template: Optional[Text] = PROMPT_TEMPLATE_RECOMMENDATIONS_FS_NEW, include_comp_type: Optional[bool] = True,
                                  max_tokens: Optional[int] = 2000, temperature: Optional[float] = 0) -> List[Text]:
        prompt = prompt_template.replace(FeatureRankerGPTModel.PLACEHOLDER_NLR_QUERY, query)
        if include_comp_type:
            feature_str = '\n'.join(['- '+ feat['text'] + ' (' + feat['comp_type'] + ')' for feat in feature_queries])
        else:
            feature_str = '\n'.join(['- '+ feat['text'] for feat in feature_queries])
        prompt = prompt.replace(FeatureRankerGPTModel.PLACEHOLDER_FEATURES, feature_str)
        guistr = self.gui2str.get_str_repr_gui(selected_gui, n=30, m=30, to_lower=False, quote=True, style={},
                        feat_method=GUI2Str.FEAT_METHOD_TEXT_COMP_TYPE_RES_ID,
                        struct_method=GUI2Str.STRUCT_METHOD_TWO_LEVEL_BULLETS)
        prompt = prompt.replace(FeatureRankerGPTModel.PLACEHOLDER_SELECTED_GUI, guistr)
        try:
            answer = openai.ChatCompletion.create(
                    model=self.model,
                    messages= [{"role": "system", "content": "You are a helpful assistant."},
                               {"role": "user", "content": prompt}],
                    max_tokens=max_tokens,
                    temperature=temperature
            )
            result = answer['choices'][0]['message']['content'].replace('\t', '').strip()
            features_recommended = ast.literal_eval(result)
        except:
            return []
        return features_recommended

    def get_feature_explanations(self, query, features, prompt_template: Optional[Text] = PROMPT_TEMPLATE_FEATURE_EXPL,
                                 max_tokens: Optional[int] = 2000, temperature: Optional[float] = 0) -> Dict[Text, Text]:
        prompt = prompt_template.replace(FeatureRankerGPTModel.PLACEHOLDER_NLR_QUERY, query) \
                                .replace(FeatureRankerGPTModel.PLACEHOLDER_FEATURES, '\n'.join(['- '+ feat for feat in features]))
        try:
            answer = openai.ChatCompletion.create(
                model=self.model,
                messages=[{"role": "system", "content": "You are a helpful assistant."},
                          {"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=temperature
            )
            feat_mappings = ast.literal_eval(answer['choices'][0]['message']['content'])
        except:
            return {}
        return feat_mappings
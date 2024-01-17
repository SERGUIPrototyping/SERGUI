# Few-Shot Prompting

In the following, we provide and explain one of the few-shot examples that we utilized in the SERGUI approach to generate the potentially relevant GUI features given the original description of the user interface, potentially previously actively searched for and selected other features by the user and the current selected GUI itself. The prompt is structured into four main parts: **A)** The *task instruction*, **B)** the *user interface description* provided by the user, **C)** the *already selected user interface* and **D)** the *potentially previously selected features*.

## A) Task Instruction

In the following, we provide the actual task instruction used in the few-shot prompt template:

```
You are given a short description of graphical user interface of a mobile app, an user interface that the has already been selected (as a list of ui components) and a list of features the user already selected.
Your task is to recommend the top 30 additional user interface features (as keywords) that are relevant for the user. Please thorougly check the features contained in the already selected user interface and the already found features to avoid repeating features in your recommendation.
For your feature recommendations, focus on the specific user interface given to you and do not recommend features that are too general to the entire app (e.g. FAQs, customer support or help). A features should be a single user interface component. The result should be in the format of a python list of strings. 
Make the feature descriptions as general as possible (e.g. instead of "report comment" just "report" or instead of "product ratings" just "ratings"). If possible use only a single word to name the feature.
```

We clearly state to generate the top-30 user interface features (in the form of keywords for later retrieval) and push the LLM to take extra care to not repeat features that are already in the provided GUI or selected features. For improving the retrieval later on, we additionally instruct the model to provide more general feature names instead. This task instruction precedes every few-shot example. In the following, we discuss the prompting template on the basis of one of the few-shot examples.

## B) User Interface Description

Next, we provide the short user interface description to the LLM that the user has written to initially retrieve potentially relevant GUIs.

```
user interface description: "music player with list of songs"
```

## C) Abstract GUI Representation

Next, we show a detailed example for the abstract textual GUI representation that we create on the basis of the original GUI hierarchy data, but with the focus on the features and a rough layout. First, we show the actual GUI as a screenshot in the following.

Second, we show the part of the few-shot prompt including the abstract GUI representation.

```
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
```

Here, each GUI component is represented by the following abstract pattern:

```
"ui_comp_text" (uicomp-type) (resource-id)
```

For all features that contain text, we first start with the text, otherwise the *"ui_comp_text"* part is left out, followed by the *GUI component type* (e.g. **Button**, **Label**, **Checkbox** etc.) and finally the *resource-id*, a naming provided to the component by the devloper, hence, this often provides a meaningful short semantic description of the component.

Based on the extracted layouting information, we create layout groups similar to as they appear on the original GUI screenshot. In each layout group, we include the encompassed GUI components sorted in ascending order by their top-left coordinates. Each layout group is named according to their semantic information extracted from the GUI hierarchies and the groups are themselves organized in a second-level list sorted in ascending order by their top-left coordinates.

## D) Selected User Interface Features

Next, we provide a list of already selected user interface features in the few-shot prompt, which have been actively searched for by the user initially. The naming of the features follows the previously described abstract pattern.

```
 already found features:
     - "share" (Icon) (share song ic)
```

## E) Feature Recommendation

Finally, we provide the actual list of recommended features. The recommended features are represented in a Python string array to enable a simple parsing of these features later. For this few-shot example, we provided interesting features to the model that could be included in the given GUI. 

```
recommended features:["volume control", "search bar", "song thumbnail", "download button", "like", "add to playlist", "song lyrics", "artist info", "album info", "genre tag", "play speed control", "audio quality option", "offline mode", "cast button", "radio mode", "podcast mode", "personalized recommendations", "new releases", "trending songs", "user profile", "notifications", "music categories", "song comments", "song reviews", "music visualizer", "history", "queue list"]
```

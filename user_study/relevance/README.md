# Relevance Datasets

In the following, we provide a brief summary for each of the three datasets:

### 1. Feature Recommended Relevance Annotation
- **user_id**: uuid for the user session
- **gui_id**:  uuid for the gui session
-  **task_number**:  the task number of the user study
- **gui_number**:  the GUI number of the user study
- **nlr_query**:  the NLR formulation for the GUI written by the participant
- **feature_text**:  the feature text of the recommended GUI feature
- **feature_question**:  the formulated feature questions on the basis of the feature_text
- **timestamp**: the timestamp when the annotation was created
- **ranking**: the top-*k* *aspect*-GUI ranking for the feature recommendation 
- **selected_gui_id**: the gui_id of the select *aspect*-GUI
- **feature_annotation**: the relevance annotation of the feature either 0=no, 1=yes or *aspect*-GUI selected and 3=already selected 
- **matching_annotation**: the rank of the selected *aspect*-GUI or -1 if none was selected


### 2. Feature Retrieval Relevance Annotations
- **user_id**: uuid for the user session
- **gui_id**: uuid for the gui session
-  **task_number**: the task number of the user study
- **gui_number**: the GUI number of the user study
- **nlr_query**: the NLR formulation for the GUI written by the participant
- **feature_query**: the NLR formulation for the feature written by the participant
- **timestamp**: the timestamp when the annotation was created
- **ranking**: the top-*k* *aspect*-GUI ranking for the given feature NLR
- **annotation**: the rank of the selected *aspect*-GUI or -1 if none was selected

### 3. GUI Ranking Annotation
- **user_id**: uuid for the user session
- **gui_id**: uuid for the gui session
-  **task_number**: the task number of the user study
- **gui_number**: the GUI number of the user study
- **nlr_query**: the NLR formulation for the GUI written by the participant
- **timestamp**: the timestamp when the annotation was created
- **selected_gui_id_initial**: the *Rico* GUI id of the initally selected GUI
- **selected_gui_id_reselected**:  the *Rico* GUI id of the reselected GUI
- **rank_methods**: an ordererd list of applied reranking methods and steps
- **ranks_initial**: an ordered list of the ranks for the initially selected GUI for each reranking step
- **ranks_reselected**: an ordered list of the ranks for the reselected GUI for each reranking step
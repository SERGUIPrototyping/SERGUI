# GUI Ranking Overview

In this part of the repository, we provide all code files of our Python-based implementation. This includes the different GUI ranking models, the GUI feature recommendation techniques and the GUI feature ranking models. In the following, we provide a brief description of the different packages contained in the GUI ranking submission:

-  **feature_ranking**: Contains the Python scripts that are related to GUI feature ranking (feature_ranker.py), the LLM-based GUI feature recommendation (feature_ranker_gpt.py) and the methods for transforming a *Rico* GUI into a string representation (gui_2_str.py)

-  **preprocessing**: Contains the Python scripts that are related to text preprocessing (preprocess.py), text extraction (extraction.py) and filtering (filter.py)

-  **q_generator**: Contains the Python scripts that are related to creating questions (template-based) for the recommended GUI features (q_generator.py)

-  **retrieval**: Contains all Python scripts implementing the different GUI ranking models and the main script (retriever.py)

	-  **configuration**: Contains the configuration class to set and save different configuration settings

	-  **ranker**: Contains the implementations for the different GUI ranking models including the SentenceBERT GUI ranking model (sentence_bert_ranker.py), the S2W GUI ranking model (s2w_ranker.py), the ensemble model of SentenceBERT and S2W (meta_ranker.py) and another meta ranker used for computing the feature-based reranking scores (meta_ranker_v2.py)

- **resources**: Contains the downloading and installation guides for the necessary resource files employed in our approach. Due to the large size of the respective resource files, we needed to omit them in this repository. However, all of these files are publicly available such as all files related to Rico GUIs, the S2W dataset and the pretrained SentenceBERT model
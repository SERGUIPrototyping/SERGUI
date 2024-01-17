def ranking_to_json(ranking):
    return [{'index': index, 'rank': rank, 'score': score}
            for rank, (index, score) in enumerate(ranking, 1)]


def feature_ranking_to_json(feature_ranking):
    return [{'gui_id': feature.get('gui_id'), 'bounds': feature.get('bounds'), 'rank': rank}
            for rank, feature in enumerate(feature_ranking, 1)]


def feature_question_ranking_to_json(feature_question, top_k):
    return [{'gui_id': gui_id, 'bounds': bounds, 'rank': index}
           for index, (gui_id, bounds) in enumerate(zip(feature_question['feature']['gui_id'],
                                                        feature_question['feature']['bounds']),1)][:top_k]

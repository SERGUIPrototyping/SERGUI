import random

class QGenerator():

    Q_TEMPLATES = [
        "Do you need a '{}' feature in your GUI?",
        "Do you need a '{}' feature?",
        "Is a '{}' feature relevant for your GUI?",
        "Is a '{}' feature relevant for you?",
        "Is a '{}' feature in the GUI a requirement for you?",
        "Is a '{}' feature required for the GUI you are searching for?",
        "A '{}' feature is often used in similar GUIs, do you need it as well?",
        "A '{}' feature is often used in similar GUIs, do you need it as well in your GUI?",
        "A '{}' feature is often used in similar GUIs, is this a requirement for you as well?",
        "Should be a '{}' feature be part of the GUI you are searching for?",
        "Often similar GUIs contain a '{}' feature, shoud we also include in your GUI?",
        "Often similar GUIs contain a '{}' feature, is it also required for your GUI?",
        "A '{}' feature seems to be relevant for your query, do you need it in your GUI?",
        "A '{}' feature seems to be relevant for your query, is this also a requirement for your GUI?",
    ]

    Q_TEMPLATES_COMP_TYPE = [
        "Do you need a '{}' ({}) feature in your GUI?",
        "Do you need a '{}' ({}) feature?",
        "Is a '{}' ({}) feature relevant for your GUI?",
        "Is a '{}' ({}) feature relevant for you?",
        "Is a '{}' ({}) feature in the GUI a requirement for you?",
        "Is a '{}' ({}) feature required for the GUI you are searching for?",
        "A '{}' ({}) feature is often used in similar GUIs, do you need it as well?",
        "A '{}' ({}) feature is often used in similar GUIs, do you need it as well in your GUI?",
        "A '{}' ({}) feature is often used in similar GUIs, is this a requirement for you as well?",
        "Should be a '{}' ({}) feature be part of the GUI you are searching for?",
        "Often similar GUIs contain a '{}' ({}) feature, shoud we also include in your GUI?",
        "Often similar GUIs contain a '{}' ({}) feature, is it also required for your GUI?",
        "A '{}' ({}) feature seems to be relevant for your query, do you need it in your GUI?",
        "A '{}' ({}) feature seems to be relevant for your query, is this also a requirement for your GUI?",
    ]

    Q_TEMPLATES_EXPL = [
        "Do you need a <b>'{}'</b> feature in your GUI? {}",
        "Do you need a <b>'{}'</b> feature? {}",
        "Is a <b>'{}'</b> feature relevant for your GUI? {}",
        "Is a <b>'{}'</b> feature relevant for you? {}",
        "Is a <b>'{}'</b> feature in the GUI a requirement for you? {}",
        "Is a <b>'{}'</b> feature required for the GUI you are searching for? {}",
        "A <b>'{}'</b> feature is often used in similar GUIs, do you need it as well? {}",
        "A <b>'{}'</b> feature is often used in similar GUIs, do you need it as well in your GUI? {}",
        "A <b>'{}'</b> feature is often used in similar GUIs, is this a requirement for you as well? {}",
        "Should be a <b>'{}'</b> feature be part of the GUI you are searching for? {}",
        "Often similar GUIs contain a <b>'{}'</b> feature, shoud we also include in your GUI? {}",
        "Often similar GUIs contain a <b>'{}'</b> feature, is it also required for your GUI? {}",
        "A <b>'{}'</b> feature seems to be relevant for your query, do you need it in your GUI? {}",
        "A <b>'{}'</b> feature seems to be relevant for your query, is this also a requirement for your GUI? {}",
    ]

    @staticmethod
    def generate_question(feature_text, feature_comp_type=None):
        if feature_comp_type:
            selected_question = random.choice(QGenerator.Q_TEMPLATES_COMP_TYPE)
            return selected_question.format(feature_text, feature_comp_type)
        else:
            selected_question = random.choice(QGenerator.Q_TEMPLATES)
            return selected_question.format(feature_text)

    @staticmethod
    def generate_question_expl(feature_text, explanation):
        selected_question = random.choice(QGenerator.Q_TEMPLATES_EXPL)
        return selected_question.format(feature_text, explanation)

if __name__ == '__main__':
    q_generator = QGenerator()
    question_1 = q_generator.generate_question('remember me')
    print(question_1)
    question_2 = q_generator.generate_question('remember me', 'Text Button')
    print(question_2)
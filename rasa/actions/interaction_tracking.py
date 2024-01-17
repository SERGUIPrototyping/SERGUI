from sqlalchemy import Column, Integer, Text, TIMESTAMP, JSON
from sqlalchemy.exc import PendingRollbackError
from sqlalchemy.orm import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from . import config

Base = declarative_base()


class FeatureRetrievalRelevanceAnnotation(Base):
    __tablename__ = "feature_retrieval_relevance_annotations"
    user_id = Column(Text, primary_key=True)
    gui_id = Column(Text)
    task_number = Column(Text)
    gui_number = Column(Text)
    nlr_query = Column(Text)
    feature_query = Column(Text)
    timestamp = Column(TIMESTAMP)
    ranking = Column(JSON)
    annotation = Column(JSON)

    def __repr__(self):
        return "<FeatureRelevanceAnnotation(user_id='%s', gui_id='%s', task_number='%s', gui_number='%s', " \
               "nlr_query='%s', feature_query='%s', timestamp='%s', ranking='%s', annotations='%s')>" % (
            self.user_id,
            self.gui_id,
            self.task_number,
            self.gui_number,
            self.nlr_query,
            self.feature_query,
            self.timestamp,
            self.ranking,
            self.annotation
        )


class FeatureRecommendedRelevanceAnnotation(Base):
    __tablename__ = "feature_recommended_relevance_annotation"
    user_id = Column(Text, primary_key=True)
    gui_id = Column(Text)
    task_number = Column(Text)
    gui_number = Column(Text)
    nlr_query = Column(Text)
    feature_text = Column(Text)
    feature_question = Column(Text)
    timestamp = Column(TIMESTAMP)
    ranking = Column(JSON)
    selected_gui_id = Column(JSON)
    feature_annotation = Column(JSON)
    matching_annotation = Column(JSON)


    def __repr__(self):
        return "<FeatureRelevanceAnnotation(user_id='%s', gui_id='%s', task_number='%s', gui_number='%s', " \
               "nlr_query='%s', feature_text='%s', feature_question='%s', timestamp='%s', ranking='%s', selected_gui_id='%s'" \
               "feature_annotation='%s', matching_annotation='%s')>" % (
            self.user_id,
            self.gui_id,
            self.task_number,
            self.gui_number,
            self.nlr_query,
            self.feature_text,
            self.feature_question,
            self.timestamp,
            self.ranking,
            self.selected_gui_id,
            self.feature_annotation,
            self.matching_annotation,
        )


class GUIRankingAnnotation(Base):
    __tablename__ = "gui_ranking_annotation"
    user_id = Column(Text, primary_key=True)
    gui_id = Column(Text)
    task_number = Column(Text)
    gui_number = Column(Text)
    nlr_query = Column(Text)
    timestamp = Column(TIMESTAMP)
    selected_gui_id_initial = Column(Text)
    selected_gui_id_reselected = Column(Text)
    rank_methods = Column(JSON)
    ranks_initial = Column(JSON)
    ranks_reselected = Column(JSON)


    def __repr__(self):
        return "<FeatureRelevanceAnnotation(user_id='%s', gui_id='%s', task_number='%s', gui_number='%s', " \
               "nlr_query='%s', timestamp='%s', selected_gui_id_initial='%s', selected_gui_id_reselected='%s',rank_methods='%s', " \
               "ranks_initial='%s', ranks_reselected='%s')>" % (
            self.user_id,
            self.gui_id,
            self.task_number,
            self.gui_number,
            self.nlr_query,
            self.timestamp,
            self.selected_gui_id_initial,
            self.selected_gui_id_reselected,
            self.rank_methods,
            self.ranks_initial,
            self.ranks_reselected,
        )


engine = create_engine("mysql+mysqldb://"+config.INTERACTION_DB_USER+":"+
                       config.INTERACTION_DB_PW+"@"+config.INTERACTION_DB_HOST+":"+
                       config.INTERACTION_DB_PORT+"/"+ config.INTERACTION_DB_NAME, echo=True)
Session = sessionmaker(bind=engine)
session = Session()
try:
    _ = session.connection()
except PendingRollbackError:
    session.rollback()
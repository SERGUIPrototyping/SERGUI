from typing import Text
import json

class Document():

    def __init__(self, index: Text, ui_path: Text, name: Text):
        self.index = index
        self.ui_path = ui_path
        self.name = name

    def __repr__(self):
        return 'Document = index: {}, ui_path: {}, name: {}'.\
            format(self.index, self.ui_path, self.name)


class RankedDocument():

    def __init__(self, document: Document, rank: float, conf: float):
        self.document = document
        self.rank = rank
        self.conf = conf

    def __repr__(self):
        return 'RankedDocument = document {}, rank: {}, conf: {}'.\
            format(self.document, self.rank, self.conf)

    @staticmethod
    def ranked_document_to_dict(ranked_document, number_decimals=None):
        conf = ranked_document.conf
        if number_decimals:
            conf = round(conf, number_decimals)
        return {"rank": ranked_document.rank, "conf": conf,
                "document": {"index": ranked_document.document.index,
                             "ui_path": ranked_document.document.ui_path, "name": ranked_document.document.name}}


class RankedDocumentEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, RankedDocument):
                return { "rank": obj.rank, "conf": obj.conf, "document": {"index": obj.document.index,
                                        "ui_path": obj.document.ui_path, "name": obj.document.name}}
        return json.JSONEncoder.default(self, obj)
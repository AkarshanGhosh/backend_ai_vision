from datetime import datetime

class Blog:
    def __init__(self, title, content, author_id):
        self.title = title
        self.content = content
        self.author_id = author_id
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def to_dict(self):
        return self.__dict__

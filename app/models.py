from datetime import datetime
from app import db


class Record(db.Model):
    __tablename__ = "records"

    id = db.Column(db.Integer, primary_key=True)
    term = db.Column(db.String(200), nullable=False)
    full_name = db.Column(db.String(200), nullable=True)
    category = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    example = db.Column(db.Text, nullable=True)
    keywords = db.Column(db.String(500), nullable=True)
    understanding = db.Column(db.Integer, nullable=False, default=3)
    registered_year = db.Column(db.Integer, nullable=False)
    registered_month = db.Column(db.Integer, nullable=False)
    quiz_correct = db.Column(db.Integer, nullable=False, default=0)
    quiz_incorrect = db.Column(db.Integer, nullable=False, default=0)
    quiz_total = db.Column(db.Integer, nullable=False, default=0)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    @property
    def quiz_accuracy(self):
        """クイズ正答率（%）を返す。出題0回の場合はNoneを返す。"""
        if self.quiz_total == 0:
            return None
        return round(self.quiz_correct / self.quiz_total * 100, 1)

    def __repr__(self):
        return f"<Record {self.id}: {self.term}>"

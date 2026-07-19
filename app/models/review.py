from datetime import datetime

from app import db


class Review(db.Model):

    __tablename__ = "reviews"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    filename = db.Column(db.String(255), nullable=False)

    quality_score = db.Column(db.Float, nullable=False)

    ml_prediction = db.Column(db.String(50), nullable=True)

    ml_confidence = db.Column(db.Float, nullable=True)

    issue_count = db.Column(db.Integer, nullable=False, default=0)

    semantic_score = db.Column(db.Float, nullable=True)

    refactored_code = db.Column(db.Text, nullable=True)

    refactored_explanation = db.Column(db.Text, nullable=True)

    clean_code = db.Column(db.Text, nullable=True)

    best_practice_code = db.Column(db.Text, nullable=True)

    optimized_code = db.Column(db.Text, nullable=True)

    changes = db.Column(db.Text, nullable=True)


    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    user = db.relationship(
        "User",
        backref=db.backref("reviews", lazy="dynamic")
    )

    def __repr__(self):
        return f"<Review {self.filename} - Score: {self.quality_score}>"


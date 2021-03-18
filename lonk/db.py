from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Redirect(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    shortname = db.Column(db.String, unique=True, nullable=False)
    url = db.Column(db.String, nullable=False)

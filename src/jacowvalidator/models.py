from datetime import datetime
from jacowvalidator import db


class Log(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(64), index=True)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    report = db.Column(db.Text())

    def __repr__(self):
        return '<Log {} {}>'.format(self.filename, self.timestamp)

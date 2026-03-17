from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Scene(db.Model):
    __tablename__ = 'Scenes'
    # Các thông tin về bộ ảnh
    SampleToken = db.Column(db.String(100), primary_key=True)
    SceneName = db.Column(db.String(255))
    FrontImg = db.Column(db.String(255))
    BackImg = db.Column(db.String(255))
    FrontLeftImg = db.Column(db.String(255))
    FrontRightImg = db.Column(db.String(255))
    BackLeftImg = db.Column(db.String(255))
    BackRightImg = db.Column(db.String(255))
    Timestamp = db.Column(db.DateTime)
    
    # Quan hệ với nhãn vật thể và kết quả duyệt
    labels = db.relationship('ObjectLabel', backref='scene', lazy=True)
    review = db.relationship('Annotation', backref='scene', uselist=False)

class ObjectLabel(db.Model):
    __tablename__ = 'ObjectLabels'
    ID = db.Column(db.Integer, primary_key=True)
    SampleToken = db.Column(db.String(100), db.ForeignKey('Scenes.SampleToken'))
    Category = db.Column(db.String(100))
    # Tọa độ bounding box (nếu có)
    X = db.Column(db.Float)
    Y = db.Column(db.Float)

class Annotation(db.Model):
    __tablename__ = 'Annotations'
    SampleToken = db.Column(db.String(100), db.ForeignKey('Scenes.SampleToken'), primary_key=True)
    ReviewStatus = db.Column(db.Integer) # 1: Đúng, 2: Sai
    ReviewDate = db.Column(db.DateTime, default=datetime.now)
    Reviewer = db.Column(db.String(100), default='Alex Rivera')
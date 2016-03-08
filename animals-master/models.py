from init import db,app

class Animal(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50))
    location = db.Column(db.String(50))

db.create_all(app=app)
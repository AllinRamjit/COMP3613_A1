from App.database import db

class Street(db.Model):
    __tablename__ = 'streets'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, unique=True)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return f"<Street id={self.id} name={self.name}>"
    
    def get_json(self):
        return {
            'id': self.id,
            'name': self.name
        }

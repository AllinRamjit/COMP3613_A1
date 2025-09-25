from App.database import db
from datetime import datetime

class Request(db.Model):
    __tablename__ = 'requests'
    id = db.Column(db.Integer, primary_key=True)
    route_id = db.Column(db.Integer, db.ForeignKey("route.id"), nullable=False)
    resident_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    notes = db.Column(db.String(500), nullable=True)  
    quantity = db.Column(db.Integer, nullable=True)  
    status = db.Column(db.String(20), nullable=False, default="requested")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    route = db.relationship('Route', backref=db.backref('stop_requests', lazy=True))
    resident = db.relationship('User', backref=db.backref('stop_requests', lazy=True))

    def __init__(self, route_id=None, resident_id=None, notes=None, quantity=None, status="requested", created_at=None):
        self.route_id = route_id
        self.resident_id = resident_id
        self.notes = notes
        self.quantity = quantity
        self.status = status
        self.created_at = created_at or datetime.utcnow()


    def __repr__(self):
        return f"<Request id={self.id} route_id={self.route_id} resident_id={self.resident_id} quantity={self.quantity} status={self.status} created_at={self.created_at} notes={self.notes}>"

        
    
        
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

    order = db.relationship('route', backref=db.backref('stop_requests', lazy=True))
    resident = db.relationship('user', backref=db.backref('stop_requests', lazy=True))


    def __repr__(self):
        return f"<Request id={self.id} resident_id={self.resident_id} driver_id={self.driver_id} street_id={self.street_id} quantity={self.quantity} status={self.status} requested_time={self.requested_time} completed_time={self.completed_time}>"

        
    
        
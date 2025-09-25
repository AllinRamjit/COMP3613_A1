from App.database import db
from datetime import datetime

class Route(db.Model):
    __tablename__ = "route"
    id = db.Column(db.Integer, primary_key=True)
    driver_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    street_id = db.Column(db.Integer, db.ForeignKey("streets.id"), nullable=False)
    scheduled_time = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), nullable=False, default="scheduled") 
    current_lat = db.Column(db.Float, nullable=True)
    current_lng = db.Column(db.Float, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    driver = db.relationship("User", backref=db.backref("Route", lazy=True))
    street = db.relationship("Street", backref=db.backref("Route", lazy=True))

    def __init__(self, driver_id, street_id, scheduled_time, status="scheduled", current_lat=None, current_lng=None):
        self.driver_id = driver_id
        self.street_id = street_id
        self.scheduled_time = scheduled_time
        self.status = status
        self.current_lat = current_lat
        self.current_lng = current_lng

    def __repr__(self):
        return f"<Drive id={self.id} driver_id={self.driver_id} street_id={self.street_id} time={self.scheduled_time} status={self.status}>"

def get_route(self, route_id: int):
        route = route.query.get(route_id)
        if route != self.id:
            raise ValueError(f"Request {route_id} not found")
        return route

def parse_time(iso_string):
    """Convert ISO formatted string to datetime object."""
    try:
        return datetime.fromisoformat(iso_string)
    except Exception:
        raise ValueError("Invalid datetime format. Use ISO format.")
from config.database import db


class TravelRequest(db.Model):
    __tablename__ = "travel_requests"

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(
        db.Integer,
        db.ForeignKey("employees.id"),
        nullable=False
    )
    destination = db.Column(db.String(100), nullable=False)
    purpose = db.Column(db.String(255), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    estimated_amount = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(db.String(50), nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "employee_id": self.employee_id,
            "destination": self.destination,
            "purpose": self.purpose,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "estimated_amount": self.estimated_amount,
            "status": self.status
        }

from config.database import db


class ExpenseClaim(db.Model):
    __tablename__ = "expense_claims"

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(
        db.Integer,
        db.ForeignKey("employees.id"),
        nullable=False
    )
    travel_request_id = db.Column(
        db.Integer,
        db.ForeignKey("travel_requests.id"),
        nullable=False
    )
    total_amount = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(db.String(50), nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "employee_id": self.employee_id,
            "travel_request_id": self.travel_request_id,
            "total_amount": self.total_amount,
            "status": self.status
        }

from config.database import db
from models.travel_requests import TravelRequest
from sqlalchemy.exc import IntegrityError


class TravelRequestDAO:

    def get_all(self, page=1, per_page=10):
        return TravelRequest.query.paginate(page=page, per_page=per_page)

    def get_by_id(self, request_id):
        return TravelRequest.query.get(request_id)

    def get_by_employee_id(self, employee_id):
        return TravelRequest.query.filter_by(employee_id=employee_id).all()

    def get_by_status(self, status):
        return TravelRequest.query.filter_by(status=status).all()

    def save_travel_request(self, travel_request):
        db.session.add(travel_request)
        db.session.commit()
        return travel_request

    def update(self, travel_request):
        db.session.commit()
        return travel_request

    def delete(self, travel_request):
        try:
            db.session.delete(travel_request)
            db.session.commit()
            return True
        except IntegrityError:
            db.session.rollback()
            return False

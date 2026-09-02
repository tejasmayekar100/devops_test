from models.travel_requests import TravelRequest


class TravelRequestService:

    def __init__(self, travel_request_dao, employee_dao):
        self.travel_request_dao = travel_request_dao
        self.employee_dao = employee_dao

    def get_all_travel_requests(self, page=1, per_page=10):
        return self.travel_request_dao.get_all(page, per_page)

    def get_travel_request(self, request_id):
        travel_request = self.travel_request_dao.get_by_id(request_id)

        if travel_request is None:
            raise ValueError("Travel request not found")

        return travel_request

    def get_employee_requests(self, employee_id):
        return self.travel_request_dao.get_by_employee_id(employee_id)

    def get_requests_by_status(self, status):
        return self.travel_request_dao.get_by_status(status)

    def create_travel_request(
        self,
        employee_id,
        destination,
        purpose,
        start_date,
        end_date,
        estimated_amount
    ):

        travel_request = TravelRequest(
            employee_id=employee_id,
            destination=destination,
            purpose=purpose,
            start_date=start_date,
            end_date=end_date,
            estimated_amount=estimated_amount,
            status="PENDING"
        )

        return self.travel_request_dao.save_travel_request(travel_request)

    def update_travel_request(
        self,
        request_id,
        destination=None,
        purpose=None,
        start_date=None,
        end_date=None,
        estimated_amount=None
    ):

        travel_request = self.travel_request_dao.get_by_id(request_id)

        if travel_request is None:
            raise ValueError("Travel request not found")

        if travel_request.status != "PENDING":
            raise ValueError("Only pending travel requests can be updated")

        if destination:
            travel_request.destination = destination

        if purpose:
            travel_request.purpose = purpose

        if start_date:
            travel_request.start_date = start_date

        if end_date:
            travel_request.end_date = end_date

        if estimated_amount is not None:
            travel_request.estimated_amount = estimated_amount

        return self.travel_request_dao.update(travel_request)

    def delete_travel_request(self, request_id):

        travel_request = self.travel_request_dao.get_by_id(request_id)

        if not travel_request:
            return False

        return self.travel_request_dao.delete(travel_request)

    def approve_travel_request(self, request_id, manager_user_id):

        travel_request = self.travel_request_dao.get_by_id(request_id)

        if travel_request is None:
            raise ValueError("Travel request not found")

        if travel_request.status != "PENDING":
            raise ValueError("Only pending travel requests can be approved")

        # Get the employee who submitted the request
        employee = self.employee_dao.get_by_id(travel_request.employee_id)

        if employee is None:
            raise ValueError("Employee not found")

        # Get the employee record of the logged-in manager
        manager_employee = self.employee_dao.get_by_user_id(manager_user_id)

        if manager_employee is None:
            raise ValueError("Manager employee profile not found")

        # Verify that this manager actually manages the employee who submitted the request
        if employee.manager_id != manager_employee.id:
            raise ValueError(
                "Only the employee's manager can approve this request")

        travel_request.status = "APPROVED"

        return self.travel_request_dao.update(travel_request)

    def reject_travel_request(self, request_id, manager_user_id):

        travel_request = self.travel_request_dao.get_by_id(request_id)

        if travel_request is None:
            raise ValueError("Travel request not found")

        if travel_request.status != "PENDING":
            raise ValueError("Only pending travel requests can be rejected")

        # Get the employee who submitted the request
        employee = self.employee_dao.get_by_id(travel_request.employee_id)

        if employee is None:
            raise ValueError("Employee not found")

        # Get the employee record of the logged-in manager
        manager_employee = self.employee_dao.get_by_user_id(manager_user_id)

        if manager_employee is None:
            raise ValueError("Manager employee profile not found")

        # Verify that this manager actually manages the employee who submitted the request
        if employee.manager_id != manager_employee.id:
            raise ValueError(
                "Only the employee's manager can reject this request")

        travel_request.status = "REJECTED"

        return self.travel_request_dao.update(travel_request)

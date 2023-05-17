from flask import Blueprint, render_template

from public_service_employee_application.views.auth_views import login_required_admin
from public_service_employee_application.models import HR_change_request, Join_request, Vacation_request
from public_service_employee_application import db


# 블루프린트 객체 생성
bp = Blueprint('admin', __name__, url_prefix='/admin')


# 이 블루프린트의 최초 진입점
@bp.route('/', methods=['GET'])
@login_required_admin
def index():
    hr_change_request = HR_change_request.query.filter(
        HR_change_request.state == 'WAITING'
    ).all()
    join_request = Join_request.query.filter(
        Join_request.state == 'WAITING'
    ).all()
    vacation_request = Vacation_request.query.filter(
        Vacation_request.state == 'WAITING'
    ).all()

    request_list = hr_change_request + join_request + vacation_request

    return render_template('admin/main/main.html', request_list=request_list)
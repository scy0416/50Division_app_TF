from flask import Blueprint, render_template

from public_service_employee_application.views.auth_views import login_required_admin
from public_service_employee_application.models import Join_request, HR_change_request, Vacation_request, Medical_checkup_request
from public_service_employee_application import db


# 블루프린트 객체 생성
bp = Blueprint('admin_request', __name__, url_prefix='/admin/request')


# 이 블루프린트의 최초 진입점
@bp.route('/', methods=['GET'])
@login_required_admin
def index():
    join_request = Join_request.query.filter(Join_request.state == 'WAITING').all()
    hr_change_request = HR_change_request.query.filter(HR_change_request.state == 'WAITING').all()
    vacation_request = Vacation_request.query.filter(Vacation_request.state == 'WAITING').all()
    medical_checkup_request = Medical_checkup_request.query.filter(Medical_checkup_request.state == 'WAITING').all()
    return render_template('admin/request/request_main.html',
                           join_request=join_request,
                           hr_change_request=hr_change_request,
                           vacation_request=vacation_request,
                           medical_checkup_request=medical_checkup_request)
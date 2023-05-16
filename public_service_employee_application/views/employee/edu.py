from flask import Blueprint, render_template, g

from public_service_employee_application.views.auth_views import login_required_employee
from public_service_employee_application.models import User
from public_service_employee_application import db

# 블루프린트 객체 생성
bp = Blueprint('employee_edu', __name__, url_prefix='/employee/edu')


# 이 블루프린트의 최초 진입점
@bp.route('/', methods=['GET'])
@login_required_employee
def index():
    user = User.query.get_or_404(g.user.id)
    return render_template('employee/edu/edu.html', user=user)
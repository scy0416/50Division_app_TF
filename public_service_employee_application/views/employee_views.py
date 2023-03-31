from flask import Blueprint, render_template

from public_service_employee_application.views.auth_views import login_required_employee

# 블루프린트 객체 생성
bp = Blueprint('employee', __name__, url_prefix='/employee')

# 이 블루프린트의 최초 진입점
@bp.route('/', methods=('GET', ))
# 직원으로 로그인이 되었나 확인하는 부분
@login_required_employee
def index():
    return render_template('user/employee_main.html')
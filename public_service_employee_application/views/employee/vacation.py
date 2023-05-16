from flask import Blueprint, render_template, request, g, redirect, url_for
from datetime import datetime

from public_service_employee_application.views.auth_views import login_required_employee
from public_service_employee_application.models import Vacation_request
from public_service_employee_application import db

# 블루프린트 객체 생성
bp = Blueprint('employee_vacation', __name__, url_prefix='/employee/vacation')


# 이 블루프린트의 최초 진입점
@bp.route('/', methods=['GET'])
@login_required_employee
def index():
    page = request.args.get('page', type=int, default=1)
    vacation_request_list = Vacation_request.query.filter(
        Vacation_request.user_id == g.user.id
    ).order_by(
        Vacation_request.request_date.desc()
    ).paginate(page=page, per_page=5)

    return render_template('employee/vacation/vacation.html',
                           page=page, vacation_request_list=vacation_request_list)


# 휴가 신청 등록
@bp.route('/', methods=['POST'])
@login_required_employee
def request_vacation():
    from_date = request.form.get('from_date')
    to_date = request.form.get('to_date')
    reason = request.form.get('reason')
    vacation_request = Vacation_request(
        user_id=g.user.id,
        from_date=from_date,
        to_date=to_date,
        reason=reason,
        state='WAITING',
        request_date=datetime.now()
    )
    db.session.add(vacation_request)
    db.session.commit()

    return redirect(url_for('employee_vacation.index'))
from flask import Blueprint, g, render_template, request, redirect, url_for
from datetime import datetime

from public_service_employee_application.views.auth_views import login_required_employee
from public_service_employee_application.models import User, HR_change_request
from public_service_employee_application import db

# 블루프린트 객체 생성
bp = Blueprint('employee_personal_record', __name__, url_prefix='/employee/pr')


# 이 블루프린트의 최초 진입점
@bp.route('/', methods=['GET'])
@login_required_employee
def index():
    user = User.query.get_or_404(g.user.id)
    return render_template('employee/personal_record/personal_record.html', user=user)


# 연락처 편집
@bp.route('/edit/pn', methods=['POST'])
@login_required_employee
def edit_phone_num():
    user = User.query.get_or_404(g.user.id)
    phone_num = request.form.get('change_to')
    user.phone_num = phone_num
    db.session.commit()
    return redirect(url_for('employee_personal_record.index'))


# 주소 편집
@bp.route('/edit/adr', methods=['POST'])
@login_required_employee
def edit_address():
    user = User.query.get_or_404(g.user.id)
    address = request.form.get('change_to')
    user.address = address
    db.session.commit()
    return redirect(url_for('employee_personal_record.index'))


# 고용일/퇴직일 변경 신청창
@bp.route('/edit/pr/<type>', methods=['GET'])
@login_required_employee
def pr_change_page(type):
    user = User.query.get_or_404(g.user.id)
    return render_template('employee/personal_record/personal_record_change.html',
                           type=type, user=user)


# 고용일/퇴직일 변경 신청
@bp.route('/edit/pr', methods=['POST'])
@login_required_employee
def pr_change_request():
    type = request.form.get('type')
    if type == 'hire':
        type = 'HIRE'
    elif type == 'RETIRE':
        type = 'RETIREMENT'
    hr_change_request = HR_change_request(
        user_id=g.user.id,
        reason=request.form.get('reason'),
        change_to=request.form.get('change_to'),
        type=type,
        state='WAITING',
        request_date=datetime.now()
    )
    db.session.add(hr_change_request)
    db.session.commit()

    return redirect(url_for('employee_personal_record.index'))


# 이미지 변경 페이지
@bp.route('/edit/img', methods=['GET'])
@login_required_employee
def image():
    return render_template('employee/personal_record/image_change.html')


# 이미지 변경 처리
@bp.route('/edit/img', methods=['POST'])
@login_required_employee
def image_change():
    user = User.query.get_or_404(g.user.id)
    user.img_addr = request.form.get('image')
    db.session.commit()
    return redirect(url_for('employee_personal_record.index'))
from flask import Blueprint, render_template, request, g, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename
import os
from datetime import datetime

from public_service_employee_application.views.auth_views import login_required_employee
from public_service_employee_application.models import Medical_checkup_request
from public_service_employee_application import db

# 블루프린트 객체 생성
bp = Blueprint('employee_medical_checkup', __name__, url_prefix='/employee/medical_checkup')


# 이 블루프린트의 최초 진입점
@bp.route('/', methods=['GET'])
@login_required_employee
def index():
    page = request.args.get('page', type=int, default=1)
    medical_checkup_list = Medical_checkup_request.query.filter_by(
        user_id=g.user.id
    ).order_by(Medical_checkup_request.request_date.desc())
    medical_checkup_list = medical_checkup_list.paginate(page=page, per_page=10)

    return render_template('employee/medical_checkup/medical_checkup.html',
                           page=page,
                           medical_checkup_list=medical_checkup_list)


# 건강검진 등록 화면
@bp.route('/request', methods=['GET'])
@login_required_employee
def medical_checkup_request_page():
    return render_template('employee/medical_checkup/medical_checkup_request.html')


# 이미지 업로드 및 건강검진 확인 요청 생성
@bp.route('/request', methods=['POST'])
def medical_checkup_request():
    f = request.files['file']
    f.save(os.path.join('static/medical_checkup', secure_filename(f.filename)))

    medical_checkup_request = Medical_checkup_request(
        user_id=g.user.id,
        img_addr=secure_filename(f.filename),
        state='WAITING',
        request_date=datetime.now()
    )
    db.session.add(medical_checkup_request)
    db.session.commit()

    return redirect(url_for('employee_medical_checkup.index'))


# 신청 사항 자세히 보기
@bp.route('/request/<int:request_id>', methods=['GET'])
@login_required_employee
def medical_checkup_request_detail(request_id):
    request = Medical_checkup_request.query.get_or_404(request_id)
    img_name = request.img_addr

    return render_template('employee/medical_checkup/medical_checkup_detail.html',
                           medical_checkup=request, img_name=img_name)

# 건강검진 이미지 반환
@bp.route('/request/image/<path:filename>', methods=['GET'])
@login_required_employee
def medical_checkup_image(filename):
    return send_from_directory('static/medical_checkup', filename)
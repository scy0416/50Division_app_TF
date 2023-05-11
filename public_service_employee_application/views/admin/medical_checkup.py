from flask import Blueprint, render_template, request, redirect, url_for, send_from_directory
from sqlalchemy import asc, desc, or_
from datetime import datetime

from public_service_employee_application.views.auth_views import login_required_admin
from public_service_employee_application.models import Medical_checkup_request, User
from public_service_employee_application import db

# 블루프린트 객체 생성
bp = Blueprint('admin_medical_checkup', __name__, url_prefix='/admin/medical_checkup')


# 이 블루프린트의 최초 진입점
@bp.route('/', methods=['GET'])
@login_required_admin
def index():
    return render_template('admin/medical_checkup/medical_checkup.html')


# 유저 목록
@bp.route('/employee', methods=['GET'])
@login_required_admin
def get_user_list():
    # 검색 및 페이징 처리
    q = request.args.get('q', type=str, default='')
    page = request.args.get('page', type=int, default=1)
    order = request.args.get('order', type=str, default='asc')
    processed = request.args.get('processed', type=str, default='true')
    processed = str_to_bool(processed)
    unprocessed = request.args.get('unprocessed', type=str, default='true')
    unprocessed = str_to_bool(unprocessed)

    # 처리 대기중인 신청 쿼리->정렬->검색
    if unprocessed:
        # 대기중인 신청 필터링
        unprocessed_request = Medical_checkup_request.query.filter(
            Medical_checkup_request.state == 'WAITING'
        )
        # 정렬
        if order == 'asc':
            unprocessed_request = unprocessed_request.order_by(
                asc(Medical_checkup_request.request_date)
            )
        elif order == 'desc':
            unprocessed_request = unprocessed_request.order_by(
                desc(Medical_checkup_request.request_date)
            )
        # 이름 검색
        unprocessed_request = unprocessed_request.outerjoin(
            User,
            Medical_checkup_request.user_id == User.id
        ).filter(
            User.name.ilike('%' + q + '%')
        )
    # 처리된 신청 쿼리->정렬->검색
    if processed:
        # 처리된 신청 필터링
        processed_request = Medical_checkup_request.query.filter(
            or_(
                Medical_checkup_request.state == 'ALLOWED',
                Medical_checkup_request.state == 'REJECTED'
            )
        )
        # 정렬
        if order == 'asc':
            processed_request = processed_request.order_by(
                desc(Medical_checkup_request.state),
                asc(Medical_checkup_request.request_date)
            )
        elif order == 'desc':
            processed_request = processed_request.order_by(
                desc(Medical_checkup_request.state),
                desc(Medical_checkup_request.request_date)
            )
        # 이름 검색
        processed_request = processed_request.outerjoin(
            User,
            Medical_checkup_request.user_id == User.id
        ).filter(
            User.name.ilike('%' + q + '%')
        )
    # 두 쿼리 합치기
    if processed is True and unprocessed is True:
        unprocessed_request = unprocessed_request
        processed_request = processed_request
        request_list = unprocessed_request.union(processed_request)
        if order == 'asc':
            request_list = request_list.order_by(
                desc(Medical_checkup_request.state),
                Medical_checkup_request.request_date
            )
        elif order == 'desc':
            request_list = request_list.order_by(
                desc(Medical_checkup_request.state),
                desc(Medical_checkup_request.request_date)
            )
    elif processed is False and unprocessed is True:
        request_list = unprocessed_request
    elif processed is True and unprocessed is False:
        request_list = processed_request
    elif processed is False and unprocessed is False:
        request_list = Medical_checkup_request.query.filter_by(state='')
    # 페이지네이트
    request_list = request_list.paginate(page=page, per_page=10)

    return render_template('admin/medical_checkup/user_list.html', q=q, page=page, medical_checkup_list=request_list)


# 문자열을 통해서 참 거짓을 판별하는 함수
def str_to_bool(s):
    if s.lower() == 'true':
        return True
    elif s.lower() == 'false':
        return False


# 상세 요청 페이지를 반환
@bp.route('/<int:request_id>', methods=['GET'])
@login_required_admin
def medical_checkup_detail(request_id):
    medical_checkup = Medical_checkup_request.query.get_or_404(request_id)
    user = User.query.get_or_404(medical_checkup.user_id)
    return render_template(
        'admin/medical_checkup/medical_checkup_detail.html',
        user=user,
        medical_checkup=medical_checkup
    )

# 승인 처리
@bp.route('/<int:request_id>/allow', methods=['POST'])
@login_required_admin
def allow_medical_checkup(request_id):
    medical_checkup = Medical_checkup_request.query.get_or_404(request_id)
    bigo = request.form.get('bigo', default='')
    medical_checkup.bigo = bigo
    medical_checkup.state = 'ALLOWED'
    medical_checkup.proc_date = datetime.now()
    db.session.commit()

    return redirect(url_for('admin_medical_checkup.medical_checkup_detail', request_id=request_id))


# 거부 처리
@bp.route('/<int:request_id>/reject', methods=['POST'])
@login_required_admin
def reject_medical_checkup(request_id):
    medical_checkup = Medical_checkup_request.query.get_or_404(request_id)
    bigo = request.form.get('bigo', default='')
    medical_checkup.bigo = bigo
    medical_checkup.state = 'REJECTED'
    medical_checkup.proc_date = datetime.now()
    db.session.commit()

    return redirect(url_for('admin_medical_checkup.medical_checkup_detail', request_id=request_id))


# 변경 처리
@bp.route('/<int:request_id>/edit', methods=['POST'])
@login_required_admin
def edit_medical_checkup(request_id):
    medical_checkup = Medical_checkup_request.query.get_or_404(request_id)
    bigo = request.form.get('bigo', default='')
    medical_checkup.bigo = bigo
    db.session.commit()

    return redirect(url_for('admin_medical_checkup.medical_checkup_detail', request_id=request_id))


# 건강검진 이미지 반환
@bp.route('/<int:request_id>/image', methods=['GET'])
@login_required_admin
def medical_checkup_image(request_id):
    request = Medical_checkup_request.query.get_or_404(request_id)
    return send_from_directory('static/medical_checkup', request.img_addr)
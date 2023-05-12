from flask import Blueprint, request, render_template, redirect, url_for
from sqlalchemy import asc, desc, or_
from datetime import datetime

from public_service_employee_application.views.auth_views import login_required_admin
from public_service_employee_application.models import Vacation_request, User
from public_service_employee_application import db

# 블루프린트 객체 생성
bp = Blueprint('admin_vacation_request', __name__, url_prefix='/admin/request/vacation')


# 이 블루프린트의 최초 진입점
@bp.route('/', methods=['GET'])
@login_required_admin
def index():
    return render_template('admin/vacation_request/vacation_request_list.html')


# 유저 목록
@bp.route('/user', methods=['GET'])
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

    # 처리 대기중인 신청
    if unprocessed:
        # 유저와 아우터 조인
        unprocessed_request = db.session.query(
            Vacation_request,
            User
        ).outerjoin(
            User,
            Vacation_request.user_id == User.id
        ).filter(
            Vacation_request.state == 'WAITING'
        ).filter(
            User.name.contains(q)
        )
        # 정렬
        if order == 'asc':
            unprocessed_request = unprocessed_request.order_by(
                asc(Vacation_request.request_date)
            )
        elif order == 'desc':
            unprocessed_request = unprocessed_request.order_by(
                desc(Vacation_request.request_date)
            )
    # 처리된 신청
    if processed:
        processed_request = db.session.query(
            Vacation_request,
            User
        ).outerjoin(
            User,
            Vacation_request.user_id == User.id
        ).filter(
            or_(
                Vacation_request.state == 'ALLOWED',
                Vacation_request.state == 'REJECTED'
            )
        ).filter(
            User.name.contains(q)
        )
        # 정렬
        if order == 'asc':
            processed_request = processed_request.order_by(
                desc(Vacation_request.state),
                asc(Vacation_request.request_date)
            )
        elif order == 'desc':
            processed_request = processed_request.order_by(
                desc(Vacation_request.state),
                desc(Vacation_request.request_date)
            )
    # 두 쿼리 합치기
    if processed is True and unprocessed is True:
        unprocessed_request = unprocessed_request
        processed_request = processed_request
        request_list = unprocessed_request.union(processed_request)
        if order == 'asc':
            request_list = request_list.order_by(
                desc(Vacation_request.state),
                asc(Vacation_request.request_date)
            )
        elif order == 'desc':
            request_list = request_list.order_by(
                desc(Vacation_request.state),
                desc(Vacation_request.request_date)
            )
    elif processed is False and unprocessed is True:
        request_list = unprocessed_request
    elif processed is True and unprocessed is False:
        request_list = processed_request
    elif processed is False and unprocessed is False:
        request_list = Vacation_request.query.filter_by(state='')
    #페이지네이트
    request_list = request_list.paginate(page=page, per_page=10)

    return render_template('admin/vacation_request/user_list.html', q=q, page=page, request_list=request_list)


# 문자열을 통해서 참 거짓을 판별하는 함수
def str_to_bool(s):
    if s.lower() == 'true':
        return True
    elif s.lower() == 'false':
        return False


# 상세창
@bp.route('/<int:request_id>', methods=['GET'])
@login_required_admin
def detail(request_id):
    request = Vacation_request.query.get_or_404(request_id)
    user = User.query.get_or_404(request.user_id)

    return render_template('admin/vacation_request/vacation_request_detail.html',
                           request=request, user=user)


# 승인
@bp.route('/<int:request_id>/allow', methods=['POST'])
@login_required_admin
def allow(request_id):
    request = Vacation_request.query.get_or_404(request_id)
    request.state = 'ALLOWED'
    request.proc_date = datetime.now()
    db.session.commit()
    return redirect(url_for('admin_vacation_request.detail', request_id=request_id))


# 거부
@bp.route('/<int:request_id>/deny', methods=['POST'])
@login_required_admin
def deny(request_id):
    request = Vacation_request.query.get_or_404(request_id)
    request.state = 'REJECTED'
    request.proc_date = datetime.now()
    db.session.commit()
    return redirect(url_for('admin_vacation_request.detail', request_id=request_id))
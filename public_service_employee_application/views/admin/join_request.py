from flask import Blueprint, render_template, request, redirect, url_for
from sqlalchemy import asc, desc, or_
from datetime import datetime

from public_service_employee_application.views.auth_views import login_required_admin
from public_service_employee_application.models import Join_request, User
from public_service_employee_application import db

# 블루프린트 객체 생성
bp = Blueprint('admin_join_request', __name__, url_prefix='/admin/request/join')


# 이 블루프린트의 최초 진입점
@bp.route('/', methods=['GET'])
@login_required_admin
def index():
    return render_template('admin/join_request/join_request_list.html')


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

    # 처리 대기중인 신청 쿼리->정렬->검색
    if unprocessed:
        # 대기중인 신청 필터링
        unprocessed_request = Join_request.query.filter(
            Join_request.state == 'WAITING'
        )
        # 정렬
        if order == 'asc':
            unprocessed_request = unprocessed_request.order_by(
                asc(Join_request.request_date)
            )
        elif order == 'desc':
            unprocessed_request = unprocessed_request.order_by(
                desc(Join_request.request_date)
            )
        # 이름 검색
        unprocessed_request = unprocessed_request.filter(
            Join_request.name.ilike('%' + q + '%')
        )
    # 처리된 신청 쿼리->정렬->검색
    if processed:
        # 처리된 신청 필터링
        processed_request = Join_request.query.filter(
            or_(
                Join_request.state == 'ALLOWED',
                Join_request.state == 'REJECTED'
            )
        )
        # 정렬
        if order == 'asc':
            processed = processed_request.order_by(
                desc(Join_request.state),
                asc(Join_request.request_date)
            )
        elif order == 'desc':
            processed_request = processed_request.order_by(
                desc(Join_request.state),
                desc(Join_request.request_date)
            )
        # 이름 검색
        processed_request = processed_request.filter(
            Join_request.name.ilike('%' + q + '%')
        )
    # 두 쿼리 합치기
    if processed is True and unprocessed is True:
        unprocessed_request = unprocessed_request
        processed_request = processed_request
        request_list = unprocessed_request.union(processed_request)
        if order == 'asc':
            request_list = request_list.order_by(
                desc(Join_request.state),
                Join_request.request_date
            )
        elif order == 'desc':
            request_list = request_list.order_by(
                desc(Join_request.state),
                desc(Join_request.request_date)
            )
    elif processed is False and unprocessed is True:
        request_list = unprocessed_request
    elif processed is True and unprocessed is False:
        request_list = processed_request
    elif processed is False and unprocessed is False:
        request_list = Join_request.query.filter_by(state='')
    # 페이지네이트
    request_list = request_list.paginate(page=page, per_page=10)

    return render_template('admin/join_request/user_list.html', q=q, page=page, request_list=request_list)


# 문자열을 통해서 참 거짓을 판별하는 함수
def str_to_bool(s):
    if s.lower() == 'true':
        return True
    elif s.lower() == 'false':
        return False


# 가입 신청 상세 창
@bp.route('/<int:request_id>', methods=['GET'])
@login_required_admin
def join_detail(request_id):
    join_request = Join_request.query.get_or_404(request_id)

    name = request.args.get('name', type=str, default=join_request.name)
    birth_date = request.args.get('birth_date', type=str, default=join_request.birth_date)
    id = request.args.get('id', type=str, default='')

    result_list = User.query.filter(User.name.contains(name))
    result_list = result_list.filter(User.birth_date == birth_date)
    result_list = result_list.filter(User.userid is None)
    result_list = result_list.filter(User.password is None)
    result_list = result_list.filter(User.userid.ilike('%' + id + '%'))

    return render_template('admin/join_request/join_request_detail.html',
                           join_request=join_request,
                           name=name, birth_date=birth_date)


# 가입 거부 처리
@bp.route('/reject/<int:request_id>', methods=['POST'])
@login_required_admin
def reject_request(request_id):
    join_request = Join_request.query.get_or_404(request_id)
    join_request.state = 'REJECTED'
    join_request.proc_date = datetime.now()
    db.session.commit()
    return redirect(url_for('admin_join_request.index'))


# 가입 승인 처리
@bp.route('/allow/<int:request_id>', methods=['GET'])
@login_required_admin
def allow_request(request_id):
    join_request = Join_request.query.get_or_404(request_id)

    user_id = request.form.get('user_id', type=str)
    user = User.query.get_or_404(user_id)
    user.userid = join_request.userid
    user.password = join_request.password

    join_request.state = 'ALLOWED'
    join_request.proc_date = datetime.now()
    db.session.commit()
    return redirect(url_for('admin_join_request.index'))
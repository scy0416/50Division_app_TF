from flask import Blueprint, render_template, request, make_response, jsonify
from sqlalchemy import union, distinct, and_
from datetime import datetime

from public_service_employee_application.views.auth_views import login_required_admin
from public_service_employee_application.models import User, Punch_in_out
from public_service_employee_application import db

# 블루프린트 객체 생성
bp = Blueprint('admin_punch_in_out', __name__, url_prefix='/admin/punch_in_out')

# 이 블루프린트의 최초 진입점
@bp.route('/', methods=['GET'])
@login_required_admin
def index():
    return render_template('admin/punch_in_out/punch_in_out_calendar.html')

# 선택한 날짜에 대한 목록을 가져오는 엔드포인트
@bp.route('/<date>', methods=['GET'])
@login_required_admin
def punch_in_out_detail(date):
    # 검색 및 페이징 처리
    q = request.args.get('q', type=str, default='')
    page = request.args.get('page', type=int, default=1)

    if date is None:
        response = "문제가 발생했습니다."
    else:
        waiting_pio = db.session.query(
            Punch_in_out.id.label('pio_id'),
            User.id.label('user_id'),
            Punch_in_out,
            User
        ).outerjoin(User, Punch_in_out.user_id == User.id).filter(
            Punch_in_out.state == 'WAITING',
            Punch_in_out.date == date,
            User.name.like('%' + q + '%')
        ).subquery()
        processed_pio = db.session.query(
            Punch_in_out.id.label('pio_id'),
            User.id.label('user_id'),
            Punch_in_out,
            User
        ).outerjoin(User, Punch_in_out.user_id == User.id).filter(
            Punch_in_out.state == 'PROCESSED',
            Punch_in_out.date == date,
            User.name.like('%' + q + '%')
        ).subquery()
        pio = union(waiting_pio.select(), processed_pio.select()).subquery()
        pio = db.session.query(pio)
        pio_list = pio.paginate(page=page, per_page=10)
        response = render_template(
            'admin/punch_in_out/punch_in_out_detail.html',
            q=q, page=page, pio_list=pio_list, date=date
        )
    return response

# 출석 처리 엔드포인트
@bp.route('/proc/accept/<pio_id>', methods=['POST'])
@login_required_admin
def proc_pio(pio_id):
    pio = Punch_in_out.query.get_or_404(pio_id)
    pio.state = 'PROCESSED'
    pio.proc_date = datetime.now()
    db.session.commit()
    return make_response("", 204)

# 비고를 저장하는 엔드포인트
@bp.route('/proc/edit/<pio_id>', methods=['POST'])
@login_required_admin
def edit_pio(pio_id):
    data = request.form
    bigo = data.get('bigo')
    pio = Punch_in_out.query.get_or_404(pio_id)
    pio.bigo = bigo
    db.session.commit()
    return make_response("", 204)

# 전달받은 날짜 사이에 있는 처리되지 않은 출근 정보를 반환하는 엔드포인트
@bp.route('/proc/yet', methods=['GET'])
@login_required_admin
def get_unprocessed():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    pio_list = db.session.query(distinct(Punch_in_out.date)).filter(
        and_(
            Punch_in_out.date.between(start_date, end_date),
            Punch_in_out.state == 'WAITING'
        )
    ).all()

    response = []
    for pio in pio_list:
        response.append(pio[0].strftime('%Y-%m-%d'))

    return jsonify(response)
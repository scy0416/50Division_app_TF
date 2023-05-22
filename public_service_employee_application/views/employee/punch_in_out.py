from flask import Blueprint, render_template, g, request, jsonify
from sqlalchemy import and_, or_, not_
from datetime import datetime
import json

from public_service_employee_application.views.auth_views import login_required_employee
from public_service_employee_application.models import User, Punch_in_out
from public_service_employee_application import db

# 블루프린트 객체 생성
bp = Blueprint('employee_punch_in_out', __name__, url_prefix='/employee/punch_in_out')


# 이 블루프린트의 최초 진입점
@bp.route('/', methods=['GET'])
@login_required_employee
def index():
    return render_template('employee/punch_in_out/punch_in_out_calendar.html')

# 선택한 날짜에 대한 처리를 위한 엔드포인트
@bp.route('/<date>', methods=['GET'])
@login_required_employee
def punch_in_out_detail(date):
    if date is None:
        response = "<div>문제가 발생했습니다.</div>"
    else:
        pio = Punch_in_out.query.filter_by(date=date, user_id=g.user.id).first()
        response = render_template('employee/punch_in_out/punch_in_out_detail.html', pio=pio, date=date)
    return response


# 출근부 데이터 생성
@bp.route('/create', methods=['POST'])
@login_required_employee
def punch_in_out_create():
    data = request.get_json()
    date = data.get('date')
    punch_in = data.get('punch_in')
    punch_out = data.get('punch_out')

    # 이 부분에서 데이터가 전부 들어있는지 재확인
    if punch_in == '' and punch_out == '':
        response = {
            'isEmpty': True
        }
        return jsonify(response)

    punch_in_out_data = Punch_in_out(
        user_id=g.user.id,
        date=date,
        punch_in=punch_in if punch_in != '' else None,
        pi_create_time=datetime.now() if punch_in != '' else None,
        punch_out=punch_out if punch_out != '' else None,
        po_create_time=datetime.now() if punch_out != '' else None,
        state='WAITING'
    )
    db.session.add(punch_in_out_data)
    db.session.commit()

    response = {
        'isEmpty': False,
        'html': punch_in_out_detail(date=date)
    }
    return jsonify(response)


# 출근부 데이터 편집
@bp.route('/edit/<int:id>', methods=['POST'])
@login_required_employee
def punch_in_out_edit(id):
    punch_in_out_data = Punch_in_out.query.get_or_404(id)
    punch_in = request.form.get('punch_in')
    punch_out = request.form.get('punch_out')

    punch_in_out_data.punch_in = \
        punch_in if punch_in != '' else punch_in_out_data.punch_in
    punch_in_out_data.pi_modify_time = \
        datetime.now() if punch_in != '' else punch_in_out_data.pi_modify_time

    punch_in_out_data.punch_out = \
        punch_out if punch_out != '' else punch_in_out_data.punch_out
    punch_in_out_data.po_modify_time = \
        datetime.now() if punch_out != '' else punch_in_out_data.po_modify_time

    db.session.commit()

    return punch_in_out_detail(date=punch_in_out_data.date)


# 전달받은 날짜 사이에 있는 완전히 입력되지 않은 출근 정보를 반환하는 엔드보인트
@bp.route('/proc/yet', methods=['GET'])
@login_required_employee
def get_unprocessed():
    from_date = request.args.get('from_date')
    to_date = request.args.get('to_date')
    all_dates = json.loads(request.args.get('all_dates'))

    pio_list = Punch_in_out.query.filter(
        and_(
            Punch_in_out.user_id == g.user.id,
            and_(
                not_(Punch_in_out.punch_in.is_(None)),
                not_(Punch_in_out.punch_out.is_(None))
            ),
            Punch_in_out.date.between(from_date, to_date)
        )
    ).all()

    pio_list = [str(pio.date) for pio in pio_list]

    response = [date for date in all_dates if date not in pio_list]
    #print(response)

    return jsonify(response)
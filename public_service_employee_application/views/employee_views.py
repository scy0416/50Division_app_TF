import os
from flask import Blueprint, render_template, request, session, redirect, url_for, g, send_from_directory, jsonify
from sqlalchemy import and_
from datetime import datetime
from werkzeug.utils import secure_filename

from public_service_employee_application.views.auth_views import login_required_employee

from sqlalchemy import and_, cast, String
from public_service_employee_application import db
from public_service_employee_application.models import Post, User, Comment, HR_change_request, Vacation_request, Quarter, Wellfare_point, Medical_checkup_request, Punch_in_out
from public_service_employee_application.forms import writeForm, contentForm

# 블루프린트 객체 생성
bp = Blueprint('employee', __name__, url_prefix='/employee')


# 이 블루프린트의 최초 진입점
@bp.route('/', methods=('GET',))
# 직원으로 로그인이 되었나 확인하는 부분
@login_required_employee
def index():
    return render_template('employee/employee_main.html')


# 복지 포인트 조회
@bp.route('/welfare/', methods=('GET', ))
@login_required_employee
def welfare():
    quarter_id = request.args.get('quarter_id', type=int, default=-1)
    quarter = None

    quarter_list = Quarter.query.all()

    if quarter_id == -1:
        quarter = Quarter.query.order_by(Quarter.quarter.desc()).first()
        quarter_id = quarter.id
    else:
        quarter = Quarter.query.get_or_404(quarter_id)

    welfare_point = Wellfare_point.query.filter_by(user_id=g.user.id, quarter_id=quarter_id).first()

    return render_template('employee/welfare_point.html', quarter_list=quarter_list, quarter=quarter, welfare=welfare_point)
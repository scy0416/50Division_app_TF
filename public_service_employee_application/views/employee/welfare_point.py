from flask import Blueprint, request, g, render_template
import os
import pandas as pd

from public_service_employee_application.views.auth_views import login_required_employee
from public_service_employee_application.models import User, Quarter
from public_service_employee_application import db

# 블루프린트 객체 생성
bp = Blueprint('employee_welfare_point', __name__, url_prefix='/employee/welfare_point')


# 이 블루프린트의 최초 진입점
@bp.route('/', methods=['GET'])
@login_required_employee
def index():
    quarter_id = request.args.get('quarter_id', type=int, default=None)

    quarter = None
    if quarter_id is None:
        quarter = Quarter.query.first()
    else:
        quarter = Quarter.query.get_or_404(quarter_id)
    quarter_list = Quarter.query.all()

    filename = quarter.quarter + '.xlsx'
    filepath = os.path.join('static', 'welfare_point', filename)

    welfare_point = pd.read_excel(filepath, sheet_name='data', header=None, index_col=None)
    welfare_point = welfare_point[[2, 4, 6]]
    welfare_point.columns = ['name', 'birth', 'point']
    birth = str(g.user.birth_date).replace('-', '')
    welfare_point = welfare_point.query('name==@g.user.name|birth==@birth')

    return render_template('/employee/welfare_point/welfare_point.html',
                           quarter=quarter, quarter_list=quarter_list,
                           welfare_point=welfare_point)
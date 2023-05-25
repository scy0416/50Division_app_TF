from flask import Blueprint, request, render_template, redirect, url_for, flash
import os
import pandas as pd

from public_service_employee_application.views.auth_views import login_required_admin
from public_service_employee_application.models import User, Quarter
from public_service_employee_application import db

# 블루프린트 객체 생성
bp = Blueprint('admin_welfare_point', __name__, url_prefix='/admin/welfare_point')


# 이 블루프린트의 최초 진입점
@bp.route('/', methods=['GET'])
@login_required_admin
def index():
    quarter_id = request.args.get('quarter_id', type=int, default=None)

    quarter = None
    if quarter_id is None:
        quarter = Quarter.query.first()
    else:
        quarter = Quarter.query.get_or_404(quarter_id)
    quarter_list = Quarter.query.all()

    return render_template('/admin/welfare_point/welfare_point.html',
                    quarter_list=quarter_list, quarter=quarter)


# 유저 목록
@bp.route('/user', methods=['GET'])
@login_required_admin
def get_user_list():
    q = request.args.get('q', type=str, default='')
    page = request.args.get('page', type=int, default=1)
    quarter_id = request.args.get('quarter_id', type=int)

    user_list = User.query.filter(
        User.role == 'USER'
    ).filter(
        User.name.contains(q)
    ).paginate(page=page, per_page=10)

    file_name = Quarter.query.get_or_404(quarter_id).quarter + '.xlsx'
    file_path = os.path.join('static', 'welfare_point', file_name)
    welfare_point_data =pd.read_excel(file_path, sheet_name='data', header=None, index_col=None)
    welfare_point_data = welfare_point_data[[2, 4, 6]]
    welfare_point_data.columns = ['name', 'birth', 'point']

    return render_template('/admin/welfare_point/user_list.html',
                           user_list=user_list,
                           welfare_point_data=welfare_point_data,
                           q=q, page=page)


# 분기 관리 페이지
@bp.route('/quarter/manage', methods=['GET'])
@login_required_admin
def manage_quarter():
    quarter_list = Quarter.query.all()
    return render_template('/admin/welfare_point/quarter_manage.html',
                           quarter_list=quarter_list)


# 분기 등록
@bp.route('/quarter/add', methods=['POST'])
@login_required_admin
def add_quarter():
    quarter_name = request.form.get('quarter_name')

    check = Quarter.query.filter(
        Quarter.quarter == quarter_name
    ).all()
    if len(check) > 0:
        flash('이름이 같은 분기가 존재합니다')
        return redirect(url_for('admin_welfare_point.manage_quarter'))

    if 'quarter_file' not in request.files:
        return '파일이 없습니다', 400
    file = request.files['quarter_file']
    if file.filename == '':
        return '파일이 없습니다', 400
    if file:
        file_name = quarter_name + '.xlsx'
        file_path = os.path.join('static', 'welfare_point', file_name)
        file.save(file_path)

    quarter = Quarter(
        quarter=quarter_name
    )
    db.session.add(quarter)
    db.session.commit()

    return redirect(url_for('admin_welfare_point.manage_quarter'))


# 분기 삭제
@bp.route('/quarter/<quarter_id>/delete', methods=['POST'])
@login_required_admin
def delete_quarter(quarter_id):
    quarter = Quarter.query.get_or_404(quarter_id)
    db.session.delete(quarter)
    db.session.commit()

    file_path = os.path.join('static', 'welfare_point', quarter.quarter + '.xlsx')
    os.remove(file_path)

    return redirect(url_for('admin_welfare_point.manage_quarter'))


# 분기 편집
@bp.route('/quarter/<quarter_id>/edit', methods=['POST'])
@login_required_admin
def edit_quarter(quarter_id):
    quarter = Quarter.query.get_or_404(quarter_id)
    new_name = request.form.get('name')
    origin = quarter.quarter

    check = Quarter.query.filter(
        Quarter.quarter == origin
    ).all()
    print(len(check))
    if len(check) >= 1:
        flash('이름이 같은 분기가 존재합니다')
        return redirect(url_for('admin_welfare_point.manage_quarter'))

    file_name = origin + '.xlsx'
    file_path = os.path.join('static', 'welfare_point', file_name)
    new_file_name = new_name + '.xlsx'
    new_file_path = os.path.join('static', 'welfare_point', new_file_name)
    os.rename(file_path, new_file_path)

    quarter.quarter = new_name
    db.session.commit()

    return redirect(url_for('admin_welfare_point.manage_quarter'))
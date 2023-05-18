from flask import Blueprint, request, render_template, redirect, url_for, flash

from public_service_employee_application.views.auth_views import login_required_admin
from public_service_employee_application import db
from public_service_employee_application.models import User

# 블루프린트 객체 생성
bp = Blueprint('admin_personal_record', __name__, url_prefix='/admin/pr')


# 이 블루프린트의 최초 진입점
@bp.route('/', methods=['GET'])
@login_required_admin
def index():
    page = request.args.get('page', type=int, default=1)
    q = request.args.get('q', type=str, default='')

    user_list = User.query.filter(User.role == 'USER')
    user_list = user_list.filter(User.name.ilike('%'+q+'%'))

    user_list = user_list.paginate(page=page, per_page=10)

    return render_template('admin/personal_record/personal_record_list.html',
                           user_list=user_list, q=q, page=page)


# 관리자를 추가
@bp.route('/create/admin/', methods=['POST'])
@login_required_admin
def create_admin():
    position = request.form.get('position', type=str)
    rank = request.form.get('rank', type=str)
    name = request.form.get('name', type=str)
    id = request.form.get('id', type=str)
    password = request.form.get('password', type=str)

    check = User.query.filter(User.userid == id).first()
    if check:
        flash("관리자가 이미 존재합니다.")
        return redirect(url_for('admin_personal_record.index'))

    admin = User(
        userid=id,
        name=position+'/'+rank+'/'+name,
        password=password,
        role='ADMIN'
    )
    db.session.add(admin)
    db.session.commit()

    return redirect(url_for('admin_personal_record.index'))


# 공무직원 생성
@bp.route('/create/employee', methods=['POST'])
@login_required_admin
def create_employee():
    name = request.form.get('name', type=str)
    unit_name = request.form.get('unit_name', type=str)
    position = request.form.get('position', type=str)
    birth_date = request.form.get('birth_date', type=str)
    hire_date = request.form.get('hire_date', type=str)
    retirement_date = request.form.get('retirement_date', type=str)
    id = request.form.get('id', type=str)
    password = request.form.get('password', type=str, default='')
    bigo = request.form.get('bigo', type=str, default='')

    check = User.query.filter(User.userid == id).first()
    if check:
        flash("동일한 아이디의 사용자가 있습니다.")
        return redirect(url_for('admin_personal_record.index'))

    employee = User(
        userid=id,
        name=name,
        password=None if password == '' else password,
        unit_name=unit_name,
        position=position,
        birth_date=birth_date,
        hire_date=hire_date,
        retirement_date=retirement_date,
        employment_type='PUBLIC_SERVICE',
        bigo=bigo
    )
    db.session.add(employee)
    db.session.commit()

    return redirect(url_for('admin_personal_record.index'))


# 관리자 목록 확인창
@bp.route('/admin', methods=['GET'])
@login_required_admin
def admin_list():
    admin_list = User.query.filter(User.role == 'ADMIN')
    admin_list = admin_list.paginate(page=1, per_page=100)
    return render_template('admin/personal_record/admin_list.html', admin_list=admin_list)


# 관리자 삭제
@bp.route('/admin/<int:id>/delete', methods=['POST'])
@login_required_admin
def delete_admin(id):
    admin = User.query.get_or_404(id)
    db.session.delete(admin)
    db.session.commit()
    return redirect(url_for('admin_personal_record.admin_list'))


# 공무직원 상세창
@bp.route('/<int:id>/detail', methods=['GET'])
@login_required_admin
def employee_detail(id):
    employee = User.query.get_or_404(id)
    return render_template('admin/personal_record/personal_record_detail.html', user=employee)


# 공무직원 정보 변경
@bp.route('/<int:id>/edit', methods=['POST'])
@login_required_admin
def edit_employee(id):
    employee = User.query.get_or_404(id)

    name = request.form.get('name', type=str)
    birth_date = request.form.get('birth_date', type=str)
    phone_num = request.form.get('phone_num', type=str)
    address = request.form.get('address', type=str)
    unit_name = request.form.get('unit_name', type=str)
    position = request.form.get('position', type=str)
    hire_date = request.form.get('hire_date', type=str)
    retirement_date = request.form.get('retirement_date', type=str)
    employment_type = request.form.get('employment_type', type=str)
    bigo = request.form.get('bigo', type=str)

    employee.name = name
    employee.birth_date = birth_date
    employee.phone_num = phone_num
    employee.address = address
    employee.unit_name = unit_name
    employee.position = position
    employee.hire_date = hire_date
    employee.retirement_date = retirement_date
    employee.employment_type = employment_type
    employee.bigo = bigo

    db.session.commit()

    return redirect(url_for('admin_personal_record.employee_detail', id=id))


# 공무직원 삭제
@bp.route('/<int:id>/delete', methods=['POST'])
@login_required_admin
def delete_employee(id):
    employee = User.query.get_or_404(id)
    db.session.delete(employee)
    db.session.commit()

    return redirect(url_for('admin_personal_record.index'))
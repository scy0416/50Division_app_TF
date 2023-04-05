from flask import Blueprint, render_template, request, url_for, flash, g
from werkzeug.utils import redirect
from datetime import date

from public_service_employee_application import db
from public_service_employee_application.views.auth_views import login_required_admin
from public_service_employee_application.models import User
from public_service_employee_application.forms import AddAdmin, AddEmployee, UserDetail, searchUser

# 블루프린트 객체 생성
bp = Blueprint('admin', __name__, url_prefix='/admin')

# 이 블루프린트의 최초 진입점
@bp.route('/', methods=('GET', ))
# 관리자로 로그인이 되었나 확인하는 부분
@login_required_admin
def index():
    #return render_template('base.html')
    return render_template('user/admin_main.html')

# 인사정보 관리창
@bp.route('/pr/', methods=('GET', 'POST'))
@login_required_admin
def pr_information():

    # 어드민 추가할 때 사용할 폼 추가
    adminForm = AddAdmin()
    # 공무직원 추가할 때 사용할 폼 추가
    employeeForm = AddEmployee()
    # 검색할 때 사용할 폼 추가
    searchForm = searchUser()

    # post메소드로 요청이 왔다면
    if request.method == 'POST':
        # form들의 form_id를 읽어와서 어떤 폼이 post요청을 했는지 확인
        form_id = request.form.get('form_id')
        if form_id == 'addAdmin':
            g.addAdmin_error = True
        elif form_id == 'addEmployee':
            g.addEmployee_error = True

    # post메소드로 요청이 왔고, 어드민 추가 요청이 처리되는 경우
    # sce를 사용해서 한쪽 폼이 작동할 때 동작하지 않게 처리함
    if request.method == 'POST' and request.form.get('form_id') == 'addAdmin' and adminForm.validate_on_submit():
        # 유저 테이블 중에서 입력한 id와 같고 어드민인 사용자를 가져온다
        user = User.query.filter_by(role='ADMIN', userid=adminForm.id.data).first()
        # 해당하는 유저가 존재하지 않는 경우
        if not user:
            # 입력 정보 토대로 유저 객체 생성
            user = User(
                userid=adminForm.id.data,
                name='관리자',
                password=adminForm.password1.data,
                role='ADMIN'
            )
            # 유저 추가
            db.session.add(user)
            db.session.commit()
            # 정상적으로 처리되었기 때문에 g객체의 addAdmin_error을 거짓으로 초기화
            g.addAdmin_error = False
            g.addEmployee_error = False
            # 다시 인사정보 화면으로 리디렉션
            redirect(url_for('admin.pr_information'))
        else:
            # 유저가 이미 존재하는 경우
            flash('이미 존재하는 관리자입니다.')

    # post메소드로 요청이 왔고, 사용자 추가 요청이 처리되는 경우
    # sce를 사용해서 한쪽 폼이 작동할 때 동작하지 않게 처리함
    if request.method == 'POST' and request.form.get('form_id') == 'addEmployee' and employeeForm.validate_on_submit():
        user = User(
            name=employeeForm.user_name.data,
            unit_name=employeeForm.unit_name.data,
            position=employeeForm.user_position.data,
            birth_date=employeeForm.birth_date.data,
            hire_date=employeeForm.hire_date.data,
            retirement_date=employeeForm.retirement_date.data,
            employment_type=employeeForm.employment_type.data,
            vacation=0,
            medical_checkup='N',
            sexual_harassment_prevent='N',
            disability_awareness_improvement='N',
            workplace_harassment_prevent='N',
            bigo=employeeForm.bigo.data,
            role='USER'
        )
        # 유저 추가
        db.session.add(user)
        db.session.commit()
        # 정상적으로 처리되었기 때문에 g객체의 addEmployee_error을 거짓으로 초기화
        g.addEmployee_error = False
        g.addAdmin_error = False
        # 다시 인사정보 화면으로 리디렉션
        redirect(url_for('admin.pr_information'))

    # 검색 및 페이징 처리
    # 입력 파라미터
    page = request.args.get('page', type=int, default=1) # 페이지
    name = request.args.get('Name', type=str, default=None) # 이름
    searchForm.name.data = name
    unit_name = request.args.get('UnitName', type=str, default=None) # 부대명
    searchForm.unit_name.data = unit_name
    position = request.args.get('Position', type=str, default=None) # 직책
    searchForm.position.data = position
    birth_date = request.args.get('BirthDate', type=str, default=None) # 생년월일
    searchForm.birth_date.data = birth_date

    # 검색 처리 과정
    user_list = User.query.filter_by(role='USER')
    if name != None and name != '': # 값이 존재하는 경우에 실행하는 조건
        user_list = user_list.filter(User.name.ilike('%'+name+'%'))
    if unit_name != None and unit_name != '':
        user_list = user_list.filter(User.unit_name.ilike('%'+unit_name+'%'))
    if position != None and position != '':
        user_list = user_list.filter(User.position.ilike('%'+position+'%'))
    if birth_date != None and birth_date != '':
        user_list = user_list.filter_by(birth_date=birth_date)
    # 페이징 처리
    user_list = user_list.paginate(page=page, per_page=10)

    return render_template('user/user_list.html', user_list=user_list, adminForm=adminForm, employeeForm=employeeForm, searchForm=searchForm)

# 유저의 상세한 정보를 볼 때 사용하는 라우트
@bp.route('/pr/detail/<int:user_id>', methods=('GET', 'DELETE', 'POST'))
@login_required_admin
def detail(user_id):
    form = UserDetail()
    user = User.query.get_or_404(user_id)

    if request.method == "DELETE" and g.user.role != 'ADMIN':
        flash('삭제 권한이 없습니다.')
        return redirect(url_for('admin.detail', user_id=user.id))
    elif request.method == "DELETE" and g.user.role == 'ADMIN':
        user = User.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()
        return redirect(url_for('admin.pr_information'))

    if request.method == 'POST':
        g.modifyError = True
    if request.method == 'POST' and form.validate_on_submit():
        user.name = form.name.data
        user.birth_date = form.birth_date.data
        user.phone_num = form.phone_num.data
        user.address = form.address.data
        user.unit_name = form.unit_name.data
        user.position = form.position.data
        user.hire_date = form.hire_date.data
        user.retirement_date = form.retirement_date.data
        user.employment_type = form.employment_type.data
        user.bigo = form.bigo.data
        db.session.commit()
        g.modifyError = False

    return render_template('user/user_detail_for_admin.html', user=user, form=form)

# 의무 교육 관리창
@bp.route('/edu/', methods=('GET', 'PATCH'))
@login_required_admin
def edu():
    # 상세검색을 위한 폼
    searchForm = searchUser()

    # 검색 및 페이징 처리
    # 입력 파라미터
    page = request.args.get('page', type=int, default=1)  # 페이지
    name = request.args.get('name', type=str, default=None)  # 이름
    searchForm.name.data = name
    unit_name = request.args.get('unitName', type=str, default=None)  # 부대명
    searchForm.unit_name.data = unit_name
    position = request.args.get('position', type=str, default=None)  # 직책
    searchForm.position.data = position
    birth_date = request.args.get('birthDate', type=str, default=None)  # 생년월일
    searchForm.birth_date.data = birth_date

    # 검색 처리 과정
    user_list = User.query.filter_by(role='USER')
    if name != None and name != '':  # 값이 존재하는 경우에 실행하는 조건
        user_list = user_list.filter(User.name.ilike('%'+name+'%'))
    if unit_name != None and unit_name != '':
        user_list = user_list.filter(User.unit_name.ilike('%'+unit_name+'%'))
    if position != None and position != '':
        user_list = user_list.filter(User.position.ilike('%'+position+'%'))
    if birth_date != None and birth_date != '':
        user_list = user_list.filter_by(birth_date=birth_date)
    # 페이징 처리
    user_list = user_list.paginate(page=page, per_page=10)

    return render_template('user/edu_list.html', user_list=user_list, form=searchForm)
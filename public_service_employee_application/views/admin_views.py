from flask import Blueprint, render_template, request, url_for, flash, g
from werkzeug.utils import redirect

from public_service_employee_application import db
from public_service_employee_application.views.auth_views import login_required_admin
from public_service_employee_application.models import User
from public_service_employee_application.forms import AddAdmin, AddEmployee

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
            name=employeeForm.name.data,
            unit_name=employeeForm.unit_name.data,
            position=employeeForm.position.data,
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

    # 페이진 처리
    page = request.args.get('page', type=int, default=1) # 페이지
    user_list = User.query.filter_by(role='USER')
    user_list = user_list.paginate(page=page, per_page=10)

    return render_template('user/user_list.html', user_list=user_list, adminForm=adminForm, employeeForm=employeeForm)
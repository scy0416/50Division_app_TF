from flask import Blueprint, render_template, request, url_for, flash, g, jsonify, session, make_response, Response, send_from_directory, jsonify
from sqlalchemy import desc
from sqlalchemy.orm import joinedload
from werkzeug.utils import redirect
from datetime import date
from sqlalchemy import and_, union, alias
from sqlalchemy.orm import aliased
from datetime import datetime

from public_service_employee_application import db, csrf
from public_service_employee_application.views.auth_views import login_required_admin
from public_service_employee_application.models import User, Post, User, Comment, HR_change_request, Join_request, Vacation_request, Quarter, Wellfare_point, Medical_checkup_request, Punch_in_out
from public_service_employee_application.forms import AddAdmin, AddEmployee, UserDetail, searchUser, writeForm, contentForm


# 블루프린트 객체 생성
bp = Blueprint('admin', __name__, url_prefix='/admin')

# 이 블루프린트의 최초 진입점
@bp.route('/', methods=('GET', ))
# 관리자로 로그인이 되었나 확인하는 부분
@login_required_admin
def index():
    hr_change_request = HR_change_request.query.filter_by(state='WAITING').all()
    join_request = Join_request.query.filter_by(state='WAITING').all()
    vacation_request = Vacation_request.query.filter_by(state='WAITING').all()
    return render_template('admin/admin_main.html', hr_change_request=hr_change_request, join_request=join_request, vacation_request=vacation_request)

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
            return redirect(url_for('admin.pr_information'))
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
        return redirect(url_for('admin.pr_information'))

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

    response = make_response(render_template('admin/user_list.html', user_list=user_list, adminForm=adminForm, employeeForm=employeeForm, searchForm=searchForm))
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'

    return response

# 유저의 상세한 정보를 볼 때 사용하는 라우트
@bp.route('/pr/detail/<int:user_id>', methods=('GET', 'DELETE', 'POST'))
@login_required_admin
def detail(user_id):
    form = UserDetail()
    user = User.query.get_or_404(user_id)

    if request.method == "DELETE" and g.user.role != 'ADMIN':
        flash('삭제 권한이 없습니다.')
        return redirect(url_for('admin.pr_information', user_id=user.id))
    elif request.method == "DELETE" and g.user.role == 'ADMIN':
        #employee = User.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()
        #return redirect(url_for('admin.detail', user_id=employee.id))
        return jsonify({'status': 'success'})

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

    return render_template('admin/user_detail_for_admin.html', user=user, form=form)

# 의무 교육 관리창
@bp.route('/edu/', methods=('GET', 'PATCH'))
@login_required_admin
def edu():
    # 상세검색을 위한 폼
    searchForm = searchUser()

    # patch메소드로 호출되었을 경우
    if request.method == 'PATCH':
        # 전달된 데이터를 추출하는 과정
        data = request.get_json()
        # 유저의 식별용 id추출
        user_id = data.get('id')
        # 요청의 타입을 추출
        request_type = data.get('type')
        # 바뀔 값을 추출
        value = data.get('value')
        
        # 값을 바꿀 유저를 추출
        user = User.query.get_or_404(user_id)
        # 성희롱 예방 교육 인 경우
        if request_type == 'sexual_harassment_prevent':
            user.sexual_harassment_prevent = value
        # 장애 인식 개선 교육인 경우
        elif request_type == 'disability_awareness_improvement':
            user.disability_awareness_improvement = value
        # 직장 내 괴롭힘 예방 교육인 경우
        elif request_type == 'workplace_harassment_prevent':
            user.workplace_harassment_prevent = value
        
        # 바꾼 결과를 저장
        db.session.commit()
        
        # 결과를 반환
        return jsonify({'status':'success'}), 200

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
    user_list = user_list.paginate(page=page, per_page=5)

    return render_template('admin/edu_list.html', user_list=user_list, form=searchForm)

# 공지사항 관리창
@bp.route('/notice/', methods=('GET', 'POST'))
@login_required_admin
def notice():
    # 입력 폼 생성
    form = writeForm()

    if request.method == 'POST':
        g.form_error = True
    # 공지사항 등록
    if request.method == 'POST' and form.validate_on_submit():
        notice = Post(
            user_id=session.get('user_id'),
            subject=form.subject.data,
            content=form.content.data,
            create_date=datetime.now()
        )
        db.session.add(notice)
        db.session.commit()
        g.form_error = False
        form.subject.data = None
        form.content.data = None
        return redirect(url_for('admin.notice'))

    # 검색 및 페이징 처리
    q = request.args.get('q', type=str, default='')
    page = request.args.get('page', type=int, default=1)

    # 검색 처리 과정
    # 실질적인 검색
    notice_list = db.session.query(Post).join(User).filter(and_(User.role == 'ADMIN', Post.subject.contains(q))).order_by(Post.create_date.desc())
    notice_list = notice_list.paginate(page=page, per_page=10)

    # 템플릿 출력
    return render_template('admin/notice_list.html', notice_list=notice_list, q=q, page=page, form=form)

# 공지사항 상세창
@bp.route('/notice/<int:post_id>', methods=('GET', 'PATCH', 'DELETE', 'POST'))
@login_required_admin
def notice_detail(post_id):
    # 폼 생성
    form = writeForm()
    cForm = contentForm()

    # delete로 요청이 전달된 경우
    if request.method == 'DELETE':
        notice = Post.query.get_or_404(post_id)
        if notice.user_id != session.get('user_id'):
            return jsonify({"error": f"An error occurred while deleting the resource"}), 500
        else:
            db.session.delete(notice)
            db.session.commit()
            return jsonify({"result": f"Resource has been deleted."}), 200


    # patch로 요청이 전달된 경우
    if request.method == 'PATCH':
        # 데이터 추출
        data = request.get_json()
        # 바꿀 제목 추출
        subject = data.get('subject')
        # 바꿀 내용 추출
        content = data.get('content')
        # 바꿔질 글 추출
        post = Post.query.get_or_404(post_id)
        # 값 편집
        post.subject = subject
        post.content = content
        # 데이터베이스에 적용
        db.session.commit()

        # 결과를 반환
        return jsonify({'status': 'success'})

    # post로 요청이 온 경우
    if request.method == 'POST':
        if form.validate_on_submit():
            comment = Comment(
                user_id=session.get('user_id'),
                post_id=post_id,
                content=form.content.data,
                create_date=datetime.now()
            )
            db.session.add(comment)
            db.session.commit()
            return redirect(url_for('admin.notice_detail', post_id=post_id))

    # 확인하려는 공지사항 확인
    post = Post.query.get_or_404(post_id)
    # 템플릿 출력
    return render_template('admin/notice_detail.html', post=post, form=form, cForm=cForm)

# 댓글에 대한 엔드포인트(편집, 삭제)
@bp.route('/comment/', defaults={'comment_id':None}, methods=('POST', ))
@bp.route('/comment/<int:comment_id>', methods=('POST', ))
@login_required_admin
def comment(comment_id):
    if request.method == 'POST' and request.form.get('form_id') == 'post':
        c = Comment(
            user_id=session.get('user_id'),
            post_id=request.form.get('post_id'),
            content=request.form.get('content'),
            create_date=datetime.now()
        )
        db.session.add(c)
        db.session.commit()
        return redirect(url_for('admin.grievance_detail', post_id=c.post_id))
    ccomment = Comment.query.get_or_404(comment_id)
    writer_role = ccomment.post.user.role
    if request.method == 'POST' and request.form.get('form_id') == 'modify':
        ccomment.content = request.form.get('content')
        ccomment.modify_date = datetime.now()
        db.session.commit()
        if writer_role == 'USER':
            return redirect(url_for('admin.grievance_detail', post_id=ccomment.post_id))
        return redirect(url_for('admin.notice_detail', post_id=ccomment.post_id))
    if request.method == 'POST' and request.form.get('form_id') == 'delete':
        db.session.delete(ccomment)
        db.session.commit()
        #return redirect(url_for('admin.notice'))
        if writer_role == 'USER':
            return redirect(url_for('admin.grievance_detail', post_id=ccomment.post_id))
        return redirect(url_for('admin.notice_detail', post_id=ccomment.post_id))

@bp.route('/grievance/', methods=('GET', ))
@login_required_admin
def grievance_list():
    # 검색 및 페이진 처리
    q = request.args.get('q', type=str, default='')
    page = request.args.get('page', type=int, default=1)

    # 검색 처리 과정
    # 실직적인 검색
    grievance = db.session.query(Post).join(User).filter(and_(User.role == 'USER', Post.subject.contains(q))).order_by(Post.create_date.desc())
    grievance = grievance.paginate(page=page, per_page=10)

    # 템플릿 출력
    return render_template('admin/grievance_list.html', grievance_list=grievance, q=q, page=page)

# 고충 글 상세 창
@bp.route('/grievance/<int:post_id>', methods=('GET', ))
@login_required_admin
def grievance_detail(post_id):
    # 확인하려는 글
    post = Post.query.get_or_404(post_id)
    # 템플릿 출력
    return render_template('admin/grievance_detail.html', post=post)

@bp.route('/request/', methods=('GET', ))
@login_required_admin
def request_main():
    join_request = Join_request.query.filter_by(state='WAITING').all()
    hr_change_request = HR_change_request.query.filter_by(state='WAITING').all()
    vacation_request = Vacation_request.query.filter_by(state='WAITING').all()
    medical_checkup_request = Medical_checkup_request.query.filter_by(state='WAITING').all()
    return render_template('admin/request_main.html', join_request=join_request, hr_change_request=hr_change_request, vacation_request=vacation_request, medical_checkup_request=medical_checkup_request)

# 가입 신청 관리 부분
@bp.route('/request/join/', methods=('GET', ))
@login_required_admin
def join_list():
    # 검색 및 페이진 처리
    q = request.args.get('q', type=str, default='')
    page = request.args.get('page', type=int, default=1)

    # 검색 처리 과정
    # 실직적인 검색
    join = Join_request.query.filter(Join_request.name.contains(q))
    join = join.paginate(page=page, per_page=10)

    return render_template('admin/join_request_list.html', q=q, page=page, join_request_list=join)

# 가입 신청 상세 창 부분
@bp.route('/request/join/<int:request_id>', methods=('GET', 'POST'))
@ login_required_admin
def join_detail(request_id):
    # 처리할 가입 신청 데이터
    join_request = Join_request.query.get_or_404(request_id)

    # post로 요청이 온 경우
    if request.method == 'POST':
        # 등록을 하는 경우
        if request.form.get('form_id') == 'regist':
            user_id = request.form.get('user_id')
            user = User.query.get_or_404(user_id)
            user.userid = join_request.userid
            user.password = join_request.password

            join_request.state = 'ALLOWED'
            join_request.proc_date = datetime.now()
            db.session.commit()
            return redirect(url_for('admin.join_list'))
        # 거부하는 경우
        if request.form.get('form_id') == 'reject':
            join_request.state = 'REJECTED'
            join_request.proc_date = datetime.now()
            db.session.commit()
            return redirect(url_for('admin.join_list'))

    # 검색 처리
    name = request.args.get('name', type=str, default=join_request.name)
    birth_date = request.args.get('birth_date', type=str, default=join_request.birth_date)

    result_list = User.query.filter(User.name.contains(name))
    result_list = result_list.filter_by(birth_date=birth_date)
    result_list = result_list.filter(User.userid==None)
    result_list = result_list.filter(User.password==None).all()

    return render_template('admin/join_request_detail.html', join_request=join_request, result_list=result_list, name=name, birth_date=birth_date)

# 인사정보 리스트 출력 페이지
@bp.route('/request/hr_information/', methods=('GET', ))
@login_required_admin
def hr_information_list():
    # 검색 및 페이징 처리
    q = request.args.get('q', type=str, default='')
    page = request.args.get('page', type=int, default=1)

    # 인사정보 관련 신청 중에서 유저의 이름에 q가 포함되어 있는걸 필터링
    request_list = HR_change_request.query.join(User).filter(User.name.contains(q))
    request_list = request_list.paginate(page=page, per_page=5)

    return render_template('admin/hr_information_change_request_list.html', q=q, page=page, request_list=request_list)

# 인사정보 변경 상세 페이지
@bp.route('/request/hr_information/<int:request_id>', methods=('GET', 'POST'))
@login_required_admin
def hr_information_detail(request_id):
    hr_request = HR_change_request.query.get_or_404(request_id)

    # post로 요청이 들어온 경우
    if request.method == 'POST':
        # 승인/거부여부 확인
        state = request.form.get('form_id')
        # 승인된 경우라면
        if state == 'OK':
            # 신청 타입이 고용일 변경이라면
            if hr_request.type == 'HIRE':
                # 고용일 변경
                hr_request.user.hire_date = hr_request.change_to
            # 신청 타입이 퇴직일 변경이라면
            elif hr_request.type == 'RETIREMENT':
                # 퇴직일 변경
                hr_request.user.retirement_date = hr_request.change_to
            # 상태를 승인 상태로 변경한다.
            hr_request.state = 'ALLOWED'
        # 거부된 경우라면
        elif state == 'DENY':
            # 상태를 거부됨으로 변경한다.
            hr_request.state = 'REJECTED'
        # 처리 시간을 현재 시간을 대입한다.
        hr_request.proc_date = datetime.now()
        # 변경사항을 저장한다.
        db.session.commit()
        # 신청 리스트로 리다이렉션 시킨다.
        return redirect(url_for('admin.hr_information_list'))

    return render_template('admin/hr_information_change_request_detail.html', request=hr_request)

# 휴가 신청 리스트 출력 페이지
@bp.route('/request/vacation/', methods=('GET', ))
@login_required_admin
def vacation_list():
    # 검색 및 페이징 처리
    q = request.args.get('q', type=str, default='')
    page = request.args.get('page', type=int, default=1)

    # 휴가 관련 신청 중에서 유저의 이름에 q가 포함되어 있는걸 필터링
    request_list = Vacation_request.query.join(User).filter(User.name.contains(q))
    request_list = request_list.paginate(page=page, per_page=5)

    return render_template('admin/vacation_request_list.html', q=q, page=page, request_list=request_list)

# 휴가 신청 상세 페이지 출력
@bp.route('/request/vacation/<int:request_id>', methods=('GET', 'POST'))
@login_required_admin
def vacation_detail(request_id):
    # 신청 데이터 추출
    vacation_request = Vacation_request.query.get_or_404(request_id)

    # post로 요청이 온다면
    if request.method == 'POST':
        # 승인된 경우
        if request.form.get('form_id') == 'OK':
            # 상태를 승인됨으로 바꾼다.
            vacation_request.state = 'ALLOWED'
        # 거부된 경우
        elif request.form.get('form_id') == 'DENY':
            # 상태를 거부됨으로 바꾼다.
            vacation_request.state = 'REJECTED'
        # 휴가 신청의 처리된 날짜를 현재로 한다.
        vacation_request.proc_date = datetime.now()
        db.session.commit()
        # 휴가 신청 목록으로 리아디렉션 시킨다.
        return redirect(url_for('admin.vacation_list'))
    return render_template('admin/vacation_request_detail.html', request=vacation_request)

# 복지 포인트 관리 페이지
@bp.route('/welfare', methods=('GET', ))
@login_required_admin
def welfare():
    # 검색 중이던 결과로 들어갈 것인지에 대한 여부
    # 참이라면 검색 중이었던 것으로 세션에 저장된 정보대로 검색을 실시해야 한다.
    isSearching = request.args.get('isSearching', type=str, default='false')

    # 검색 중이어서 중간 결과로 들어가야 하는 경우
    if isSearching == 'true':
        q = session.pop('q', '')
        page = session.pop('page', 1)
        quarter_id = session.pop('quarter_id', Quarter.query.order_by(desc(Quarter.quarter)).first().quarter)
    # 중간으로 돌아가야 하는 것이 아닌 경우
    elif isSearching == 'false':
        q = request.args.get('q', type=str, default='')
        page = request.args.get('page', type=int, default=1)
        quarter_id = request.args.get('quarter_id', type=int, default=Quarter.query.order_by(desc(Quarter.quarter)).first().id)
    '''
    # 검색어, 페이지, 분기id를 불러옴
    q = request.args.get('q', type=str, default=session.pop('q', ''))
    page = request.args.get('page', type=int, default=session.pop('page', 1))
    quarter_id = request.args.get('quarter_id', type=int,
                                  default=session.pop('quarter_id', Quarter.query.order_by(desc(Quarter.quarter)).first().quarter))
    '''
    # 추출한 검색 데이터들을 세션에 저장
    session['q'] = q
    session['page'] = page
    session['quarter_id'] = quarter_id
    # 검색 처리
    quarter = Quarter.query.get_or_404(quarter_id)
    # 현재 복지 포인트에 대한 서브쿼리를 만든다.
    welfare_point = Wellfare_point.query.filter(Wellfare_point.quarter_id == quarter_id).subquery()
    # 공무직원이고, 이름에 검색어를 포함하는 경우에 대한 필터링을 서브쿼리로 만듦
    user_list = User.query.filter(User.role == 'USER', User.name.contains(q)).subquery()
    # 만들었던 서브쿼리끼리 아우터 조인을 실시한 결과를 서브쿼리화
    user_list = db.session.query(user_list, welfare_point, welfare_point.c.id.label('welfare_point_id')).join(
        welfare_point,
        user_list.c.id == welfare_point.c.user_id,
        isouter=True).subquery()
    # 서브쿼리로 만들었던 것 다시 아우터 조인
    user_list = db.session.query(user_list, Quarter).join(Quarter, user_list.c.quarter_id == Quarter.id, isouter=True)
    # 페이지네이션
    user_list = user_list.paginate(page=page, per_page=5)

    # 모든 분기 추출
    quarter_list = Quarter.query.all()

    return render_template('admin/welfare_point.html', quarter=quarter, quarter_list=quarter_list, user_list=user_list,
                           q=q, page=page, quarter_id=quarter_id)
    '''
    # 사용자 목록, 분기, 검색어, 페이지들을 None으로 초기화
    user_list = None
    quarter = None
    q = ''
    #q = session.pop('q', '')
    page = None
    #page = session.pop('page', None)
    # 분기id를 받아온다
    #quarter_id = session.pop('quarter_id', '')
    quarter_id = request.args.get('quarter_id', type=str, default='')
    # 분기id가 존재하는 경우
    if quarter_id != '':
        # 검색 및 페이징 처리
        q = request.args.get('q', type=str, default='')
        page = request.args.get('page', type=int, default=1)
        
        # 분기 데이터를 받아온다
        quarter = Quarter.query.get_or_404(quarter_id)
        # 현재 복지 포인트에 대한 서브쿼리를 만든다.
        welfare_point = Wellfare_point.query.filter(Wellfare_point.quarter_id == quarter_id).subquery()
        # 공무직원이고, 이름에 검색어를 포함하는 경우에 대한 필터링을 서브쿼리로 만듦
        user_list = User.query.filter(User.role == 'USER', User.name.contains(q)).subquery()
        # 만들었던 서브쿼리끼리 아우터 조인을 실시한 결과를 서브쿼리화
        user_list = db.session.query(user_list, welfare_point, welfare_point.c.id.label('welfare_point_id')).join(welfare_point,
                                                                     user_list.c.id == welfare_point.c.user_id,
                                                                     isouter=True).subquery()
        # 서브쿼리로 만들었던 것 다시 아우터 조인
        user_list = db.session.query(user_list, Quarter).join(Quarter, user_list.c.quarter_id == Quarter.id, isouter=True)
        # 페이지네이션
        user_list = user_list.paginate(page=page, per_page=10)
    
    # 모든 분기 추출
    quarter_list = Quarter.query.all()

    session['q'] = q
    session['page'] = page
    session['quarter_id'] = quarter_id
    #session['quarter'] = quarter

    if request.method == 'POST':
        #print("실행")
        #quarter = Quarter.query.get_or_404(session.get('quarter_id'))
        user_id = request.form.get('user_id')
        quarter_id = request.form.get('quarter_id')
        point = request.form.get('point')

        welfare_point = Wellfare_point(
            user_id=user_id,
            quarter_id=quarter_id,
            point=point
        )
        db.session.add(welfare_point)
        db.session.commit()
        #return render_template('admin/welfare_point.html', quarter=quarter,quarter_list=quarter_list, q=session.pop('q', ''),quarter_id=session.pop('quarter_id', ''), user_list=user_list)
        return Response(status=302)

    return render_template('admin/welfare_point.html', quarter=quarter, quarter_list=quarter_list, user_list=user_list, q=q, page=page, quarter_id=quarter_id)
    #return render_template('admin/welfare_point.html', quarter=session.pop('quarter', None), quarter_list=quarter_list, q=session.pop('q', ''), quarter_id=session.pop('quarter_id', ''), user_list=user_list)
    '''

# 복지 포인트 데이터를 생성하는 라우팅
@bp.route('/welfare/', methods=('POST', ))
@login_required_admin
def create_welfare():
    user_id = request.form.get('user_id')
    quarter_id = request.form.get('quarter_id')
    point = request.form.get('point')

    welfare_point = Wellfare_point(
        user_id=user_id,
        quarter_id=quarter_id,
        point=point
    )
    db.session.add(welfare_point)
    db.session.commit()

    #return Response(status=302)
    return redirect(url_for('admin.welfare', isSearching='true'))
    #return Response('', status=204)

# 복지 포인트 데이터를 편집하는 라우팅
@bp.route('/welfare/<int:welfare_point_id>', methods=('POST', ))
@login_required_admin
def edit_welfare(welfare_point_id):
    # 편집할 복지 포인트를 받아옴
    welfare_point = Wellfare_point.query.get_or_404(welfare_point_id)
    # 복지 포인트 편집
    welfare_point.point = request.form.get('point')
    db.session.commit()

    # 본문이 없는 결과를 반환(화면의 새로고침을 방지)
    return Response('', status=204)

# 복지 포인트용 분기를 생성하는 라우팅
@bp.route('/quarter', methods=('POST', ))
@login_required_admin
def make_quarter():
    # 분기 이름 추출 후 그 이름으로 분기 데이터 새엇ㅇ
    quarter = Quarter(
        quarter=request.form.get('quarter_name')
    )
    db.session.add(quarter)
    db.session.commit()
    return redirect(url_for('admin.welfare'))

# 복지 포인트용 분기를 편집하는 라우팅
@bp.route('/quarter/<int:quarter_id>/edit', methods=('POST', ))
@login_required_admin
def edit_quarter(quarter_id):
    # 편집할 분기를 가져옴
    quarter = Quarter.query.get_or_404(quarter_id)
    # 분기의 이름을 편집
    quarter.quarter = request.form.get('new_name')
    db.session.commit()
    return redirect(url_for('admin.welfare'))

# 복지 포인트용 분기를 삭제하는 라우팅
@bp.route('/quarter/<int:quarter_id>/delete', methods=('POST', ))
@login_required_admin
def delete_quarter(quarter_id):
    # 삭제할 분기를 가져옴
    quarter = Quarter.query.get_or_404(quarter_id)
    # 분기 삭제
    db.session.delete(quarter)
    db.session.commit()
    return redirect(url_for('admin.welfare'))
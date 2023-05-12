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
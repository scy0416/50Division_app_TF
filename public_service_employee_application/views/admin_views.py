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